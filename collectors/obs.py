import logging
from prometheus_client import Gauge, REGISTRY
from .base import BaseCollector

logger = logging.getLogger(__name__)

class OBSCollector(BaseCollector):
    def __init__(self, client):
        super().__init__(client)
        self.hcs_obs_size = Gauge('hcs_obs_size', 'OBS bucket size', ['bucket_name', 'bucket_owner', 'location'])
        self.hcs_obs_quota = Gauge('hcs_obs_quota', 'OBS bucket quota', ['bucket_name', 'bucket_owner', 'location'])
        self.hcs_obs_object_count = Gauge('hcs_obs_object_count', 'OBS bucket object count', ['bucket_name', 'bucket_owner', 'location'])

    def collect(self):
        REGISTRY.register(self.hcs_obs_size)
        REGISTRY.register(self.hcs_obs_quota)
        REGISTRY.register(self.hcs_obs_object_count)

        logger.info("Collecting OBS metrics...")
        resp = self.client.listBuckets(True)
        if resp.status < 300:
            for bucket in resp.body.buckets:
                bucket_name = bucket.name
                location = bucket.location
                owner_name = resp.body.owner.owner_name

                storage_info_resp = self.client.getBucketStorageInfo(bucket_name)
                quota_resp = self.client.getBucketQuota(bucket_name)

                if storage_info_resp.status < 300 and quota_resp.status < 300:
                    bucket_size = storage_info_resp.body.size
                    object_count = storage_info_resp.body.objectNumber
                    quota = quota_resp.body.quota

                    self.hcs_obs_size.labels(
                        bucket_name=bucket_name,
                        bucket_owner=owner_name,
                        location=location
                    ).set(bucket_size)
                    self.hcs_obs_quota.labels(
                        bucket_name=bucket_name,
                        bucket_owner=owner_name,
                        location=location
                    ).set(quota)
                    self.hcs_obs_object_count.labels(
                        bucket_name=bucket_name,
                        bucket_owner=owner_name,
                        location=location
                    ).set(object_count)
                    logger.info(f"Successfully collected metrics for bucket: {bucket_name}")
                else:
                    if storage_info_resp.status >= 300:
                        logger.error(f"Failed to get storage info for bucket {bucket_name}: {storage_info_resp.errorCode}: {storage_info_resp.errorMessage}")
                    if quota_resp.status >= 300:
                        logger.error(f"Failed to get quota for bucket {bucket_name}: {quota_resp.errorCode}: {quota_resp.errorMessage}")
        else:
            logger.error(f"Failed to list buckets: {resp.errorCode}: {resp.errorMessage}")

        yield from self.hcs_obs_size.collect()
        yield from self.hcs_obs_quota.collect()
        yield from self.hcs_obs_object_count.collect()

        REGISTRY.unregister(self.hcs_obs_size)
        REGISTRY.unregister(self.hcs_obs_quota)
        REGISTRY.unregister(self.hcs_obs_object_count)