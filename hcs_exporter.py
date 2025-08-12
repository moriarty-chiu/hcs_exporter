import time
import logging
import sys
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import REGISTRY, push_to_gateway, CollectorRegistry
from clients.obs import OBSClient
from collectors.obs import OBSCollector
from utils.config import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class HealthCheckHandler(BaseHTTPRequestHandler):
    def __init__(self, health_check_path, *args, **kwargs):
        self.health_check_path = health_check_path
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == self.health_check_path:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

def start_health_check_server(config):
    """Start the health check server in a separate thread."""
    port = config['exporter']['port']
    health_check_path = config['exporter']['health_check_path']

    def handler(*args, **kwargs):
        return HealthCheckHandler(health_check_path, *args, **kwargs)

    httpd = HTTPServer(("", port), handler)
    logging.info(f"Health check server started on port {port}")
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

def main():
    """Main function to start the exporter."""
    logging.info("Starting HCS exporter...")

    config = load_config('conf/config.yml')
    start_health_check_server(config)

    pushgateway_address = config['pushgateway']['address']
    push_interval = config['pushgateway']['push_interval']
    job_name = config['pushgateway']['job_name']

    try:
        obs_client = OBSClient().get_client()
    except ValueError as e:
        logging.error(f"Failed to create OBS client: {e}")
        sys.exit(1)

    collectors = {
        'obs': OBSCollector
    }

    while True:
        registry = CollectorRegistry()
        for collector_name, collector_config in config['collectors'].items():
            if collector_config['enabled']:
                if collector_name in collectors:
                    collector_class = collectors[collector_name]
                    rate_limit_sleep = collector_config.get('rate_limit_sleep', 10)
                    collector_instance = collector_class(obs_client, rate_limit_sleep)
                    registry.register(collector_instance)
                else:
                    logging.warning(f"Collector '{collector_name}' is enabled but not found.")
        
        try:
            push_to_gateway(pushgateway_address, job=job_name, registry=registry)
            logging.info("Metrics pushed to Pushgateway.")
        except Exception as e:
            logging.error(f"Failed to push metrics to Pushgateway: {e}")
        
        time.sleep(push_interval)

if __name__ == '__main__':
    main()