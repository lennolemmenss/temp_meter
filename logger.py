# save as logger.py
import csv, os, serial, time, datetime, pathlib

PORT      = os.getenv("SERIAL_PORT", "/dev/ttyACM0")  # override at runtime if needed
BAUD      = int(os.getenv("SERIAL_BAUD", "9600"))
CSV_PATH  = pathlib.Path(os.getenv("CSV_PATH", "/data/measurements.csv"))

ser = serial.serial_for_url(PORT, baudrate=BAUD, timeout=5)


# Create file with header once
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
new_file = not CSV_PATH.exists()
with CSV_PATH.open("a", newline="") as f:
    writer = csv.writer(f)
    if new_file:
        writer.writerow(["timestamp_iso", "temperature_C", "humidity_%"])
    while True:
        line = ser.readline().decode().strip()         # e.g. TEMP:23.4;HUM:48.9
        if not line:                                   # skip blanks / timeouts
            continue
        try:
            parts = {kv.split(":")[0]: kv.split(":")[1]
                     for kv in line.split(";")}        # {'TEMP':'23.4', 'HUM':'48.9'}
            writer.writerow([
                datetime.datetime.utcnow().isoformat(timespec="seconds"),
                parts["TEMP"],
                parts["HUM"]
            ])
            f.flush()                                  # flush so data survives container crash
            print("logged:", line)
        except Exception as e:
            print("parse-error:", line, e)
