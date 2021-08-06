# Development

nix-build:
```sh
# Build package
> nix build

# Create key structure for 5 people
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

# Create key structure for 5 people
> rm -r /tmp/out; oesr-cli generate Rhea-Thisbe Nessa-Amor Kleio-Ing Hormazd-Philandros Hel-Phineus -t 4 -o /tmp/out;

# Verify created keys
> oesr-cli verify -o /tmp/out;

# Lint created keys
> oesr-cli lint -o /tmp/out;
```
