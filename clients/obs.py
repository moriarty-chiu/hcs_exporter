import os
import logging
from obs import ObsClient
from .base import BaseClient

logger = logging.getLogger(__name__)

class OBSClient(BaseClient):
    def __init__(self):
        super().__init__()

    def get_client(self):
        ak = os.getenv("AccessKeyID")
        sk = os.getenv("SecretAccessKey")
        server = os.getenv("OBS_SERVER", "https://obs.cn-north-4.myhuaweicloud.com")
        if not ak or not sk:
            logger.error("AccessKeyID and SecretAccessKey environment variables must be set.")
            raise ValueError("AccessKeyID and SecretAccessKey environment variables must be set.")
        return ObsClient(access_key_id=ak, secret_access_key=sk, server=server)
