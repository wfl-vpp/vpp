#!/bin/bash

# Path to the peer file
PEER_FILE="{{ ovpn_root }}/peers"

# Path to the service file
SERVICE_FILE="/etc/stunnel/stunnel-client.conf"

# Port to check for reachability
PORT={{ fs_server_port }}

# Read the current IP from the service file
CURRENT_IP=$(grep -oE -- 'connect = \S+' "$SERVICE_FILE" | awk '{print $3}' | cut -d: -f1)

# Function to check if a port is open on an IP
function is_port_open() {
  local ip=$1
  nc -z -w1 "$ip" "$PORT" >/dev/null 2>&1
}

# Read all IP addresses from the peer file
mapfile -t IPS < "$PEER_FILE"

# Shuffle the IP addresses randomly
shuf -o IPS <<<"${IPS[*]}"

# Loop through the IP addresses
for ip in "${IPS[@]}"; do
  # Skip the current IP used in the service file
  if [[ "$ip" == "$CURRENT_IP" ]]; then
    continue
  fi

  # Check if the port is open on the IP
  if is_port_open "$ip"; then
    # Replace the IP in the service file with the selected IP
    sed -i "s|connect = $CURRENT_IP|connect = $ip|" "$SERVICE_FILE"

    # Reload the systemd daemon
    systemctl daemon-reload

    # Restart the OpenVPN service
    systemctl restart stunnel-ovpn.service
    systemctl restart openvpn-irclient.service

    echo "Switched to IP: $ip"
    exit 0
  fi
done

echo "No reachable IP found in the peer file."
exit 1

