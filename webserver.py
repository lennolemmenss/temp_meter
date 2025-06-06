import csv
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pathlib import Path
from statistics import mean
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

CSV_PATH = Path("csv_out/measurements.csv")

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")
    last_line = None

    try:
        while True:
            await asyncio.sleep(2)

            if not CSV_PATH.exists():
                print("CSV file does not exist")
                continue

            with CSV_PATH.open("r") as f:
                lines = list(csv.reader(f))

            print(f"CSV has {len(lines)} lines")

            if len(lines) < 2:
                print("CSV does not have enough data")
                continue

            headers, *rows = lines

            # Filter out accidental headers re-appended to CSV
            data_rows = [r for r in rows if r[1] != "temperature_C" and r[2] != "humidity_%"]

            if not data_rows:
                print("No valid data rows after filtering")
                continue

            latest = data_rows[-1]

            if latest == last_line:
                continue

            last_line = latest

            print("Latest valid row:", latest)

            temps = [float(r[1]) for r in data_rows]
            hums = [float(r[2]) for r in data_rows]

            stats = {
                "timestamp": latest[0],
                "temperature": float(latest[1]),
                "humidity": float(latest[2]),
                "avg_temp": round(mean(temps), 2),
                "min_temp": round(min(temps), 2),
                "max_temp": round(max(temps), 2),
                "avg_hum": round(mean(hums), 2),
                "min_hum": round(min(hums), 2),
                "max_hum": round(max(hums), 2)
            }


            print("Sending stats:", stats)
            await websocket.send_json(stats)

    except Exception as e:
        print("WebSocket error:", e)
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
