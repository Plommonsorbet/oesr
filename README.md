# OESR: Offline Emergency Secret Recovery 

A methodology or system for a maintainable long term backups of critical and sensitive data leveraging secret sharing and pki to ensure security and redundancy.

## Background

Before this I had a similar system for backing up my gpg keys, that setup consisted of symmetrically encrypting my gpg key with a 64 character key and then splitting this into 7 parts which was placed on each usb. The symetrical key I also split into a few pieces and created qr codes for these shares and hid them in various places.

This worked fine and I was very happy with the security, however this was completely un-maintainable over time as I wanted to add more things. The logistics of gathering all my usbs into one place was such a pain, as well as this was a potential security flaw as this introduced a time of vulnerability.

So I wanted to solve how I keep the aspects I like but make this actually maintainable for me, through a ton of thinking and discussions about this problem space the solution that emerged is that you need to split the data and the encryption. 

The encryption keys rarely need to be changed or accessed unless all hell breaks loose and I need to actually recover something, so instead this method is designed in such a way that on the usb's you store the way to recover the secrets and so you can encrypt new secret without access to the encryption keys, then you can store the data in the cloud, on usbs, paper or whatever medium you wish.

You can read the in depth design of the system [here](./docs/DESIGN.md).

# Using OESR

This requires the nix package manager with nix flakes enabled to run. And that is simply because I love nix and I exclusively run nixOS so I built this whole setup around it, I'm sure you can do this via another distributions live-cd however you'll need to figure that out on your own.

If you want to try your hand at this then this is what you'll need:
- python37 and dependencies (can be found in pyproject.lock)
- [sss-cli](https://github.com/dsprenkels/sss-cli)
-  gnupg
-  hopenpgp-tools

## OESR Encryption keys setup
### Live CD Setup

```sh
nix build './nix-live-cd#nixosConfigurations.liveCD.config.system.build.isoImage' 
```
_iso can be found in `./result/iso/`_ 

*Then use this to make a bootable usb*
```sh
cp -vi result/iso/*.iso /dev/sdX
```

### Generate keys

**IMPORTANT!** *Boot from the live usb and unplug ethernet/hardware disable the wifi*

Example generate oesr keys for 6 people with the threshold 4 and output it to `/tmp/out`
```sh
oesr-cli generate "firstname-lastname-1" "firstname-lastname-2" "firstname-lastname-3" "firstname-lastname-4" "firstname-lastname-5" "firstname-lastname-6" -t 3 -o /tmp/out
```

## Setup usbs with OESR encryption setup

This step needs to be done for each person in the oesr circle and requires a separate usb for each person.

### Scripted usb setup
Since I'm lazy and don't like doing this so many times, so I wrote a small and somewhat naive [script](./oesr_usb_setup.py) to setup the usb for me. **!USE AT YOUR OWN RISK!**
```
# This wipes the device, creates an encrypted luks volume and copies over the person's exported output. It will ask you to confirm before starting.
> sudo oesr-usb-setup -d /dev/sdX -p "<my-password>" -i /tmp/out/<person>
```

### Verification
_it's important to verify the password works after the usb is generated, do this manually._

```sh
# Test open with manual password entry
> sudo cryptsetup luksOpen $USB_DEVICE

# Close the encrypted partition again
> sudo cryptsetup luksClose $USB_DEVICE
```

### Manual usb setup

```sh
# Select the usb block device
> USB_DEVICE=/dev/sdX
# Select the person to export to usb
> OESR_IDENTITIY=/tmp/out/<person>

# Wipe the block_device
> sudo wipefs -a $USB_DEVICE

# Set the luks passphrase
> LUKS_PW="this is my passphrase"

# Luks format the device
> echo -n $LUKS_PW | sudo cryptsetup luksFormat $USB_DEVICE -
# Open luks device
> echo -n $LUKS_PW | sudo cryptsetup luksOpen $USB_DEVICE oesr-enc-usb -

# Format encrypted partition and set label to be the persons name
> sudo mkfs.ext2 /dev/mapper/oesr-enc-usb -L <person>

# mount encrypted partition
> sudo mount /dev/mapper/oesr-enc-usb /mnt

# Copy over the relevant files
> cp -r $OESR_IDENTITY /mnt

# Unmount encrypted partition
> umount /mnt

# Close oesr-enc-usb
> sudo cryptsetup luksClose /dev/mapper/oesr-enc-usb

```

### Distribute the keys

## Backup secret

# Hacking

You can see more about the nix development setup [here](./docs/HACKING.md).
