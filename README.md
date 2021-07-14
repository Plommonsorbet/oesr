# OESR

A methodology for long term backup of sensitive data leveraging shamir's secret sharing scheme and openpgp.

## Explanation

![graph-1](./media/ssss-split-graph.png)


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

### Setup usb

This step needs to be done for each person in the oesr circle and requires a separate usb for each person.

#### Manual usb setup

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

#### Scripted usb setup
Since I'm lazy and don't like doing this so many times I wrote a small and somewhat naive script to setup the usb for me. **USE AT YOUR OWN RISK!**
```
sudo oesr-usb-setup -d /dev/sdX -p "<my-password>" -i /tmp/out/<person>
```

#### Verification
_tip after this step make sure to manually verify that the password matches_

```sh
# Test open with manual password entry
> sudo cryptsetup luksOpen $USB_DEVICE

# Close the encrypted partition again
> sudo cryptsetup luksClose $USB_DEVICE
```

## Development

See [development](./docs/development.md) for more details about the internals and how to setup the development environment.
