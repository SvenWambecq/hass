#!/bin/bash
# Renews the Let's Encrypt certificate for sveneniris.duckdns.org.
# Requires passwordless sudo for the exact commands below (see README.md).
set -e

sudo systemctl stop nginx
sudo certbot renew --cert-name sveneniris.duckdns.org --preferred-challenges http-01
sudo systemctl start nginx
