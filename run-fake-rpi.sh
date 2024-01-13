#! /usr/bin/env nix-shell
#! nix-shell -i bash --packages docker-client

set -e

docker build -t fake-rpi docker/
docker run -p 2022:22 fake-rpi
