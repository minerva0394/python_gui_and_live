import requests
data = requests.get("https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id=139").json()
print(data)
calls = data['data']['room_info']['tags']
print(calls)