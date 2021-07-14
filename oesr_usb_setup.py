import click
import subprocess
import os
import sys
import shutil

CYAN = "\033[96m"
GREEN = "\033[92m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"

def task(msg):
    print(f"{GREEN}TASK! {msg}{ENDC}", file=sys.stderr)

def error(msg):
    print(f"{FAIL}ERROR! {msg}{ENDC}", file=sys.stderr)
    sys.exit(1)


#----------------------# LUKS #----------------------#

def luks_format(device, passphrase):
    p = subprocess.Popen(
        ["cryptsetup", "luksFormat", device, "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, err = p.communicate(input=passphrase.encode())

    if p.returncode != 0:
        error(f"luksformat failed: {err.decode()}`")

    print(output.decode())

def luks_open(device, passphrase, encrypted_part_name):
    p = subprocess.Popen(
        ["cryptsetup", "luksOpen", device, encrypted_part_name, "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, err = p.communicate(input=passphrase.encode())

    if p.returncode != 0:
        error(f"luksopen failed: {err.decode()}`")

    print(output.decode())

def luks_close(encrypted_part):
    out = subprocess.check_output(["cryptsetup", "luksClose", encrypted_part])
    print(out.decode())

#----------------------# LUKS #----------------------#


#----------------------#  FS  #----------------------#
def mkfs_ext4(device):
    out = subprocess.check_output(["mkfs.ext4", device])
    print(out.decode())

def mount(device, dest):
    out = subprocess.check_output(["mount", device, dest])
    print(out.decode())

def umount(device):
    out = subprocess.check_output(["umount", device])
    print(out.decode())

def wipe_device(device):
    out = subprocess.check_output(["wipefs", "-a", device])
    print(out.decode())

#----------------------#  FS  #----------------------#


def copy_files(src, dest):
    shutil.copytree(src, dest)

def print_tree(path):
    out = subprocess.check_output(['tree', path])
    print(out.decode())

@click.option("-i", "input_dir", required=True, help="Input Directory")
@click.option("-p", "pw", required=True, help="Password")
@click.option("-d", "device", required=True, help="Block Device to use for usb")
@click.command()
def setup_luks_usb(input_dir, pw, device):
    encrypted_part_name = "oesr-enc-usb"
    encrypted_part = f"/dev/mapper/{encrypted_part_name}"

    mount_path="/tmp/oesr-usb-mount"

    if input(f"Are you sure you want to wipe and format the {device}? Write `YES` in all caps to confirm: ") != "YES":
        error("You need to confirm this action to proceed")
    task("Starting USB setup!")
    os.makedirs(mount_path, exist_ok=True)

    task(f"Wipe device")
    wipe_device(device)

    task(f"LUKS Format disk")
    luks_format(device, pw)

    task(f"LUKS open disk {device} at {encrypted_part}")
    luks_open(device, pw, encrypted_part_name)

    task(f"Format ext4 fs on {encrypted_part}")
    mkfs_ext4(encrypted_part)

    task(f"Mount {encrypted_part} at {mount_path}")
    mount(encrypted_part, mount_path)

    

    task(f"Copy files {input_dir} to {mount_path}/oesr")
    copy_files(input_dir, f"{mount_path}/oesr")

    task(f"Print the exported directory at {mount_path}")
    print_tree(mount_path)

    task(f"Umount {encrypted_part}")
    umount(encrypted_part)

    task(f"LUKS close {encrypted_part}")
    luks_close(encrypted_part)

setup_luks_usb()
