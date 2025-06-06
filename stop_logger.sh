#!/bin/bash

echo "Stopping Docker Compose..."
docker compose down

echo "Stopping socat process..."
sudo pkill socat

echo "All services stopped."