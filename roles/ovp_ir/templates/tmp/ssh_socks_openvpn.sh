#!/usr/bin/bash
ssh -i {{ target_ssh_key }} -fR {{ socks_proxy_port }}:{{ openvpn_pkg_repo_host }}:80 {{ inventory_hostname }} sleep {{ socks_proxy_duration }} &
exit 0
