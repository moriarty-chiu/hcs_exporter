# HCS Exporter

## Overview

This is a Prometheus exporter for Huawei Cloud services. It collects metrics from various HCS services and exposes them in a format that Prometheus can scrape.

Currently, the exporter supports the following services:

*   Object Storage Service (OBS)

## Getting Started

### Prerequisites

*   Docker
*   make
*   Huawei Cloud Access Key ID and Secret AccessKey

### Build and Run

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/hcs-exporter.git
    cd hcs-exporter
    ```

2.  **Build the Docker image:**

    ```bash
    make build
    ```

3.  **Run the exporter:**

    ```bash
    AccessKeyID=<YOUR_ACCESS_KEY_ID> SecretAccessKey=<YOUR_SECRET_ACCESS_KEY> make run
    ```

    The exporter will be available at `http://localhost:8000`.

### Stop and Clean Up

*   **Stop the container:**

    ```bash
    make stop
    ```

*   **Remove the Docker image:**

    ```bash
    make clear
    ```

## Configuration

The exporter is configured using environment variables:

| Variable          | Description                                     | Default                                       |
| ----------------- | ----------------------------------------------- | --------------------------------------------- |
| `AccessKeyID`     | Your Huawei Cloud Access Key ID.                |                                               |
| `SecretAccessKey` | Your Huawei Cloud Secret Access Key.            |                                               |
| `OBS_SERVER`      | The OBS endpoint.                               | `https://obs.cn-north-4.myhuaweicloud.com`      |

## Exported Metrics

### OBS

*   `hcs_obs_info{bucket_name, location, owner_id, owner_name, bucket_size, object_count, quota}`: Information about an OBS bucket.
    *   `bucket_name`: The name of the bucket.
    *   `location`: The location of the bucket.
    *   `owner_id`: The ID of the bucket owner.
    *   `owner_name`: The name of the bucket owner.
    *   `bucket_size`: The size of the bucket in bytes.
    *   `object_count`: The number of objects in the bucket.
    *   `quota`: The quota of the bucket in bytes.
