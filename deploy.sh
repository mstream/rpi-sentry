#! /usr/bin/env nix-shell
#! nix-shell -i bash --packages nodePackages.browserify

set -e

#nix build .#sourceDist
#ssh pi@192.168.0.75 'chmod +w ~/test/result && chmod -R +w  ~/test/result && rm -rf ~/test/result'
#scp -r result pi@192.168.0.75:~/test

browserify index.js -o rpi-sentry/static/bundle.js
scp -r rpi-sentry pi@192.168.0.75:~/
