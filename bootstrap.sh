#!/usr/bin/env bash

sudo apt-get update
sudo apt-get upgrade

sudo apt-get install -y python3
sudo apt-get install -y python-virtualenv

virtualenv -p python3 /vagrant/venv
sudo apt-get install -y build-essential python3-dev postgresql postgresql-contrib libpq-dev

source vagrant/venv/bin/activate
pip install --upgrade pip
pip install -r /vagrant/requirements.txt

# Consul and Vault
sudo apt-get install -y unzip
wget https://releases.hashicorp.com/consul/0.7.5/consul_0.7.5_linux_amd64.zip?_ga=1.48262182.1681598438.1487547995
wget https://releases.hashicorp.com/vault/0.6.5/vault_0.6.5_linux_amd64.zip



consul agent -server -bootstrap-expect 1 -data-dir /tmp/consul -bind 127.0.0.1
export VAULT_ADDR='http://127.0.0.1:8200'
