FROM python:3.10-slim

WORKDIR /gatherer
RUN apt-get update && apt-get install -y \
    tshark \
    iproute2 \
    util-linux \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]