import json
import os
import requests

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")) as f:
    config = json.load(f)


def solve_turnstile():
    response = requests.post(
        "https://api.uncaptcha.io/v1/task/execute",
        headers={"X-Api-Key": config["uncaptcha_key"], "Content-Type": "application/json"},
        json={
            "task_type": "turnstile",
            "task_data": {
                "url": "https://guns.lol/",
                "sitekey": "0x4AAAAAAAgU7T2niLQD-TLm",
            },
        },
    )

    data = response.json()
    if not data.get("success"):
        raise Exception(f"Error occurred while solving WAF: {data.get('message')}")
    return data["data"]["solution"]["token"]


