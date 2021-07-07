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


def error(msg):
    print(f"ERROR! {msg}", file=sys.stderr)
    sys.exit(1)


def pwgen():
    """generate secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for i in range(64))


def create_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    return path


def gen_gnupg_dir():
    """Generate a temp directory and set it as gnupg home"""
    gnupg_path = tempfile.mkdtemp(dir="/tmp", prefix="oesr-gnupg")
    os.environ["GNUPGHOME"] = gnupg_path
    return gnupg_path


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

    output, err = p.communicate(input="\n".join(shares).encode())
    if p.returncode != 0:
        error(f"ssss_combine failed:{err.decode()}`")
    return output.decode()


def gen_pgp_key(pw_file, identity):
    """Generate pgp key"""
    subprocess.check_output(
        [
            "gpg",
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
    out = subprocess.check_output(
        [
            "gpg",
            "--list-keys",
            "--with-colons",
            f"{identity}@oesr.local",
        ]
    ).decode()

    for line in out.splitlines():
        if line.startswith("fpr"):
            fingerprint = line.split(":")[9]
            return fingerprint


def verify_pgp_passphrase(pw_file, identity):
    out = subprocess.check_output(
        [
            "gpg",
            "--pinentry-mode",
            "loopback",
            "--batch",
            "--passphrase-file",
            pw_file,
            "--export-secret-keys",
            "-a",
            f"{identity}@oesr.local",
        ]
    ).decode()


def init_oesr(output_dir, people, threshold, num):
    """Generate oesr peers"""
    oesr_config = {"people": defaultdict(dict), "threshold": threshold, "num": num}

    # Generate public output dir
    os.makedirs(f"{output_dir}/public", exist_ok=True)

    # Generate each persons output dir
    for person in people:
        os.makedirs(f"{output_dir}/{person}", exist_ok=True)
        os.makedirs(f"{output_dir}/{person}/shares", exist_ok=True)

    # Generate a tempdir and set it as GNUPGHOME
    gnupg_path = gen_gnupg_dir()

    for person in people:
        # Generate a pseudonym for the person to use as pgp identity
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
        shutil.copytree(gnupg_path, f"{output_dir}/{person}/gnupg")

        # Export public key into the public output dir
        pgp_pub_path = export_pgp(
            f"{output_dir}/public/{person}.pgp.pub",
            oesr_config["people"][person]["identity"],
        )

    # Dump the oesr config to the public output dir
    create_file(f"{output_dir}/public/oesr.json", json.dumps(oesr_config))


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
    oesr_config = json.loads(read(f"{output_dir}/public/oesr.json"))

    for person, data in oesr_config["people"].items():
        shares = []

        for other_person, other_data in oesr_config["people"].items():
            if person != other_person:
                shares.append(
                    read(f"{output_dir}/{other_person}/shares/{person}.share")
                )

        secret_restored = ssss_combine(shares[: oesr_config["threshold"]])
        secret_original = read(f"{output_dir}/{person}/passphrase")

        print(f"\nCHECK: {person}({data['identity']}@oesr.local)")
        if secret_restored == secret_original:
            print(
                "OK! restored secret (using threshold * shares) matches original secret"
            )

        if verify_pgp_passphrase(f"{output_dir}/{person}/passphrase", data["identity"]):
            print("OK! passphrase saved can unlock the private key.")


# verify()
# cmd()
#if __name__ == "__main__":
    #cmd()
