from selenium import webdriver
from selenium.webdriver import ActionChains
# import time
from time import sleep

# dr = webdriver.Chrome()
# dr.get("https://www.bilibili.com")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
dr = webdriver.Chrome(options=chrome_options)
dr.get("https://www.bilibili.com")

sreach_windows = dr.current_window_handle
# 点击登录，浏览器切换到另一个窗口
dr.find_element_by_class_name("name").click()
sleep(3)# 前一个窗口无用，3s后关闭
dr.close()
# 获取当前所有窗口
all_window = dr.window_handles
# 进入登录界面
for handle in all_window:
    if handle != sreach_windows:
        dr.switch_to.window(handle)
        print('进入登录界面!')
        dr.find_element_by_id("login-username").send_keys('15766080695')
        dr.find_element_by_id('login-passwd').send_keys('Zzlde500')
        dr.find_element_by_xpath('//*[@id="geetest-wrap"]/div/div[5]/a[1]').click()
        sleep(10)

# 定位搜索框
dr.find_element_by_xpath('//*[@id="nav_searchform"]/input').send_keys('Nintendo switch')
dr.find_element_by_class_name("nav-search-btn").click()
sleep(3)
dr.close()
# 切换界面
all_window = dr.window_handles
# 进入视频界面
for handle in all_window:
    if handle != sreach_windows:
        dr.switch_to.window(handle)


sleep(5)# 前一个窗口无用，5s后关闭




