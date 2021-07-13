# OESR

A methodology for long term backup of sensitive data leveraging shamir's secret sharing scheme and openpgp.

## Overview

_*input*_

 threshold # the minimum number of shares to restore

 people # a list of names

 output-dir # a path to use as output directory


_*Output Directory Structure*_

$out/gnupg/

$out/$person/

$out/$person/passphrase - the users own passphrase to be used with gpg --passphrase-file. This will all have luks on it so it will be encrypted and one person cannot cause any damage if they are naughty.
			
$out/$person/gnupg  - The gnupg keychain with all the keys (encrypted with their individual passphrases of course)

$out/$person/shares/$other-person.share - one of the N shares of the other people in the oesr circle's passphrase

$out/public

$out/public/$person.pgp.pub - public key export

$out/public/oesr.json - oser circle details containing the real name, the gpg identity and the fingerprint. To be used for automate the creation of new oesr backup items.


_oesr.json example_
```json
{
  "people": {
    "Rhea-Thisbe": {
      "identity": "strudel-approach",
      "fpr": "3BCB608512775880626FBF95013598E3DFE11B63"
    },
    "Nessa-Amor": {
      "identity": "finalize-bonehead",
      "fpr": "E3D40CDE6EAD90CB3A56BAA8109355E43FC43A91"
    },
    "Kleio-Ing": {
      "identity": "morally-clammy",
      "fpr": "5B538056832EED1F12F4CA28844F6AF0DAE37D02"
    },
    "Hormazd-Philandros": {
      "identity": "excuse-swizzle",
      "fpr": "230C950B5B1431F629868AF546249560B4712A40"
    },
    "Hel-Phineus": {
      "identity": "finlike-resource",
      "fpr": "6DF84228287C9439A16837B9E617E8F1CEF3E60F"
    }
  },
  "threshold": 4,
  "num": 5
}
```

# Development

nix-build:
```sh
# Build package
> nix-build

# Create key structure
> rm -r /tmp/out; ./result/bin/oesr-cli generate Rhea-Thisbe Nessa-Amor Kleio-Ing Hormazd-Philandros Hel-Phineus -t 4 -o /tmp/out;

# Verify created keys
> ./result/bin/oesr-cli verify -o /tmp/out;

# Lint created keys
> ./result/bin/oesr-cli lint -o /tmp/out;
```

nix-shell
```sh
# Build package
> nix-shell

# Create key structure
> rm -r /tmp/out; oesr-cli generate Rhea-Thisbe Nessa-Amor Kleio-Ing Hormazd-Philandros Hel-Phineus -t 4 -o /tmp/out;

# Verify created keys
> oesr-cli verify -o /tmp/out;

# Lint created keys
> oesr-cli lint -o /tmp/out;
```


## OESR Setup

### Live CD setup

##### Generate a NixOS live cd with the required packages
```sh
nix build './nix-live-cd#nixosConfigurations.liveCD.config.system.build.isoImage' 
```
_iso can be found in `./result/iso/`_ 

##### Copy the live cd to a usb
```sh
cp -vi result/iso/*.iso /dev/sdX

```

### Generate keys

***IMPORTANT! Boot from the live usb and unplug ethernet/hardware disable the wifi***

##### Example generate oesr keys for 6 people with the threshold 4 and output it to `/tmp/out`
```sh
oesr-cli generate "firstname-lastname-1" "firstname-lastname-2" "firstname-lastname-3" "firstname-lastname-4" "firstname-lastname-5" "firstname-lastname-6" -t 4 -o /tmp/out
```

##### Setup usb

```sh
# Select the usb block device
> USB_DEVICE=/dev/sdX
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

_tip after this step make sure to manually verify that the password matches_
```sh
# Test open with manual password entry
> sudo cryptsetup luksOpen $USB_DEVICE
# Close the encrypted partition again
> sudo cryptsetup luksClose $USB_DEVICE
```
