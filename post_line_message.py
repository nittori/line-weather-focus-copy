import sys
import requests
import os
import json
import get_weather_focus

def line_message(message):
    access_token = os.environ.get("LINE_TOKEN")
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }
    payload = {
        'message': message,
    }
    response = requests.post(url, headers=headers, params=payload)
    res = json.loads(response.text)
    print(res)
    return True

def main():
    text = get_weather_focus.get_weather_focus()
    print(line_message(text))

if __name__ == "__main__":
    main()
    