import subprocess
import os
from connect_browser import connect_to_browser_and_page

def open_edge_window(port, url, user_data_dir):
    subprocess.Popen([
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",  # Edge 浏览器路径
        f"--remote-debugging-port={port}",  # 不同的调试端口
        f"--user-data-dir={user_data_dir}",  # 独立的用户数据目录
        "--new-window",  # 强制在新的窗口中打开
        url  # 要打开的网页
    ])

# 创建不同的用户数据目录
base_user_data_dir = r"C:\Users\hallm\AppData\Local\Microsoft\Edge\User Data"

# 启动多个窗口，使用不同的调试端口和用户数据目录
open_edge_window(2001, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile1"))
# open_edge_window(2002, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile2"))
# open_edge_window(2003, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile3"))
# open_edge_window(2004, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile4"))
# open_edge_window(2005, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile5"))

# open_edge_window(2006, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile6"))

# open_edge_window(2007, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile7"))

# open_edge_window(2008, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile8"))

# open_edge_window(2009, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile9"))

# open_edge_window(2010, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile10"))

# open_edge_window(2011, "https://e2api.staff.xdf.cn/e2/dingdingqr?returnUrl=https%3A%2F%2Ftps-tiku.staff.xdf.cn%2F&e2clientid=20004", os.path.join(base_user_data_dir, "Profile11"))

