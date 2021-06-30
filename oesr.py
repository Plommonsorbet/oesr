import argparse
import json
from collections import defaultdict
import sys
import subprocess
import os
import shutil
import string
import secrets
import click

EXAMPLE_JSON = """
{
	"test@test.com": {"name": "Test Testersson"},
	"yest@yest.com": {"name": "Yest Testersson"},
	"best@best.com": {"name": "Best Testersson"},
	"rest@rest.com": {"name": "Rest Testersson"},
	"pest@pest.com": {"name": "Pest Testersson"}
}
"""


def error(msg):
    print(msg)
    sys.exit(1)

def pgp_keygen(email, name, t, n):
    """Generate pgp key"""
    pw = pwgen()
    subprocess.check_output(
        [
            "gpg",
            "--pinentry-mode",
            "loopback",
            "--batch",
            "--passphrase",
            pw,
            "--quick-generate-key",
            f"'{name} <{email}>'",
            "rsa4096",
            "sign,encrypt,auth",
            "never",
        ]
    )

    return ssss_split(pw, email, t, n)


def pwgen():
    """generate secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for i in range(64))


def pgp_export_pub(email, outpath):
    """Export public key to path"""
    return subprocess.check_output(
        [
            "gpg",
            "-o",
            outpath,
            "--export",
            "--armor",
            email,
        ]
    ).decode()


def ssss_split(secret, share_name, t, n):
    """Convert secret to ssss shares"""
    p = subprocess.Popen(
        ["ssss-split", "-t", str(t), "-n", str(n), "-Q", "-w", share_name],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = p.communicate(input=secret.encode())[0]
    return output.decode().splitlines()


## CLI
@click.group()
def cmd():
    pass

@cmd.command()
@click.option("-c", "config_path", help="Config file path.")
@click.option("-o", "out_dir", help="Output directory.")
@click.option("-g", "gnupg_dir", default="/tmp/gnupg", help="gnupg directory.")
@click.option("-t", "threshold", type=int, help="The SSSS share threshold.")
def generate(config_path, out_dir, gnupg_dir, threshold):

    with open(config_path) as f:
        identities = json.load(f)

    # Threshold must be less than n shares
    if threshold >= len(identities) - 1:
        error("threshold must be smaller than the number of identities")

    # Set keychain path
    os.makedirs(gnupg_dir)
    os.environ["GNUPGHOME"] = gnupg_dir

    out = defaultdict(dict)

    # Generate shares of password
    for share_email, data in identities.items():
        pgp_shares = pgp_keygen(share_email, data['name'], threshold, len(identities) - 1)
        identities[share_email]['shares'] = pgp_shares
        #identities[share_email]['shares'] = ssss_split(pw, threshold, len(identities) - 1, share_email)

        for email in identities.keys():
            # Divide the user share to each other user in the circle
            if share_email != email:
                out[email][share_email] = identities[share_email]['shares'].pop(-1)

    # Create directory for the common public data
    os.makedirs(out_dir)
    os.makedirs(f"{out_dir}/all")

    # Write shares to each other member in the OESR circle
    for email, data in out.items():
        os.makedirs(f"{out_dir}/{email}")

        for share_email, share in data.items():
            # Write share
            with open(f"{out_dir}/{email}/{share_email}.key.share", "w") as f:
                f.write(data[share_email])

        # Copy gnupg keychain the the OESR user output dir.
        shutil.copytree(gnupg_dir, f"{out_dir}/{email}/gnupg")

    # Export public keys
    for email in out.keys():
        pgp_export_pub(share_email, f"{out_dir}/all/{email}.pgp.pub")


@cmd.command()
@click.option("-f", "path", default="oesr-example.json", help="Config init path.")
def init_example(path):
    with open(path, "w") as f:
        f.write(EXAMPLE_JSON)


if __name__ == "__main__":
    cmd()
