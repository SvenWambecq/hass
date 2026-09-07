#!/bin/bash
# Renews the Let's Encrypt certificate for sveneniris.duckdns.org.
# Requires passwordless sudo for the exact commands below (see README.md).
set -e

sudo /usr/bin/systemctl stop nginx
sudo /usr/bin/certbot renew --cert-name sveneniris.duckdns.org --preferred-challenges http-01
sudo /usr/bin/systemctl start nginx
