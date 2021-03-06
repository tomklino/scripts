#!/bin/bash

echo "upgrading dist in progress" > /tmp/chef.lock &&
export APT_LISTCHANGES_FRONTEND=none &&
export DEBIAN_FRONTEND=noninteractive &&
echo 'libc6 libraries/restart-without-asking boolean true' | debconf-set-selections &&
echo "executing wheezy to jessie" &&
find /etc/apt -name "*.list" | xargs sed -i '/^deb/s/wheezy/jessie/g' &&
echo "executing autoremove" &&
apt-get -fuy --force-yes autoremove &&
echo "executing clean" &&
apt-get --force-yes clean &&
echo "cleaning old lists" &&
rm /var/lib/apt/lists/* -rf
echo "executing update" &&
apt-get update -o Acquire::CompressionTypes::Order::=gz &&
echo "executing upgrade" &&
apt-get --force-yes -o Dpkg::Options::="--force-confold" --force-yes -o Dpkg::Options::="--force-confdef" -fuy upgrade &&
echo "executing dist-upgrade" &&
apt-get --force-yes -o Dpkg::Options::="--force-confold" --force-yes -o Dpkg::Options::="--force-confdef" -fuy dist-upgrade &&
echo "distribution upgrade finished succesfuly - you should reboot the machine now!"
cat /etc/*-release
