import time
import logging
import sys
import atexit
from prometheus_client import start_http_server, REGISTRY
from clients.obs import OBSClient
from collectors.obs import OBSCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
    atexit.register(lambda: REGISTRY.unregister(obs_collector))

    start_http_server(8000)
    logging.info("Exporter started on port 8000")

    while True:
        time.sleep(60)

if __name__ == '__main__':
    main()