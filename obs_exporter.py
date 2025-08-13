import os
import logging
import time
import yaml
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from obs import ObsClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(path):
    """Load configuration from a YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_obs_client():
    """Create and return an OBS client using credentials from environment variables."""
    ak = os.getenv("AccessKeyID")
    sk = os.getenv("SecretAccessKey")
    server = os.getenv("OBS_SERVER", "https://obs.cn-north-4.myhuaweicloud.com")
    if not ak or not sk:
        logger.error("AccessKeyID and SecretAccessKey environment variables must be set.")
        raise ValueError("AccessKeyID and SecretAccessKey environment variables must be set.")
    return ObsClient(access_key_id=ak, secret_access_key=sk, server=server)

def collect_obs_metrics(client, registry, rate_limit_sleep=10):
    """Collect OBS metrics and register them with the provided registry."""
    hcs_obs_size = Gauge('hcs_obs_size', 'OBS bucket size', ['bucket_name', 'bucket_owner', 'location'], registry=registry)
    hcs_obs_quota = Gauge('hcs_obs_quota', 'OBS bucket quota', ['bucket_name', 'bucket_owner', 'location'], registry=registry)
    hcs_obs_object_count = Gauge('hcs_obs_object_count', 'OBS bucket object count', ['bucket_name', 'bucket_owner', 'location'], registry=registry)

    logger.info("Collecting OBS metrics...")
    resp = client.listBuckets(True)
    if resp.status < 300:
        for bucket in resp.body.buckets:
            bucket_name = bucket.name
            location = bucket.location
            owner_name = resp.body.owner.owner_name

            storage_info_resp = client.getBucketStorageInfo(bucket_name)
            quota_resp = client.getBucketQuota(bucket_name)

            if storage_info_resp.status < 300 and quota_resp.status < 300:
                bucket_size = storage_info_resp.body.size
                object_count = storage_info_resp.body.objectNumber
                quota = quota_resp.body.quota

                hcs_obs_size.labels(
                    bucket_name=bucket_name, bucket_owner=owner_name, location=location
                ).set(bucket_size)
                hcs_obs_quota.labels(
                    bucket_name=bucket_name, bucket_owner=owner_name, location=location
                ).set(quota)
                hcs_obs_object_count.labels(
                    bucket_name=bucket_name, bucket_owner=owner_name, location=location
                ).set(object_count)
                logger.info(f"Successfully collected metrics for bucket: {bucket_name}")
            else:
                if storage_info_resp.status >= 300:
                    logger.error(f"Failed to get storage info for bucket {bucket_name}: {storage_info_resp.errorCode}: {storage_info_resp.errorMessage}")
                if quota_resp.status >= 300:
                    logger.error(f"Failed to get quota for bucket {bucket_name}: {quota_resp.errorCode}: {quota_resp.errorMessage}")
            
            time.sleep(rate_limit_sleep)
    else:
        logger.error(f"Failed to list buckets: {resp.errorCode}: {resp.errorMessage}")

def main():
    """Main function to collect and push metrics.

    This script collects OBS metrics and pushes them to a Prometheus Pushgateway.
    """
    logging.info("Starting OBS metrics collection script...")

    config_path = os.getenv('CONFIG_FILE_PATH', 'conf/config.yml')
    config = load_config(config_path)
    pushgateway_address = config['pushgateway']['address']
    job_name = config['pushgateway']['job_name']
    rate_limit_sleep = config['collectors']['obs'].get('rate_limit_sleep', 10)

    try:
        obs_client = get_obs_client()
    except ValueError as e:
        logging.error(f"Failed to create OBS client: {e}")
        return

    registry = CollectorRegistry()
    
    collect_obs_metrics(obs_client, registry, rate_limit_sleep)

    try:
        push_to_gateway(pushgateway_address, job=job_name, registry=registry)
        logging.info("Metrics pushed to Pushgateway.")
    except Exception as e:
        logging.error(f"Failed to push metrics to Pushgateway: {e}")

if __name__ == '__main__':
    main()
