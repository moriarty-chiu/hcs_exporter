FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV AccessKeyID=""
ENV SecretAccessKey=""
ENV OBS_SERVER="https://obs.cn-north-4.myhuaweicloud.com"

CMD ["python", "obs_exporter.py"]
