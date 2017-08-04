#!/bin/bash

knife search users "groups:syadmin" -a action -a email -a id > /tmp/sysadmins

grep -E "action|email|id" /tmp/sysadmins | sed -r '/action/N;N;s/action\:[\ ]+([a-z]+)\n[\ ]+email\:[\ ]+([a-z@\.]+)\n[\ ]+id\:[\ ]+([a-z]+)/\1\t\2\t\3/'
