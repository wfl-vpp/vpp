#!/usr/bin/python3
from prometheus_client import start_http_server, Gauge
import time
import speedtest
import requests
import logging
import socket
from requests_toolbelt.adapters.socket_options import SocketOptionsAdapter

# Create Gauge metrics to monitor speeds
download_speed_gauge = Gauge('IR_ST_DL', 'Current download speed in Mbps')
upload_speed_gauge = Gauge('IR_ST_UL', 'Current upload speed in Mbps')
google_load_time_gauge = Gauge('IR_RQ_LD_google', 'Load time for google.com in seconds')
google_error_time_gauge = Gauge('IR_RQ_ERR_google', 'Error time for google.com in seconds')
facebook_load_time_gauge = Gauge('IR_RQ_LD_facebook', 'Load time for facebook.com in seconds')
facebook_error_time_gauge = Gauge('IR_RQ_ERR_facebook', 'Error time for facebook.com in seconds')
youtube_load_time_gauge = Gauge('IR_RQ_LD_youtube', 'Load time for youtube.com in seconds')
youtube_error_time_gauge = Gauge('IR_RQ_ERR_youtube', 'Error time for youtube.com in seconds')
instagram_load_time_gauge = Gauge('IR_RQ_LD_instagram', 'Load time for instagram.com in seconds')
instagram_error_time_gauge = Gauge('IR_RQ_ERR_instagram', 'Error time for instagram.com in seconds')

def measure_speed():
    try:
        # Create a speedtest-cli object with iface and source options
        st = speedtest.Speedtest(source_address='10.200.0.2')
        st.get_servers()
        st.get_best_server()
#        st.download(threads=None, pre_allocate=False, timeout=10, check=False, secure=True, source_address=None)

        # Get the download and upload speed results in Mbps
        download_speed = st.results.download #/ 10**6
        upload_speed = st.results.upload #/ 10**6

        # Set the gauge metric values
        download_speed_gauge.set(download_speed)
        upload_speed_gauge.set(upload_speed)

    except speedtest.SpeedtestException as e:
        logging.error(f"Speed test failed: {e}")

    except Exception as e:
        logging.error(f"An error occurred during speed test: {e}")

def measure_load_time():
    try:
        session = requests.Session()
        # set interface here
        options = [(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"{{ IR_FS_tunnel_interface }}")]
        for prefix in ('http://', 'https://'):
            session.mount(prefix, SocketOptionsAdapter(socket_options=options))



        # Measure load time for google.com through the tunnel interface
        google_response = session.get("https://www.google.com", headers={'Host': 'www.google.com'}, verify=True)
        if google_response.status_code == 200:
            google_load_time = google_response.elapsed.total_seconds()
            google_load_time_gauge.set(google_load_time)
        else:
            google_error_time = google_response.elapsed.total_seconds()
            google_error_time_gauge.set(google_error_time)


        # Measure load time for facebook.com through the tunnel interface
        facebook_response = session.get("https://www.facebook.com", headers={'Host': 'www.facebook.com'}, verify=True)
        if facebook_response.status_code == 200:
            facebook_load_time = facebook_response.elapsed.total_seconds()
            facebook_load_time_gauge.set(facebook_load_time)
        else:
            facebook_error_time = facebook_response.elapsed.total_seconds()
            facebook_error_time_gauge.set(facebook_error_time)


        # Measure load time for youtube.com through the tunnel interface
        youtube_response = session.get("https://www.youtube.com", headers={'Host': 'www.youtube.com'}, verify=True)
        if youtube_response.status_code == 200:
            youtube_load_time = youtube_response.elapsed.total_seconds()
            youtube_load_time_gauge.set(youtube_load_time)
        else:
            youtube_error_time = youtube_response.elapsed.total_seconds()
            youtube_error_time_gauge.set(youtube_error_time)


        # Measure load time for instagram.com through the tunnel interface
        instagram_response = session.get("https://www.instagram.com", headers={'Host': 'www.instagram.com'}, verify=True)
        if instagram_response.status_code == 200:
            instagram_load_time = instagram_response.elapsed.total_seconds()
            instagram_load_time_gauge.set(instagram_load_time)
        else:
            instagram_error_time = instagram_response.elapsed.total_seconds()
            instagram_error_time_gauge.set(instagram_error_time)
    except session.RequestException as e:
        logging.error(f"Request failed: {e}")

    except Exception as e:
        logging.error(f"An error occurred during load time measurement: {e}")

if __name__ == '__main__':
    # Start the Prometheus HTTP server
    try:
        start_http_server(addr='{{ loadtime_prometheus_listen_addr }}', port={{ loadtime_prometheus_expose_port }})
        logging.info("Prometheus HTTP server started successfully.")
    except Exception as e:
        logging.error(f"Failed to start Prometheus HTTP server: {e}")


    # Periodically measure and update the speed and load time metrics
    while True:
        #measure_speed()
        measure_load_time()
        time.sleep({{ loadtime_interval }})  # Measure speed and load time every X seconds

