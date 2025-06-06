import csv
import os
import serial
import time
import datetime
import pathlib
from zoneinfo import ZoneInfo

PORT = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
BAUD = int(os.getenv("SERIAL_BAUD", "9600"))
CSV_PATH = pathlib.Path(os.getenv("CSV_PATH", "/data/measurements.csv"))

ser = serial.serial_for_url(PORT, baudrate=BAUD, timeout=5)

CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

brussels_tz = ZoneInfo("Europe/Brussels")

with CSV_PATH.open("a+", newline="") as f:
    f.seek(0)
    is_empty = f.tell() == 0 or f.read(1) == ''
    f.seek(0, 2)  # move back to end of file for appending

    writer = csv.writer(f)
    if is_empty:
        writer.writerow(["timestamp_brussels", "temperature_C", "humidity_%"])

    while True:
        line = ser.readline().decode().strip()
        if not line:
            continue
        try:
            parts = {kv.split(":")[0]: kv.split(":")[1] for kv in line.split(";")}
            writer.writerow([
                datetime.datetime.now(brussels_tz).isoformat(timespec="seconds"),
                parts["TEMP"],
                parts["HUM"]
            ])
            f.flush()
            print("logged:", line)
        except Exception as e:
            print("parse-error:", line, e)
