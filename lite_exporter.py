#/bin/python3
import os
import time
from prometheus_client import start_http_server, Gauge, Enum
import requests
from  datetime import datetime

class AppMetrics:

    def __init__(self, app_port=80, polling_interval_seconds=5):
        self.app_port = app_port
        self.polling_interval_seconds = polling_interval_seconds


        self.latest_block_height = Gauge("latest_block_height", "Block number")
        self.health = Gauge("health", "Time delta")
        self.peers = Gauge("number_of_peers", "Number of p2p peers")

    def run_metrics_loop(self):
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        resp1 = requests.get(url=f"http://localhost:{self.app_port}/status?")
        resp2 = requests.get(url=f"http://localhost:{self.app_port}/dump_consensus_state?")
        status_data = resp1.json()
        consensus_data = resp2.json()

        self.latest_block_height.set(status_data['result']['sync_info']['latest_block_height'])
        self.health.set(datetime.now().timestamp() - datetime.strptime((f"{status_data['result']['sync_info']['latest_block_time']}")[0:-4] + 'Z', "%Y-%m-%dT%H:%M:%S.%f%z").timestamp())
        self.peers.set(len(consensus_data['result']['peers']))        

def main():
    
    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "5"))
    app_port = int(os.getenv("APP_PORT", "26657"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))

    app_metrics = AppMetrics(
        app_port=app_port,
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
