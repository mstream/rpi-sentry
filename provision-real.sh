#! /usr/bin/env nix-shell
#! nix-shell -i bash --packages ansible python3

ansible-playbook -i provisioning/hosts -l real-rpi provisioning/playbook-sudo-rpi.yml