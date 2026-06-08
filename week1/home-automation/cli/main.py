import argparse
import requests

BASE_URL = "http://127.0.0.1:8000"


def send_event(event_type):
    response = requests.post(
        f"{BASE_URL}/event",
        json={"event": event_type},
        timeout=5
    )
    print(response.json())


def get_status():
    response = requests.get(f"{BASE_URL}/state", timeout=5)
    print(response.json())


def control_light(state):
    event = "motion_detected" if state == "on" else "no_motion"
    send_event(event)


def main():
    parser = argparse.ArgumentParser(description="Home Automation CLI")
    subparsers = parser.add_subparsers(dest="command")

    # event
    event_parser = subparsers.add_parser("event")
    event_parser.add_argument("type")

    # status
    subparsers.add_parser("status")

    # light
    light_parser = subparsers.add_parser("light")
    light_parser.add_argument("state", choices=["on", "off"])

    args = parser.parse_args()

    if args.command == "event":
        send_event(args.type)

    elif args.command == "status":
        get_status()

    elif args.command == "light":
        control_light(args.state)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()