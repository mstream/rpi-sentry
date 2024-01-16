#! /usr/bin/env bash

set -e

nix build .#sourceDist
ssh pi@192.168.0.75 'chmod +w ~/test/result && chmod -R +w  ~/test/result && rm -rf ~/test/result'
scp -r result pi@192.168.0.75:~/test
