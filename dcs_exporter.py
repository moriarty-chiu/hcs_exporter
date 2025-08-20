import os
import logging
import json
import requests
import yaml
import urllib3
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# 禁用InsecureRequestWarning警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(path):
    """Load configuration from a YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_iam_token(iam_endpoint, domain_name, username, password):
    """通过IAM获取token"""
    url = f"{iam_endpoint}/v3/auth/tokens"
    
    payload = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "domain": {
                            "name": domain_name
                        },
                        "name": username,
                        "password": password
                    }
                }
            },
            "scope": {
                "domain": {
                    "name": domain_name
                }
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        response.raise_for_status()
        
        # 从header中获取token
        token = response.headers.get('X-Subject-Token')
        if not token:
            logger.error("Failed to get token from response headers")
            return None
            
        logger.info("Successfully obtained IAM token")
        return token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get IAM token: {e}")
        return None

def collect_dcs_metrics(token, oc_endpoint, registry):
    """收集DCS指标并注册到Prometheus"""
    # 定义Prometheus指标
    hcs_dcs_info = Gauge('hcs_dcs_info', 'DCS instance info', ['uuid', 'name'], registry=registry)
    
    url = f"{oc_endpoint}/rest/analysis/v2/datasets/stat-namespace-dcs"
    
    payload = {
        "dimensions": [
            {"field": "uuid", "index": 1},
            {"field": "name", "index": 2}
        ],
        "metrics": [
            {"field": "count1", "aggType": "sum"}
        ]
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': token
    }
    
    try:
        logger.info("Collecting DCS metrics...")
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # 解析并设置指标
        # 注意：根据实际API返回结构调整解析逻辑
        if 'data' in data and isinstance(data['data'], list):
            for item in data['data']:
                uuid = item.get('uuid', 'unknown')
                name = item.get('name', 'unknown')
                count1 = item.get('count1', 0)
                
                hcs_dcs_info.labels(uuid=uuid, name=name).set(count1)
                logger.info(f"Collected metrics for DCS instance: {name} ({uuid})")
        else:
            logger.warning("Unexpected data format in DCS response")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to collect DCS metrics: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse DCS metrics response: {e}")

def main():
    """Main function to collect and push DCS metrics."""
    logging.info("Starting DCS metrics collection script...")
    
    # 从环境变量获取配置
    config_path = os.getenv('CONFIG_FILE_PATH', 'conf/config.yml')
    config = load_config(config_path)
    
    # 获取Pushgateway配置
    pushgateway_address = config.get('pushgateway', {}).get('address', 'localhost:9091')
    job_name = config.get('pushgateway', {}).get('job_name', 'hcs-dcs-exporter')
    
    # 获取IAM和OC配置
    iam_endpoint = os.getenv('IAM_ENDPOINT')
    oc_endpoint = os.getenv('OC_ENDPOINT')
    domain_name = os.getenv('DOMAIN_NAME')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    
    # 检查必要配置
    if not all([iam_endpoint, oc_endpoint, domain_name, username, password]):
        logger.error("Missing required environment variables: IAM_ENDPOINT, OC_ENDPOINT, DOMAIN_NAME, USERNAME, PASSWORD")
        return
    
    # 获取IAM token
    token = get_iam_token(iam_endpoint, domain_name, username, password)
    if not token:
        logger.error("Failed to obtain IAM token, exiting.")
        return
    
    # 创建Prometheus注册表并收集指标
    registry = CollectorRegistry()
    collect_dcs_metrics(token, oc_endpoint, registry)
    
    # 推送指标到Pushgateway
    try:
        push_to_gateway(pushgateway_address, job=job_name, registry=registry)
        logging.info("DCS metrics pushed to Pushgateway.")
    except Exception as e:
        logging.error(f"Failed to push DCS metrics to Pushgateway: {e}")

if __name__ == '__main__':
    main()