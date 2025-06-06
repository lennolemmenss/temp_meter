FROM python:3.12-slim

WORKDIR /app
COPY logger.py .

RUN pip install pyserial

# default values can be overridden with -e at runtime
ENV SERIAL_PORT=/dev/ttyACM0 \
    SERIAL_BAUD=9600 \
    CSV_PATH=/data/measurements.csv

CMD ["python", "/app/logger.py"]
