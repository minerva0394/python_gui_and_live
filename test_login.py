import requests, os, re, time
# import r-qrcode

url_getinfo = "http://passport.bilibili.com/qrcode/getLoginUrl"
url_login = "http://passport.bilibili.com/qrcode/getLoginInfo"
user_url = "http://api.bilibili.com/x/web-interface/nav"


def main1():
    # 获取二维码
    req1 = requests.get(url=url_getinfo)
    req1.encoding = 'utf-8'
    ans = re.search(r'http.+,', req1.text, re.I).group()
    img_url = ans.replace(',', '').replace('"', '')
    img = qrcode.make(img_url)
    img.save("test.jpg")
    os.system(".\\test.jpg")
    print(img_url)
    f = open("img_url.txt", "w")
    f.write(img_url)
    f.close()


def main2():
    # 登录并保存cookie
    f = open("img_url.txt", "r")
    oau = f.readline()
    f.close()
    oau = re.search(r"oauthKey=.+", oau, re.I).group()
    print(oau)
    os.system(("curl {} -d \"{}\" -c cookie.txt".format(url_login, oau)))


def main3():
    # 查看个人信息
    os.system("curl -b cookie.txt {}".format(user_url))
# main1()
# time.sleep(15)
# main2()
# main3()
