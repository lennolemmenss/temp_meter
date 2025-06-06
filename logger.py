import csv, os, serial, time, datetime, pathlib
from zoneinfo import ZoneInfo

PORT      = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
BAUD      = int(os.getenv("SERIAL_BAUD", "9600"))
CSV_PATH  = pathlib.Path(os.getenv("CSV_PATH", "/data/measurements.csv"))

ser = serial.serial_for_url(PORT, baudrate=BAUD, timeout=5)

CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
new_file = not CSV_PATH.exists()

brussels_tz = ZoneInfo("Europe/Brussels")

with CSV_PATH.open("a", newline="") as f:
    writer = csv.writer(f)
    if new_file:
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
