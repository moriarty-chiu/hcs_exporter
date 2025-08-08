import time
import logging
from prometheus_client import start_http_server
from clients.obs import OBSClient
from collectors.obs import OBSCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Main function to start the exporter."""
    logging.info("Starting HCS exporter...")
    
    obs_client = OBSClient().get_client()
    obs_collector = OBSCollector(obs_client)
    obs_collector.register()

    start_http_server(8000)
    logging.info("Exporter started on port 8000")

    while True:
        time.sleep(60)

if __name__ == '__main__':
    main()