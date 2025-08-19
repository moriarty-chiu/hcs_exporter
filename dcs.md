### 通过token接口获取token
```shell
curl -k -X POST -H "Content-Type: application/json" -d '{"auth": {"identity": {"method": ["password"], "password": {"user": {"domain": {"name": "domain"}, "name": "username", "password": "password"}}}, "scope": {"domain": {"name": "domain"}}}}' $iam_endpoint/v3/auth/tokens -v
```

### 从token接口获取token
token需要从header中获取, key为X-Subject-Token

### 获取dcs数据
```shell
curl -k -X POST -H "Content-Type: application/json" -d '{"dimensions": [{"field": "uuid", "index": 1}, {"field": "name", "index": 2}], "metrics":[{"field": "count1", "aggType": "sum"}]}' $oc_endpoint/rest/analysis/v2/datasets/stat-namespace-dcs
```

### 获取返回的结果构造prometheus metrics
hcs_dcs_info {uuid, name, ...} count1