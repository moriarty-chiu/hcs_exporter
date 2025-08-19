FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY . .

ENV AccessKeyID=""
ENV SecretAccessKey=""
ENV OBS_SERVER="https://obs.cn-north-4.myhuaweicloud.com"
ENV IAM_ENDPOINT=""
ENV OC_ENDPOINT=""
ENV DOMAIN_NAME=""
ENV USERNAME=""
ENV PASSWORD=""

# 使用统一入口脚本，默认运行OBS exporter
CMD ["python", "entrypoint.py"]
