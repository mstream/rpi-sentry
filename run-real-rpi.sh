#! /usr/bin/env nix-shell
#! nix-shell -i bash --packages docker-client

set -e

ssh-copy-id mstream@192.168.0.75
