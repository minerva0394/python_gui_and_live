import tkinter
from tkinter import *
import requests
import threading
import time
import win32api, win32con, win32gui_struct, win32gui
import os


# 自定义的类
class SysTrayIcon(object):
    '''SysTrayIcon类用于显示任务栏图标'''
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]
    FIRST_ID = 5320

    def __init__(s, icon, hover_text, menu_options, on_quit, tk_window=None, default_menu_index=None,
                 window_class_name=None):
        '''
        icon         需要显示的图标文件路径
        hover_text   鼠标停留在图标上方时显示的文字
        menu_options 右键菜单，格式: (('a', None, callback), ('b', None, (('b1', None, callback),)))
        on_quit      传递退出函数，在执行退出时一并运行
        tk_window    传递Tk窗口，s.root，用于单击图标显示窗口
        default_menu_index 不显示的右键菜单序号
        window_class_name  窗口类名
        '''
        s.icon = icon
        s.hover_text = hover_text
        s.on_quit = on_quit
        s.root = tk_window

        menu_options = menu_options + (('退出', None, s.QUIT),)
        s._next_action_id = s.FIRST_ID
        s.menu_actions_by_id = set()
        s.menu_options = s._add_ids_to_menu_options(list(menu_options))
        s.menu_actions_by_id = dict(s.menu_actions_by_id)
        del s._next_action_id

        s.default_menu_index = (default_menu_index or 0)
        s.window_class_name = window_class_name or "SysTrayIconPy"

        message_map = {win32gui.RegisterWindowMessage("TaskbarCreated"): s.restart,
                       win32con.WM_DESTROY: s.destroy,
                       win32con.WM_COMMAND: s.command,
                       win32con.WM_USER + 20: s.notify, }
        # 注册窗口类。
        window_class = win32gui.WNDCLASS()
        window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = s.window_class_name
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = message_map  # 也可以指定wndproc.
        s.classAtom = win32gui.RegisterClass(window_class)
        s.update()

    def update(s):
        '''显示任务栏图标，不用每次都重新创建新的托盘图标'''
        # 创建窗口。
        hinst = win32gui.GetModuleHandle(None)
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        s.hwnd = win32gui.CreateWindow(s.classAtom,
                                       s.window_class_name,
                                       style,
                                       0,
                                       0,
                                       win32con.CW_USEDEFAULT,
                                       win32con.CW_USEDEFAULT,
                                       0,
                                       0,
                                       hinst,
                                       None)
        win32gui.UpdateWindow(s.hwnd)
        s.notify_id = None
        s.refresh_icon()

        win32gui.PumpMessages()

    def _add_ids_to_menu_options(s, menu_options):
        result = []
        for menu_option in menu_options:
            option_text, option_icon, option_action = menu_option
            if callable(option_action) or option_action in s.SPECIAL_ACTIONS:
                s.menu_actions_by_id.add((s._next_action_id, option_action))
                result.append(menu_option + (s._next_action_id,))
            else:
                result.append((option_text,
                               option_icon,
                               s._add_ids_to_menu_options(option_action),
                               s._next_action_id))
            s._next_action_id += 1
        return result

    def refresh_icon(s):
        # 尝试找到自定义图标
        hinst = win32gui.GetModuleHandle(None)
        if os.path.isfile(s.icon):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst,
                                       s.icon,
                                       win32con.IMAGE_ICON,
                                       0,
                                       0,
                                       icon_flags)
        else:  # 找不到图标文件 - 使用默认值
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        if s.notify_id:
            message = win32gui.NIM_MODIFY
        else:
            message = win32gui.NIM_ADD
        s.notify_id = (s.hwnd,
                       0,
                       win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                       win32con.WM_USER + 20,
                       hicon,
                       s.hover_text)
        win32gui.Shell_NotifyIcon(message, s.notify_id)

    def restart(s, hwnd, msg, wparam, lparam):
        s.refresh_icon()

    def destroy(s, hwnd=None, msg=None, wparam=None, lparam=None, exit=1):
        nid = (s.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)  # 终止应用程序。
        if exit and s.on_quit:
            s.on_quit()  # 需要传递自身过去时用 s.on_quit(s)
        else:
            s.root.deiconify()  # 显示tk窗口

    def notify(s, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONDBLCLK:  # 双击左键
            pass
        elif lparam == win32con.WM_RBUTTONUP:  # 右键弹起
            s.show_menu()
        elif lparam == win32con.WM_LBUTTONUP:  # 左键弹起
            s.destroy(exit=0)
        return True
        """
        可能的鼠标事件：
          WM_MOUSEMOVE      #光标经过图标
          WM_LBUTTONDOWN    #左键按下
          WM_LBUTTONUP      #左键弹起
          WM_LBUTTONDBLCLK  #双击左键
          WM_RBUTTONDOWN    #右键按下
          WM_RBUTTONUP      #右键弹起
          WM_RBUTTONDBLCLK  #双击右键
          WM_MBUTTONDOWN    #滚轮按下
          WM_MBUTTONUP      #滚轮弹起
          WM_MBUTTONDBLCLK  #双击滚轮
        """

    def show_menu(s):
        menu = win32gui.CreatePopupMenu()
        s.create_menu(menu, s.menu_options)

        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(s.hwnd)
        win32gui.TrackPopupMenu(menu,
                                win32con.TPM_LEFTALIGN,
                                pos[0],
                                pos[1],
                                0,
                                s.hwnd,
                                None)
        win32gui.PostMessage(s.hwnd, win32con.WM_NULL, 0, 0)

    def create_menu(s, menu, menu_options):
        for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            if option_icon:
                option_icon = s.prep_menu_icon(option_icon)

            if option_id in s.menu_actions_by_id:
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                wID=option_id)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                s.create_menu(submenu, option_action)
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    def prep_menu_icon(s, icon):
        # 加载图标。
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

        hdcBitmap = win32gui.CreateCompatibleDC(0)
        hdcScreen = win32gui.GetDC(0)
        hbm = win32gui.CreateCompatibleBitmap(hdcScreen, ico_x, ico_y)
        hbmOld = win32gui.SelectObject(hdcBitmap, hbm)
        brush = win32gui.GetSysColorBrush(win32con.COLOR_MENU)
        win32gui.FillRect(hdcBitmap, (0, 0, 16, 16), brush)
        win32gui.DrawIconEx(hdcBitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
        win32gui.SelectObject(hdcBitmap, hbmOld)
        win32gui.DeleteDC(hdcBitmap)

        return hbm

    def command(s, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        s.execute_menu_option(id)

    def execute_menu_option(s, id):
        menu_action = s.menu_actions_by_id[id]
        if menu_action == s.QUIT:
            win32gui.DestroyWindow(s.hwnd)
        else:
            menu_action(s)


# 多线程处理
def thread_it(func, *args):
    # 创建线程
    t = threading.Thread(target=func, args=args)
    # 守护
    t.setDaemon(True)
    # 启动
    t.start()
    # 阻塞卡死界面
    # t.join()


# 红灯
def circle_red(canvas, x, y, r):
    id_circle = canvas.create_oval(x - r, y - r, x + r, y + r, fill='red', outline='red', width=0)
    return id_circle


# 绿灯
def circle_green(canvas, x, y, r):
    id_circle = canvas.create_oval(x - r, y - r, x + r, y + r, fill='#00FF7F', outline='#00FF7F', width=0)
    return id_circle


# 不亮灯，默认和背景同色
def circle(canvas, x, y, r):
    id_circle = canvas.create_oval(x - r, y - r, x + r, y + r, fill='#778899', outline='#778899', width=0)
    return id_circle


class _Main:  # 调用SysTrayIcon的Demo窗口
    def __init__(self):
        self.root = tkinter.Tk()
        self.SysTrayIcon = None  # 判断是否打开系统托盘图标

    def main(self):
        # 按button后调用的主要方法
        def bilibli_notify():
            status = False
            url = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id='
            number = inp1.get()
            print(number)
            bilibili_url = url + number
            room_info = requests.get(bilibili_url).json()
            calls = room_info['data']['room_info']['tags']
            room_title = room_info['data']['room_info']['title']
            tmp = 0  # 用于清屏
            use_proxy = False  # 你访问土鳖要梯子么, 要就改成 True
            # 要梯子的情况下 socks5://[用户名]:[密码]@[地址]:[端口] 形式的梯子入口。一般人可能是 socks5://127.0.0.1:[端口]
            # proxy_url = 'socks5://user:pass@host:port'
            while True:
                use_proxy = False  # 你访问土鳖要梯子么, 要就改成 True
                # 要梯子的情况下 socks5://[用户名]:[密码]@[地址]:[端口] 形式的梯子入口。一般人可能是 socks5://127.0.0.1:[端口]
                proxy_url = 'socks5://user:pass@host:port'
                if btn1['text'] == '确认':
                    btn1['text'] = '停止'
                    while True:
                        if use_proxy:
                            resp = requests.get(bilibili_url, proxies=dict(http=proxy_url, https=proxy_url))
                        else:
                            resp = requests.get(bilibili_url)
                            resp = resp.content.decode('utf-8')
                            # live_status为1就是开播，0就是没开播
                            bilibili_result = '"live_status":1' in resp and '"live_status":0' not in resp
                        if bilibili_result:
                            if status is False:
                                circle_green(canvas, 200, 210, 20)
                                localtime = time.asctime(time.localtime(time.time()))
                                txt.insert(END, localtime + "\n开播了\n")
                                txt.insert(END, "房间标题:" + room_title + "\n" + "房间信息:" + calls + "\n\n")
                                tmp += 1
                                time.sleep(1)
                                circle(canvas, 200, 210, 20)
                                if tmp == 1:
                                    txt.delete(1.0, END)
                                    tmp = 0  # 重置为0，重新计数
                        else:
                            status = False
                            circle_red(canvas, 200, 210, 20)
                            localtime = time.asctime(time.localtime(time.time()))
                            txt.insert(END, localtime + "\n未开播，如要停止，请直接关闭本窗口\n\n")
                            tmp += 1
                            time.sleep(6)
                            if tmp == 3:
                                txt.delete(1.0, END)
                                tmp = 0  # 重置为0，重新计数



        self.root.bind("<Unmap>",
                       lambda
                           event: self.Hidden_window() if self.root.state() == 'iconic' else False)
        # 窗口最小化判断，可以说是调用最重要的一步
        self.root.protocol('WM_DELETE_WINDOW', self.exit)  # 点击Tk窗口关闭时直接调用s.exit，不使用默认关闭
        # root = Tk()
        self.root.geometry('400x400')
        self.root.resizable(0, 0)
        self.root.title('监听B站直播')
        canvas = Canvas(self.root, width=600, height=600, bg='#778899')
        canvas.config(highlightthickness=0)
        canvas.pack()
        self.root.configure(bg='#778899')

        lb1 = Label(self.root, text='请输入需要监听的B站直播房间号', bg='#778899', font=('San Francisco', 12, 'bold'))
        lb1.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.1)
        V = StringVar()
        inp1 = Entry(self.root, textvariable=V)
        inp1.place(relx=0.35, rely=0.2, relwidth=0.3, relheight=0.08)
        V.get()
        # 方法-直接调用 run1()
        btn1 = Button(self.root, text='确认', command=lambda: thread_it(bilibli_notify))
        btn1.place(relx=0.45, rely=0.35, relwidth=0.1, relheight=0.1)

        # 在窗体垂直自上而下位置60%处起，布局相对窗体高度40%高的文本框
        txt = Text(self.root, bg='#696969', font=('San Francisco', 10, 'bold'))
        txt.place(rely=0.6, relheight=0.4)
        txt.configure(fg='white')

        thread_it(self.root.mainloop())

    def switch_icon(self, _sysTrayIcon, icon='D:\\2.ico'):
        # 点击右键菜单项目会传递SysTrayIcon自身给引用的函数，所以这里的_sysTrayIcon = s.sysTrayIcon
        # 只是一个改图标的例子，不需要的可以删除此函数
        _sysTrayIcon.icon = icon
        _sysTrayIcon.refresh_icon()

    def Hidden_window(self, icon='D:\\1.ico', hover_text="SysTrayIcon.py Demo"):
        '''隐藏窗口至托盘区，调用SysTrayIcon的重要函数'''

        # 托盘图标右键菜单, 格式: ('name', None, callback),下面也是二级菜单的例子
        # 24行有自动添加‘退出’，不需要的可删除
        menu_options = (('别看了，没有', None, self.switch_icon),
                        ('二级 菜单', None, (('别看了，也没有', None, self.switch_icon),)))

        self.root.withdraw()  # 隐藏tk窗口
        if self.SysTrayIcon:
            self.SysTrayIcon.update()  # 已经有托盘图标时调用 update 来更新显示托盘图标
        else:
            self.SysTrayIcon = SysTrayIcon(icon,  # 图标
                                           hover_text,  # 光标停留显示文字
                                           menu_options,  # 右键菜单
                                           on_quit=self.exit,  # 退出调用
                                           tk_window=self.root,  # Tk窗口
                                           )

    def exit(self, _sysTrayIcon=None):
        self.root.destroy()
        print('exit...')


if __name__ == '__main__':
    Main = _Main()
    Main.main()
