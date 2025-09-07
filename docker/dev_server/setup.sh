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

echo "Generating certificates for dev.local and *.dev.local ..."
mkcert -cert-file $CERTS_DIR/dev.local.pem -key-file $CERTS_DIR/dev.local-key.pem dev.local "*.dev.local"

echo "Certificates generated in $CERTS_DIR/"
echo "Now you can run: docker compose up -d"
