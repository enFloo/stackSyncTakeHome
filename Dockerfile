FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      git g++ make pkg-config protobuf-compiler libprotobuf-dev \
      libnl-route-3-dev flex bison tini && \
    git clone https://github.com/google/nsjail.git /tmp/nsjail && \
    make -C /tmp/nsjail && mv /tmp/nsjail/nsjail /usr/sbin/nsjail && \
    rm -rf /var/lib/apt/lists/* /tmp/nsjail

RUN pip install --no-cache-dir flask pandas numpy

WORKDIR /app
COPY main.py nsjail.config ./

ENV PYTHONUNBUFFERED=1 PORT=8080
EXPOSE 8080
ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["python","main.py"]
