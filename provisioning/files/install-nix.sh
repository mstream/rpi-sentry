#! /bin/bash

set -e
set -E

sh <(curl -L https://nixos.org/nix/install) --no-daemon
