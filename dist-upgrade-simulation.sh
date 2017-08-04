#!/bin/bash

echo "upgrading dist in progress" > /tmp/chef.lock &&
export APT_LISTCHANGES_FRONTEND=none &&
export DEBIAN_FRONTEND=noninteractive &&
echo 'libc6 libraries/restart-without-asking boolean true' | debconf-set-selections &&
echo "executing wheezy to jessie" &&
find /etc/apt -name "*.list" | xargs sed -i '/^deb/s/wheezy/jessie/g' &&
echo "executing autoremove" &&
apt-get -s autoremove &&
echo "executing clean" &&
apt-get -s clean &&
echo "cleaning old lists" &&
rm /var/lib/apt/lists/* -rf
echo "executing update" &&
apt-get update -o Acquire::CompressionTypes::Order::=gz &&
echo "executing upgrade" &&
apt-get -o Dpkg::Options::="--force-confold" -o Dpkg::Options::="--force-confdef" -s upgrade &&
echo "executing dist-upgrade" &&
apt-get -o Dpkg::Options::="--force-confold" -o Dpkg::Options::="--force-confdef" -s dist-upgrade
find /etc/apt -name "*.list" | xargs sed -i '/^deb/s/jessie/wheezy/g'
rm /tmp/chef.lock
