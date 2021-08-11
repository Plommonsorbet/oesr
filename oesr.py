import json
from collections import defaultdict
import subprocess
import sys
import os
import shutil
import string
import secrets
import click
import tempfile
from xkcdpass import xkcd_password

CYAN = "\033[96m"
GREEN = "\033[92m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"

def error(msg):
    print(f"{FAIL}ERROR! {msg}{ENDC}", file=sys.stderr)
    sys.exit(1)


def pwgen():
    """generate secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for i in range(64))


def create_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    return path


def set_gnupg_dir(path):
    """Generate a temp directory and set it as gnupg home"""
    os.environ["GNUPGHOME"] = path


def gen_person_pseudonym():
    """Generate a random pseudonym using xkcdpass, example: uncombed-utopia"""
    wordfile = xkcd_password.locate_wordfile()
    mywords = xkcd_password.generate_wordlist(wordfile=wordfile)

    return xkcd_password.generate_xkcdpassword(mywords, numwords=2, delimiter="-")


def ssss_split(passphrase, threshold, num):
    """Convert passphrase to shares using shamir's secret sharing scheme"""
    p = subprocess.Popen(
        ["secret-share-split", "-t", str(threshold), "-n", str(num)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, err = p.communicate(input=passphrase.encode())

    if p.returncode != 0:
        error(f"ssss_split failed:{err.decode()}`")
    return output.decode().splitlines()


def ssss_combine(shares):
    """Convert passphrase to shares using shamir's secret sharing scheme"""
    p = subprocess.Popen(
        ["secret-share-combine"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Join the list of shares to be new line separated string instead
    output, err = p.communicate(input="\n".join(shares).encode())
    if p.returncode != 0:
        error(f"ssss_combine failed:{err.decode()}`")
    return output.decode()


def gen_pgp_key(pw_file, identity):
    """Generate pgp key"""
    subprocess.check_output(
        [
            "gpg",
            "--no-permission-warning",
            "--pinentry-mode",
            "loopback",
            "--batch",
            "--passphrase-file",
            pw_file,
            "--quick-generate-key",
            f"'{identity} <{identity}@oesr.local>'",
            "rsa4096",
            "sign,encrypt,auth",
            "never",
        ]
    )


def export_pgp(path, identity):
    """Export public key to file"""
    subprocess.check_output(
        [
            "gpg",
            "--no-permission-warning",
            "-o",
            path,
            "--export",
            "--armor",
            f"{identity}@oesr.local",
        ]
    ).decode()

    return path


def pgp_fingerprint(identity):
    """Get fingerprint for the identity"""
    # list the keys with the identity in machine readable output
    out = subprocess.check_output(
        [
            "gpg",
            "--no-permission-warning",
            "--list-keys",
            "--with-colons",
            f"{identity}@oesr.local",
        ]
    ).decode()

    for line in out.splitlines():
        # Find the fingerprint line
        if line.startswith("fpr"):
            # The 10th column always has the fingerprint
            fingerprint = line.split(":")[9]
            return fingerprint


def verify_pgp_passphrase(pw_file, identity):
    """Verify that the pgp key can be opened with the passphrase file"""

    # throws an exception if it the command is not successful
    subprocess.check_output(
        [
            "gpg",
            "--no-permission-warning",
            "--pinentry-mode",
            "loopback",
            "--batch",
            "--passphrase-file",
            pw_file,
            "--export-secret-keys",
            "-a",
            f"{identity}@oesr.local",
        ]
    )

    # The subprocess will return error if the command failed, so if it doesn't do that then it succeeeded
    return True


def lint_pgp(identity):
    """Run hopenpgp-tools on the gpg key to give linter output for best practices"""

    # Get the binary output of the public gpg certificate
    out = subprocess.check_output(
        ["gpg", "--no-permission-warning", "--export", f"{identity}@oesr.local"]
    )

    # Pipe the gpg certificate into hopenpgp-tools lint
    p = subprocess.Popen(
        ["hokey", "lint"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, err = p.communicate(input=out)

    if p.returncode != 0:
        error(f"pgp lint failed: {err.decode()}`")

    print(output.decode())


def init_oesr(output_dir, people, threshold, num):
    """Generate oesr peers"""
    oesr_config = {"people": defaultdict(dict), "threshold": threshold, "num": num}

    # Generate public output dir
    os.makedirs(f"{output_dir}/public", exist_ok=True)

    # Generate the keep dir
    os.makedirs(f"{output_dir}/keep", exist_ok=True)

    # Generate each persons output dir
    for person in people:
        os.makedirs(f"{output_dir}/{person}", exist_ok=True)
        os.makedirs(f"{output_dir}/{person}/shares", exist_ok=True)

    # Generate gnupg output dir
    os.makedirs(f"{output_dir}/gnupg", exist_ok=True)
    set_gnupg_dir(f"{output_dir}/gnupg")

    for person in people:
        # Generate a pseudonym for the person to use as pgp identity so the real name is not disclosed
        pgp_identity = gen_person_pseudonym()

        # Generate a password to use for pgp
        pw = pwgen()

        # Create password file for the persons gnupg key in $out_dir/$person/passphrase
        pw_file = create_file(f"{output_dir}/{person}/passphrase", pw)

        # Generate a list of shares from the password with shamir's secret sharing scheme
        shares = ssss_split(pw, threshold, num)

        # Generate pgp key in the keychain
        gen_pgp_key(pw_file, pgp_identity)

        # Add identity to public registry
        oesr_config["people"][person]["identity"] = pgp_identity

        # Add the fingerprint to the public registry
        oesr_config["people"][person]["fpr"] = pgp_fingerprint(pgp_identity)

        # For every other person in the list of people
        for other_person in people:
            if person != other_person:
                # Take a share from the list of the persons shares
                share = shares.pop(0)

                # Save the persons share to each other persons output dir: ${out_dir}/${other_person}/shares/${person}.share
                create_file(f"{output_dir}/{other_person}/shares/{person}.share", share)

    for person in people:
        # Copy over the keychain to the persons output dir
        shutil.copytree(f"{output_dir}/gnupg", f"{output_dir}/{person}/gnupg")

        # Export public key into the public output dir
        pgp_pub_path = export_pgp(
            f"{output_dir}/public/{person}.pgp.pub",
            oesr_config["people"][person]["identity"],
        )


    # Make sure each person has a copy of the public export
    for person in people:
        shutil.copytree(f"{output_dir}/public", f"{output_dir}/{person}/public")

    # Dump the oesr config to the public output dir
    create_file(f"{output_dir}/keep/oesr.json", json.dumps(oesr_config))

    # ENDC GREEN
    print(f"{GREEN}Initialised oesr peers in {output_dir}! {ENDC}\n")
    print(f"{CYAN}You can now use the verify and lint the {output_dir} with the oesr-cli{ENDC}\n")
    print(f"{CYAN}Remember to grab a copy of the {output_dir}/public directory and memorise or figure out a way to store the pseudonym mappings stored in {output_dir}/keep {ENDC}\n")





## CLI
@click.group()
def cmd():
    pass


@cmd.command()
@click.argument("people", nargs=-1, required=True)
@click.option("-o", "output_dir", required=True, help="Output directory.")
@click.option(
    "-t", "threshold", required=True, type=int, help="The SSSS share threshold."
)
def generate(people, output_dir, threshold):
    num = len(people)
    if threshold >= num:
        error(
            f"threshold must be smaller than the number of people: t/n = {threshold}/{num}"
        )
    if threshold <= 1:
        error(f"threshold must be > 1")
    if num <= 2:
        error(f"Number of identities need to be > 2")

    init_oesr(output_dir, people, threshold, num)


def read(path):
    with open(path, "r") as f:
        return f.read()


@cmd.command()
@click.option("-o", "output_dir", required=True, help="Output directory.")
def verify(output_dir):
    """Run some basic verifications."""

    set_gnupg_dir(f"{output_dir}/gnupg")
    oesr_config = json.loads(read(f"{output_dir}/keep/oesr.json"))

    for person, data in oesr_config["people"].items():
        shares = []

        for other_person, other_data in oesr_config["people"].items():
            if person != other_person:
                shares.append(
                    read(f"{output_dir}/{other_person}/shares/{person}.share")
                )

        # Get T number of shares (the minimum necessary to restore)
        secret_restored = ssss_combine(shares[: oesr_config["threshold"]])
        # Get the original passphrase
        secret_original = read(f"{output_dir}/{person}/passphrase")

        # Verify that the secret restored from the threshold number of shares is the same as the original.
        print(f"\n{BOLD}{CYAN}CHECK!{ENDC} {person}({data['identity']}@oesr.local)")
        if secret_restored == secret_original:
            print(
                f"{BOLD}{GREEN}OK!{ENDC} restored secret (using threshold * shares) matches original secret"
            )

        # Verify that the specific gpg key can be opened with it's respective passphrase
        if verify_pgp_passphrase(f"{output_dir}/{person}/passphrase", data["identity"]):
            print(
                f"{BOLD}{GREEN}OK!{ENDC} passphrase saved can unlock the private key."
            )


@cmd.command()
@click.option("-o", "output_dir", required=True, help="Output directory.")
def lint(output_dir):
    """Lint each persons certificate and print result."""

    set_gnupg_dir(f"{output_dir}/gnupg")
    oesr_config = json.loads(read(f"{output_dir}/keep/oesr.json"))

    for person, data in oesr_config["people"].items():
        print(f"{BOLD}{CYAN}LINT!{ENDC} {person}")
        lint_pgp(data["identity"])


if __name__ == "__main__":
    cmd()
