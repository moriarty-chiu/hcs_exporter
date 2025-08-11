import time
import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import REGISTRY, generate_latest
from clients.obs import OBSClient
from collectors.obs import OBSCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(generate_latest(REGISTRY))
        else:
            self.send_response(404)
            self.end_headers()

def main():
    """Main function to start the exporter."""
    logging.info("Starting HCS exporter...")
    
    try:
        obs_client = OBSClient().get_client()
    except ValueError as e:
        logging.error(f"Failed to create OBS client: {e}")
        sys.exit(1)

    obs_collector = OBSCollector(obs_client)
    REGISTRY.register(obs_collector)

    server_address = ('', 8100)
    httpd = HTTPServer(server_address, MetricsHandler)
    logging.info(f"Exporter started on port {server_address[1]}")
    httpd.serve_forever()

if __name__ == '__main__':
    main()