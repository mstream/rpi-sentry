#! /usr/bin/env nix-shell
#! nix-shell -i bash --packages nodePackages.browserify

set -e

cp index.css rpi-sentry/static/
browserify index.js -o rpi-sentry/static/bundle.js
scp -r rpi-sentry pi@192.168.0.75:~/
