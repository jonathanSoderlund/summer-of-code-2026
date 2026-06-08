from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from backend.automation.engine import AutomationEngine
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- State Storage ---
STATE = {
    "events": [],
    "devices": {
        "light": "off",
        "alarm": "off"
    },
    "logs": []
}

# --- Init engine ---
engine = AutomationEngine(STATE)

# --- Models ---
class Event(BaseModel):
    event: str
    value: str | None = None


# --- API ---
@app.post("/event")
async def receive_event(event: Event):

    entry = {
        "event": event.event,
        "value": event.value,
        "time": datetime.now().isoformat()
    }

    # 1. spara event
    STATE["events"].append(entry)

    # 2. kör automation 
    await engine.handle_event(entry)

    # 3. logga state efter automation
    STATE["logs"].append({
        "event": entry,
        "devices_after": STATE["devices"].copy(),
        "time": datetime.now().isoformat()
    })

    return {
        "status": "ok",
        "state": STATE
    }

# HTML dashboard route
@app.get("/state")
def get_state():
    return STATE

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Home Automation Dashboard</title>
    <style>
        body { font-family: Arial; background: #111; color: white; padding: 20px; }
        .box { padding: 10px; margin: 10px; border: 1px solid #333; border-radius: 8px; }
        .on { color: lime; }
        .off { color: red; }
    </style>
</head>
<body>

<h1>🏠 Smart Home Dashboard</h1>

<div class="box">
    <h2>Devices</h2>
    <div>💡 Light: <span id="light">loading...</span></div>
    <div>🚨 Alarm: <span id="alarm">loading...</span></div>
</div>

<div class="box">
    <h2>Events</h2>
    <pre id="events"></pre>
</div>

<div class="box">
    <h2>Logs</h2>
    <pre id="logs"></pre>
</div>

<script>
async function update() {
    const res = await fetch("/state");
    const data = await res.json();

    document.getElementById("light").innerText = data.devices.light;
    document.getElementById("alarm").innerText = data.devices.alarm;

    document.getElementById("events").innerText =
        JSON.stringify(data.events.slice(-5), null, 2);

    document.getElementById("logs").innerText =
        JSON.stringify(data.logs.slice(-10), null, 2);
}

setInterval(update, 1000);
update();
</script>

</body>
</html>
"""


# --- Debug Endpoint ---
@app.get("/debug")
def debug():
    return {
        "events": STATE["events"][-10:],
        "devices": STATE["devices"],
        "logs": STATE["logs"][-10:]
    }