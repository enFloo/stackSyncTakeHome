FROM python:3.11-slim

# Install build tools and build nsjail
RUN apt-get update && \
    apt-get install -y git g++ make pkg-config protobuf-compiler libprotobuf-dev libnl-route-3-dev flex bison && \
    git clone https://github.com/google/nsjail.git && \
    cd nsjail && make && cp nsjail /usr/sbin/ && \
    cd .. && rm -rf nsjail && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Install Python packages
RUN pip install --no-cache-dir flask pandas numpy

WORKDIR /app
COPY main.py .

EXPOSE 8080

CMD ["python", "main.py"]