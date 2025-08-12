# HCS Exporter

## Overview

This is a Prometheus exporter for Huawei Cloud services. It collects metrics from various HCS services and pushes them to a Prometheus Pushgateway.

Currently, the exporter supports the following services:

*   Object Storage Service (OBS)

## Architecture

The exporter runs as a standalone service that periodically collects metrics from HCS services and pushes them to a configured Pushgateway. It also provides a health check endpoint to monitor its status.

## Configuration

The exporter is configured using the `conf/config.yml` file. Here is an example configuration:

```yaml
exporter:
  port: 8100
  health_check_path: /healthz

pushgateway:
  address: "localhost:9091"
  job_name: "hcs-exporter"
  push_interval: 60

collectors:
  obs:
    enabled: true
    rate_limit_sleep: 10
```

**Configuration Options:**

*   `exporter.port`: The port for the health check endpoint.
*   `exporter.health_check_path`: The path for the health check endpoint.
*   `pushgateway.address`: The address of the Prometheus Pushgateway.
*   `pushgateway.job_name`: The job name to use when pushing metrics.
*   `pushgateway.push_interval`: The interval in seconds at which to push metrics.
*   `collectors.obs.enabled`: Set to `true` to enable the OBS collector.
*   `collectors.obs.rate_limit_sleep`: The time in seconds to sleep between API calls for each bucket to avoid rate limiting.

## Getting Started

### Prerequisites

*   Docker
*   A running Prometheus Pushgateway instance.
*   Huawei Cloud Access Key ID and Secret Access Key.

### Build and Run

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/hcs-exporter.git
    cd hcs-exporter
    ```

2.  **Configure the exporter:**

    Create a `conf/config.yml` file with your desired configuration.

3.  **Build the Docker image:**

    ```bash
    docker build -t hcs-exporter .
    ```

4.  **Run the exporter:**

    ```bash
    docker run -d --name hcs-exporter \
      -v $(pwd)/conf:/app/conf \
      -e AccessKeyID=<YOUR_ACCESS_KEY_ID> \
      -e SecretAccessKey=<YOUR_SECRET_ACCESS_KEY> \
      hcs-exporter
    ```

## Health Check

The exporter provides a health check endpoint at `http://localhost:8100/healthz` by default. You can use this to monitor the status of the exporter.

## Exported Metrics

### OBS

*   `hcs_obs_size{bucket_name, bucket_owner, location}`: OBS bucket size in bytes.
*   `hcs_obs_quota{bucket_name, bucket_owner, location}`: OBS bucket quota in bytes.
*   `hcs_obs_object_count{bucket_name, bucket_owner, location}`: Number of objects in an OBS bucket.