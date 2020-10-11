import requests
import time


def bilibli_notify():
    status = False
    number = input("请输入需要监听的B站直播房间号:")
    url = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getRoomPlayInfo?room_id='
    bilibili_url = url + number
    print(bilibili_url)
    use_proxy = False  # 你访问土鳖要梯子么, 要就改成 True
    proxy_url = 'socks5://user:pass@host:port'  # 要梯子的情况下 socks5://[用户名]:[密码]@[地址]:[端口] 形式的梯子入口。一般人可能是 socks5://127.0.0.1:[端口]
    while True:
        if use_proxy:
            resp = requests.get(bilibili_url, proxies=dict(http=proxy_url, https=proxy_url))
        else:
            resp = requests.get(bilibili_url)
            resp = resp.content.decode('utf-8')
            # print(resp)
            bilibili_result = '"live_status":1' in resp and '"live_status":0' not in resp  # live_status为1就是开播，0就是没开播
        if bilibili_result:
            if status is False:
                print("开播了，如要退出，请按Ctrl+C")  # 此处可以塞你需要的其他通知代码
                status = True
        else:
            status = False
            print("未开播，如要停止，请按Ctrl+C")
            time.sleep(6)


if __name__ == '__main__':
    bilibli_notify()
