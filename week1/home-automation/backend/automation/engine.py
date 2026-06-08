from .rules import Rule
from datetime import datetime
import asyncio
import time


class AutomationEngine:
    def __init__(self, state):
        self.state = state
        self.rules = []
        self.off_task = None
        self.register_rules()

    # --------------------
    # RULES
    # --------------------
    def register_rules(self):
        self.rules = [

            Rule(
                name="Turn on light when motion detected",
                condition=lambda e: e["event"] == "motion_detected",
                action=lambda s: self.turn_on_with_timer(),
                priority=5,
                cooldown=2
            ),

            Rule(
                name="Turn off light no motion",
                condition=lambda e: e["event"] == "no_motion",
                action=lambda s: self.light_off(),
                priority=5,
                cooldown=1
            ),

            Rule(
                name="Night motion alarm boost",
                condition=lambda e: e["event"] == "motion_detected" and self.is_night(),
                action=lambda s: self.trigger_alarm(),
                priority=10,
                cooldown=5
            ),
        ]

    # --------------------
    # EVENT HANDLER
    # --------------------
    async def handle_event(self, event: dict):
        self.state.setdefault("logs", [])

        now = time.time()

        for rule in sorted(self.rules, key=lambda r: r.priority, reverse=True):

            if not rule.condition(event):
                continue

            if now - rule.last_triggered < rule.cooldown:
                continue

            rule.last_triggered = now
            rule.action(self.state)

            self.state["logs"].append({
                "rule": rule.name,
                "event": event,
                "devices_after": self.state["devices"].copy(),
                "time": datetime.now().isoformat()
            })

    # --------------------
    # ACTIONS
    # --------------------
    def turn_on_with_timer(self):
        self.state["devices"]["light"] = "on"

        if self.off_task:
            self.off_task.cancel()

        self.off_task = asyncio.create_task(self.schedule_light_off(10))

    def light_off(self):
        self.state["devices"]["light"] = "off"

        if self.off_task:
            self.off_task.cancel()
            self.off_task = None

    def trigger_alarm(self):
        self.state["devices"]["alarm"] = "on"

        # alarm auto-off after 5 sec
        asyncio.create_task(self.auto_off_alarm())

    async def auto_off_alarm(self):
        await asyncio.sleep(5)
        self.state["devices"]["alarm"] = "off"

        self.state["logs"].append({
            "rule": "auto_alarm_off",
            "event": {"event": "alarm_timeout"},
            "devices_after": self.state["devices"].copy(),
            "time": datetime.now().isoformat()
        })

    # --------------------
    # TIMER
    # --------------------
    async def schedule_light_off(self, delay: int):
        try:
            await asyncio.sleep(delay)

            self.state["devices"]["light"] = "off"

            self.state["logs"].append({
                "rule": "auto_off_timer",
                "event": {"event": "timer_expired"},
                "devices_after": self.state["devices"].copy(),
                "time": datetime.now().isoformat()
            })

        except asyncio.CancelledError:
            pass

    # --------------------
    # UTIL
    # --------------------
    def is_night(self):
        hour = datetime.now().hour
        return hour >= 22 or hour < 6