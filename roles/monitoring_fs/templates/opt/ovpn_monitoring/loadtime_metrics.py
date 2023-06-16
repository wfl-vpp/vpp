#!/usr/bin/python3
from prometheus_client import start_http_server, Gauge
import time
import speedtest
import requests
import logging

# Create Gauge metrics to monitor speeds
download_speed_gauge = Gauge('FS_ST_DL', 'Current download speed in Mbps')
upload_speed_gauge = Gauge('FS_ST_UL', 'Current upload speed in Mbps')
google_load_time_gauge = Gauge('FS_RQ_LD_google', 'Load time for google.com in seconds')
google_error_time_gauge = Gauge('FS_RQ_ERR_google', 'Error time for google.com in seconds')
facebook_load_time_gauge = Gauge('FS_RQ_LD_facebook', 'Load time for facebook.com in seconds')
facebook_error_time_gauge = Gauge('FS_RQ_ERR_facebook', 'Error time for facebook.com in seconds')
youtube_load_time_gauge = Gauge('FS_RQ_LD_youtube', 'Load time for youtube.com in seconds')
youtube_error_time_gauge = Gauge('FS_RQ_ERR_youtube', 'Error time for youtube.com in seconds')
instagram_load_time_gauge = Gauge('FS_RQ_LD_instagram', 'Load time for instagram.com in seconds')
instagram_error_time_gauge = Gauge('FS_RQ_ERR_instagram', 'Error time for instagram.com in seconds')

def measure_speed():
    try:
        # Create a speedtest-cli object
        st = speedtest.Speedtest()

        # Perform the speed test
        st.download()
        st.upload()

        # Get the download and upload speed results in Mbps
        download_speed = st.results.download # / 1024*1024
        upload_speed = st.results.upload # / 1024*1024

        # Set the gauge metric values
        download_speed_gauge.set(download_speed)
        upload_speed_gauge.set(upload_speed)

    except speedtest.SpeedtestException as e:
        logging.error(f"Speed test failed: {e}")

    except Exception as e:
        logging.error(f"An error occurred during speed test: {e}")

def measure_load_time():
    try:
        # Measure load time for google.com
        google_response = requests.get("https://www.google.com")
        if google_response.status_code == 200:
            google_load_time = google_response.elapsed.total_seconds()
            google_load_time_gauge.set(google_load_time)
        else:
            google_error_time = google_response.elapsed.total_seconds()
            google_error_time_gauge.set(google_error_time)

        # Measure load time for facebook.com
        facebook_response = requests.get("https://www.facebook.com")
        if facebook_response.status_code == 200:
            facebook_load_time = facebook_response.elapsed.total_seconds()
            facebook_load_time_gauge.set(facebook_load_time)
        else:
            facebook_error_time = facebook_response.elapsed.total_seconds()
            facebook_error_time_gauge.set(facebook_error_time)

        # Measure load time for youtube.com
        youtube_response = requests.get("https://www.youtube.com")
        if youtube_response.status_code == 200:
            youtube_load_time = youtube_response.elapsed.total_seconds()
            youtube_load_time_gauge.set(youtube_load_time)
        else:
            youtube_error_time = youtube_response.elapsed.total_seconds()
            youtube_error_time_gauge.set(youtube_error_time)

        # Measure load time for instagram.com
        instagram_response = requests.get("https://www.instagram.com")
        if instagram_response.status_code == 200:
            instagram_load_time = instagram_response.elapsed.total_seconds()
            instagram_load_time_gauge.set(instagram_load_time)
        else:
            instagram_error_time = instagram_response.elapsed.total_seconds()
            instagram_error_time_gauge.set(instagram_load_time)

    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")

    except Exception as e:
        logging.error(f"An error occurred during load time measurement: {e}")

if __name__ == '__main__':
    # Start the Prometheus HTTP server
    start_http_server(addr='{{ loadtime_prometheus_listen_addr }}', port={{ loadtime_prometheus_expose_port }})

    # Periodically measure and update the speed and load time metrics
    while True:
        measure_speed()
        measure_load_time()
        time.sleep({{ loadtime_interval }})  # Measure speed and load time every X seconds
