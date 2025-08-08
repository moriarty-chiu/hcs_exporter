import logging
from prometheus_client import Gauge
from .base import BaseCollector

logger = logging.getLogger(__name__)

class OBSCollector(BaseCollector):
    def __init__(self, client):
        super().__init__(client)
        self.obs_info = Gauge('hcs_obs_info', 'OBS bucket information', ['bucket_name', 'location', 'owner_id', 'owner_name', 'bucket_size', 'object_count', 'quota'])

    def collect(self):
        logger.info("Collecting OBS metrics...")
        resp = self.client.listBuckets(True)
        if resp.status < 300:
            for bucket in resp.body.buckets:
                bucket_name = bucket.name
                location = bucket.location
                owner_id = resp.body.owner.owner_id
                owner_name = resp.body.owner.owner_name

                storage_info_resp = self.client.getBucketStorageInfo(bucket_name)
                quota_resp = self.client.getBucketQuota(bucket_name)

                if storage_info_resp.status < 300 and quota_resp.status < 300:
                    bucket_size = storage_info_resp.body.size
                    object_count = storage_info_resp.body.objectNumber
                    quota = quota_resp.body.quota

                    self.obs_info.labels(
                        bucket_name=bucket_name, 
                        location=location, 
                        owner_id=owner_id, 
                        owner_name=owner_name, 
                        bucket_size=bucket_size, 
                        object_count=object_count, 
                        quota=quota
                    ).set(1)
                    logger.info(f"Successfully collected metrics for bucket: {bucket_name}")
                else:
                    if storage_info_resp.status >= 300:
                        logger.error(f"Failed to get storage info for bucket {bucket_name}: {storage_info_resp.errorCode}: {storage_info_resp.errorMessage}")
                    if quota_resp.status >= 300:
                        logger.error(f"Failed to get quota for bucket {bucket_name}: {quota_resp.errorCode}: {quota_resp.errorMessage}")
        else:
            logger.error(f"Failed to list buckets: {resp.errorCode}: {resp.errorMessage}")