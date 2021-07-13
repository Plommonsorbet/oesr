# Development

nix-build:
```sh
# Build package
> nix build

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
> nix develop

# Create key structure
> rm -r /tmp/out; oesr-cli generate Rhea-Thisbe Nessa-Amor Kleio-Ing Hormazd-Philandros Hel-Phineus -t 4 -o /tmp/out;

# Verify created keys
> oesr-cli verify -o /tmp/out;

# Lint created keys
> oesr-cli lint -o /tmp/out;
```

# Output Directory Overview

```
/tmp/out
├── gnupg # gpg keychain containing all keys
├── public # public keys and json containg each identity's pseudonym.
│  ├── Hel-Phineus.pgp.pub
│  ├── Hormazd-Philandros.pgp.pub
│  ├── Kleio-Ing.pgp.pub
│  ├── Nessa-Amor.pgp.pub
│  ├── oesr.json # contains each persons name mapped to their gpg pseudonym
│  └── Rhea-Thisbe.pgp.pub
├── Hel-Phineus
│  ├── gnupg # copy of ../gnupg
│  ├── passphrase # the passphrase for the key owned by this user
│  └── shares # the shares of each other persons password
│     ├── Hormazd-Philandros.share
│     ├── Kleio-Ing.share
│     ├── Nessa-Amor.share
│     └── Rhea-Thisbe.share
├── Hormazd-Philandros
│  ├── gnupg # copy of ../gnupg
│  ├── passphrase # the passphrase for the key owned by this user
│  └── shares # the shares of each other persons password
│     ├── Hel-Phineus.share
│     ├── Kleio-Ing.share
│     ├── Nessa-Amor.share
│     └── Rhea-Thisbe.share
├── Kleio-Ing
│  ├── gnupg # copy of ../gnupg
│  ├── passphrase # the passphrase for the key owned by this user
│  └── shares # the shares of each other persons password
│     ├── Hel-Phineus.share
│     ├── Hormazd-Philandros.share
│     ├── Nessa-Amor.share
│     └── Rhea-Thisbe.share
├── Nessa-Amor
│  ├── gnupg # copy of ../gnupg
│  ├── passphrase # the passphrase for the key owned by this user
│  └── shares # the shares of each other persons password
│     ├── Hel-Phineus.share
│     ├── Hormazd-Philandros.share
│     ├── Kleio-Ing.share
│     └── Rhea-Thisbe.share
└── Rhea-Thisbe
   ├── gnupg # copy of ../gnupg
   ├── passphrase # the passphrase for the key owned by this user
   └── shares # the shares of each other persons password
      ├── Hel-Phineus.share
      ├── Hormazd-Philandros.share
      ├── Kleio-Ing.share
      └── Nessa-Amor.share
```

_oesr.json example_
```json
{
  "people": {
    "Rhea-Thisbe": {
      "identity": "strudel-approach", # this is the pseudonym used my gpg
      "fpr": "3BCB608512775880626FBF95013598E3DFE11B63"
    },
    "Nessa-Amor": {
      "identity": "finalize-bonehead", # this is the pseudonym used my gpg
      "fpr": "E3D40CDE6EAD90CB3A56BAA8109355E43FC43A91"
    },
    "Kleio-Ing": {
      "identity": "morally-clammy", # this is the pseudonym used my gpg
      "fpr": "5B538056832EED1F12F4CA28844F6AF0DAE37D02"
    },
    "Hormazd-Philandros": {
      "identity": "excuse-swizzle", # this is the pseudonym used my gpg
      "fpr": "230C950B5B1431F629868AF546249560B4712A40"
    },
    "Hel-Phineus": {
      "identity": "finlike-resource", # this is the pseudonym used my gpg
      "fpr": "6DF84228287C9439A16837B9E617E8F1CEF3E60F"
    }
  },
  "threshold": 4,
  "num": 5
}
```
