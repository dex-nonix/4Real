#!/bin/bash
set -e

CERTS_DIR=certs
mkdir -p $CERTS_DIR

if ! command -v mkcert &> /dev/null
then
    echo "mkcert could not be found, please install it first: https://github.com/FiloSottile/mkcert"
    exit 1
fi

echo "Installing mkcert root CA (if not already installed)..."
mkcert -install

PRIMARY_IP=$(ip -4 addr show scope global | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1 || true)
if [ -z "$PRIMARY_IP" ]; then
    PRIMARY_IP=$(hostname -I | awk '{print $1}')
fi
echo "Generating certificates for dev.local, *.dev.local, 127.0.0.1 and $PRIMARY_IP ..."
mkcert -cert-file $CERTS_DIR/dev.local.pem -key-file $CERTS_DIR/dev.local-key.pem dev.local "*.dev.local" 127.0.0.1 "$PRIMARY_IP"

echo "Certificates generated in $CERTS_DIR/"
echo "Now you can run: docker compose up -d"
