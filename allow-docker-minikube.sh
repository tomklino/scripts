if ! [ $(id -u) = 0 ]; then
  echo "Run with sudo"
  exit 1
fi

if grep "# Allow operation with minikube" /var/lib/snapd/apparmor/profiles/snap.docker.docker >/dev/null; then
  echo "File /var/lib/snapd/apparmor/profiles/snap.docker.docker already contains fix. Doing nothing";
  exit 0;
fi

sed -i -nE '1h;1!H;$g;$s|(.*)(^[ \t]*}[ \t]*$)|\1# Allow operation with minikube\nowner @{HOME}/.minikube/certs/* r,\n\2 |;$p' /var/lib/snapd/apparmor/profiles/snap.docker.docker &&
apparmor_parser -r /var/lib/snapd/apparmor/profiles/snap.docker.docker

