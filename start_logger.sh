#!/bin/bash

# Path to Arduino serial port
SERIAL_PORT="/dev/cu.usbserial-0001"
SOCAT_LOG="socat.log"

echo "Starting socat bridge for Arduino on ${SERIAL_PORT}..."
sudo nohup socat -d -d TCP-LISTEN:7000,reuseaddr,fork FILE:$SERIAL_PORT,raw,echo=0 > $SOCAT_LOG 2>&1 &

SOCAT_PID=$!
echo "socat started with PID $SOCAT_PID (logging to $SOCAT_LOG)"

# Wait briefly to ensure socat is ready
sleep 5

echo "Starting Docker Compose..."
docker compose up -d --build

echo "Docker services started. View logs with: docker logs -f temp_hum_logger"
