#!/usr/bin/python3
from prometheus_client import start_http_server, Gauge
import subprocess
import json
import time

# Create Gauge metrics for download and upload speeds
download_speed_gauge = Gauge("{{ iperf_dl_speed_guage_metric_name }}", 'Current tunnel ndownload speed in Mbps')
upload_speed_gauge = Gauge("{{ iperf_ul_speed_guage_metric_name }}", 'Current tunnel upload speed in Mbps')

def run_iperf_client(server_ip, source_ip, server_port):
    command = ['iperf3', '-c', server_ip, '-J', '-B', source_ip, '-p', server_port]
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout.strip()

    try:
        json_output = json.loads(output)
        if 'end' in json_output:
            end = json_output['end']
            if 'sum_sent' in end and 'sum_received' in end:
                upload_speed_bps = end['sum_sent']['bits_per_second']
                download_speed_bps = end['sum_received']['bits_per_second']
                upload_speed_mbps = upload_speed_bps / 10**6
                download_speed_mbps = download_speed_bps / 10**6
                return upload_speed_mbps, download_speed_mbps

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON output: {e}")

    return None, None

def update_metrics(server_ip, source_ip, server_port):
    upload_speed, download_speed = run_iperf_client(server_ip, source_ip, server_port)

    if upload_speed is not None and download_speed is not None:
        download_speed_gauge.set(download_speed)
        upload_speed_gauge.set(upload_speed)
    else:
        download_speed_gauge.set(0)
        upload_speed_gauge.set(0)

def main():
    server_ip = "{{ iperf_server_address }}"
    source_ip = "{{ iperf_bind_address }}"
    server_port = "{{ iperf_server_port }}"

    # Start the Prometheus HTTP server
    start_http_server( addr='127.0.0.1', port={{ prometheus_iperf_endpoint_port }})

    while True:
        update_metrics(server_ip, source_ip, server_port)
        time.sleep({{ iperf_run_period }})  # Wait for X seconds before the next measurement

if __name__ == '__main__':
    main()

