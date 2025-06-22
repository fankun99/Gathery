import datetime
import ipaddress
import json
import os
import random
import re
import shlex
import sqlite3
import sys
import base64
import traceback
from urllib.parse import quote, unquote
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QPushButton, QComboBox, \
    QTextEdit, QHBoxLayout, QCheckBox, QLineEdit,QFileDialog,QGroupBox,QScrollArea,QTextBrowser,QSpacerItem, QSizePolicy

from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
import string
from PyQt5.QtCore import Qt, QUrl ,QSize
from PyQt5.QtGui import QDesktopServices

from urllib.parse import quote
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import FunctionPage.common as common


def get_main_path():
    """
    Returns the absolute path of the last directory in the path of the main executable or script.
    If the program is frozen (i.e., packaged with PyInstaller), it returns the directory containing the .exe file.
    Otherwise, it returns the directory containing the main .py script.
    """
    if getattr(sys, 'frozen', False):
        # If the application is frozen, get the directory of the executable
        path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        # If not frozen, get the directory of the main script
        path = os.path.dirname(os.path.abspath(__file__))
    
    # Get the last directory path
    last_directory = os.path.basename(path)
    last_directory_absolute_path = os.path.join(os.path.dirname(path), last_directory)
    
    return last_directory_absolute_path

this_dir = common.this_dir


scroll_style = """
    /* 水平滚动条样式 */
    QScrollBar:horizontal {
        border: none;
        background: #f0f0f0;
        height: 10px;  /* 设置滚动条高度 */
        margin: 0px 20px 0 20px;  /* 设置滚动条的边距 */
    }

    /* 水平滚动条滑块样式 */
    QScrollBar::handle:horizontal {
        background: #c0c0c0;
        min-width: 20px;  /* 设置滑块的最小宽度 */
    }

    /* 水平滚动条增加和减少按钮样式 */
    QScrollBar::add-line:horizontal {
        border: none;
        background: none;
    }

    QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
    }

    /* 垂直滚动条样式 */
    QScrollBar:vertical {
        border: none;
        background: #f0f0f0;
        width: 5px;  /* 设置滚动条宽度 */
        margin: 20px 0 20px 0;  /* 设置滚动条的边距 */
    }

    /* 垂直滚动条滑块样式 */
    QScrollBar::handle:vertical {
        background: #c0c0c0;
        min-height: 20px;  /* 设置滑块的最小高度 */
    }

    /* 垂直滚动条增加和减少按钮样式 */
    QScrollBar::add-line:vertical {
        border: none;
        background: none;
    }

    QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    QScrollArea { border: none; border-radius: 15px; }
"""

class TextProcessor(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()
        self.basic_style = basic_style
        # self.setStyleSheet("background-color: #f7f8fc;")  # 设置背景色
        self.link_connected = False
        self.combo_box_style = combo_box_style
        self.setStyleSheet(self.basic_style)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        self.input_text_edit = QTextEdit()
        self.input_mode_combo = QComboBox()
        self.input_mode_combo.addItem("输入")
        self.input_mode_combo.addItem("文件")
        self.input_mode_combo.setFixedWidth(180)
        self.input_mode_combo.setFixedHeight(40)
        self.input_mode_combo.setStyleSheet(self.combo_box_style)

        self.input_mode_combo.currentIndexChanged.connect(self.change_input_mode)
        self.function_buttons = {}
        self.result_display = QTextBrowser()
        self.input_file_path = ""
        self.input_model = 0  # 0: 输入形式 1:文件形式

        input_mode_layout = QHBoxLayout()
        label = QLabel("  模式:  ")
        input_mode_layout.addWidget(label)
        input_mode_layout.addWidget(self.input_mode_combo)

        input_mode_layout.addStretch()
        layout.addLayout(input_mode_layout)

        input_group_box = QGroupBox("输入")
        
        input_group_layout = QVBoxLayout()
        input_group_layout.setContentsMargins(0, 1, 0, 0)  # 设置内边距
        input_group_layout.addWidget(self.input_text_edit)
        input_group_box.setLayout(input_group_layout)

        result_group_box = QGroupBox("结果")
        result_group_layout = QVBoxLayout()
        result_group_layout.setContentsMargins(0, 1, 0, 0)  # 设置内边距
        result_group_layout.addWidget(self.result_display)
        result_group_box.setLayout(result_group_layout)

        scroll_area_input = QScrollArea()
        scroll_area_input.setWidget(input_group_box)
        scroll_area_input.setWidgetResizable(True)
        scroll_area_input.setStyleSheet(scroll_style)

        scroll_area_output = QScrollArea()
        scroll_area_output.setWidget(result_group_box)
        scroll_area_output.setWidgetResizable(True)
        scroll_area_output.setStyleSheet(scroll_style)
        # 第一行按钮
        function_row1_layout = QHBoxLayout()
        functions_row1 = {
            "提取IP": this_dir+"/icon/ip.png",
            "IP转C段": this_dir+"/icon/ipc.png",
            "IP转B段": this_dir+"/icon/ipB.png",
            "IP段转IP": this_dir+"/icon/ip.png",
            "公网/私网地址分类": this_dir+"/icon/ip.png",
            "提取邮箱": this_dir+"/icon/mail.png",
        }
        for func,icon_path in functions_row1.items():
            button = QPushButton(func)
            # 按钮样式
            icon = QIcon(icon_path)
            button.setIcon(icon)
            button.setIconSize(QSize(28, 28))  # 设置图标大小为 32x32 像素
            button.setStyleSheet("QPushButton { border-radius: 10px; background-color: #e2f1fd; color: #7586a6; height:40px; border: 1px solid gray;}")
            # 按钮点击
            button.clicked.connect(lambda state, x=func: self.apply_function(x))
            self.function_buttons[func] = button
            function_row1_layout.addWidget(button)
        
        # 创建一个 QGroupBox用来分割
        group_box = QGroupBox()
        group_box.setStyleSheet("border-radius: 10px;border: 1px solid #c0dbf0;")
        group_box_layout = QHBoxLayout(group_box)

        # 分割
        self.button_split = QPushButton("切分")
        icon = QIcon(this_dir+"/icon/split.png")
        self.button_split.setIcon(icon)
        self.button_split.setIconSize(QSize(28, 28))  # 设置图标大小为 32x32 像素
        # self.button_split.setFixedWidth(100)
        self.button_split.setStyleSheet("QPushButton { background-color: #c0dbf0; border-radius: 10px; color: #7586a6; height:40px; border: 1px solid gray;}")

        self.split_str = QLineEdit()
        self.split_str.setFixedWidth(120)
        self.split_str.setFixedHeight(40)
        self.split_str.setPlaceholderText("切分字符")
        self.split_number = QLineEdit()
        self.split_number.setFixedWidth(150)
        self.split_number.setFixedHeight(40)
        self.split_number.setPlaceholderText("值索引,从0开始")
        # 添加组件到 QGroupBox
        group_box_layout.addWidget(self.split_str)
        group_box_layout.addWidget(self.split_number)
        group_box_layout.addWidget(self.button_split)
        function_row1_layout.addWidget(group_box)
        self.button_split.clicked.connect(self.SplitStr)

        #第2行
        function_row2_layout = QHBoxLayout()
        functions_row2 = {
            "文本去重": this_dir +"/icon/text.png",
            "去掉换行": this_dir +"/icon/Line_break.png",
            "添加https://": this_dir +"/icon/https.png",
            "添加http://": this_dir +"/icon/http.png",
        }
        for func,icon_path in functions_row2.items():
            button = QPushButton(func)
            icon = QIcon(icon_path)
            button.setIcon(icon)
            button.setIconSize(QSize(28, 28))  # 设置图标大小为 32x32 像素
            # 按钮样式
            font = QFont('Microsoft YaHei', 12)
            font.setBold(True)  # 设置为加粗
            button.setFont(font)
            button.setStyleSheet(
                "QPushButton { border-radius: 10px; background-color: #c0dbf0; color: #7586a6; height:40px; border: 1px solid gray;}")
            # 按钮点击
            button.clicked.connect(lambda state, x=func: self.apply_function(x))
            self.function_buttons[func] = button
            function_row2_layout.addWidget(button)

        # 第3行按钮
        function_row3_layout = QHBoxLayout()
        functions_row3 = {
            "Base64 解码": this_dir +"/icon/Base64.png",
            "Base64 编码": this_dir +"/icon/Base64.png",
            "URL 解码": this_dir +"/icon/url.png",
            "URL 编码": this_dir +"/icon/url.png",
        }
        for func,icon_path in functions_row3.items():
            button = QPushButton(func)
            icon = QIcon(icon_path)
            button.setIcon(icon)
            button.setIconSize(QSize(28, 28))  # 设置图标大小为 32x32 像素
            # 按钮样式
            font = QFont('Microsoft YaHei', 12)
            font.setBold(True)  # 设置为加粗
            button.setFont(font)
            button.setStyleSheet(
                "QPushButton { border-radius: 10px; background-color: #c0dbf0; color: #7586a6; height:40px; border: 1px solid gray;}")
            # 按钮点击
            button.clicked.connect(lambda state, x=func: self.apply_function(x))
            self.function_buttons[func] = button
            function_row3_layout.addWidget(button)

        # 第4行按钮
        function_row4_layout = QHBoxLayout()
        
        functions_row4 = {
            "​​HTTP 请求原始格式换 Python 代码": this_dir +"/icon/convert.png",
            "Curl 转 Python": this_dir +"/icon/convert.png",
            "Json格式化":this_dir +"/icon/convert.png"
        }
        for func, icon_path in functions_row4.items():
            button = QPushButton(func)
            button = QPushButton(func)
            icon = QIcon(icon_path)
            button.setIcon(icon)
            button.setIconSize(QSize(28, 28))  # 设置图标大小为 32x32 像素
            # 按钮样式
            font = QFont('Microsoft YaHei', 12)
            font.setBold(True)  # 设置为加粗
            button.setFont(font)
            button.setStyleSheet(
                "QPushButton { border-radius: 10px; background-color: #e2f1fd; color: #7586a6; height:40px; border: 1px solid gray;}")
            if func == "​​HTTP 请求原始格式换 Python 代码":
                tips = """
                例如:POST /xxxx HTTP/2
                    Host: 127.0.0.1
                    Content-Length: 20
                    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36
                    Content-Type: application/x-www-form-urlencoded
                    Accept: */*

                    w=123123&x=1234
                """
                button.setToolTip(tips)
            if func == "Curl 转 Python":
                tips = """
                    例如:\ncurl -X POST \
                    -H "Content-Type: application/x-www-form-urlencoded" \
                    -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" \
                    -d "name=John&age=30&location=USA" \
                    http://example.com/submit/
                """
                button.setToolTip(tips)
            # 按钮点击
            button.clicked.connect(lambda state, x=func: self.apply_function(x))
            self.function_buttons[func] = button
            function_row4_layout.addWidget(button)
            
        layout.addWidget(scroll_area_input)
        layout.addLayout(function_row1_layout)
        layout.addLayout(function_row2_layout)
        layout.addLayout(function_row3_layout)
        layout.addLayout(function_row4_layout)
        layout.addWidget(scroll_area_output)

    def change_input_mode(self, index):
        if index == 0:  # 输入形式
            self.input_model = 0
            self.input_text_edit.setReadOnly(False)
            self.input_text_edit.clear()
        elif index == 1:  # 文件形式
            self.input_model = 1
            self.input_text_edit.setReadOnly(True)
            self.load_file_content()

    def load_file_content(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "Text Files (*.txt)")
        if file_path:
            self.input_file_path = file_path
            self.input_text_edit.setPlainText(file_path)

    def get_input_text(self):
        if self.input_model == 0:  # 输入形式
            return self.input_text_edit.toPlainText().strip()
        elif self.input_model == 1:  # 文件形式
            with open(self.input_file_path, 'r') as file:
                return file.read()

    def open_directory(self, url):
         # 如果输入模式为文件形式，则执行打开文件夹的操作
        if self.input_model == 1:
            try:
                QDesktopServices.openUrl(url)
            except Exception as e:
                print("Error creating database connection:", e)

            self.result_display.setText(f"结果已保存到：{self.path}")
            return
        else:
            self.result_display.setText(self.result_text)

    # 分割字符串
    def SplitStr(self, event=None):
        self.result_display.setText("执行中......")
        input_text = str(self.get_input_text()).strip()
        if input_text:
            split_object = self.split_str.text()
            get_number_index = self.split_number.text()
            if not get_number_index:
                get_number_index = 0
            else:
                get_number_index = int(get_number_index)
            if not split_object or len(split_object.strip()) == 0:
                split_object = None
            lines = input_text.split('\n')
            # 遍历每一行进行处理
            result = []
            for line in lines:
                # 如果行为空则跳过
                if not line:
                    continue
                # 按照切分字符切分每一行，并获取指定索引的值
                parts = line.split(split_object)
                if len(parts) > get_number_index:
                    result.append(parts[get_number_index])
            # 展示结果
            if self.input_model == 0:  # 输入形式
                if self.link_connected:
                    self.link_connected = False
                self.result_display.clear()  # 清空文本内容并插入新文本
                if result:
                    result_text = '\n'.join(result)
                    self.result_display.setPlainText(result_text)
                else:
                    self.result_display.setPlainText("已完成，结果为空")
                self.result_display.setOpenExternalLinks(False)  # 禁止打开外部链接

            elif self.input_model == 1:  # 文件形式
                # 获取当前时间
                current_time = datetime.datetime.now()
                output_filename = current_time.strftime("%Y-%m-%d_%H-%M-%S")
                save_path = "split_" + output_filename + "_result.txt"
                with open(save_path, 'a+') as file:
                    file.write(self.result_text)
                current_directory = os.getcwd()
                print("当前路径:", current_directory)
                self.path = f"{current_directory}\\{save_path}"
                # 将文本设置为超链接
                local_file_url = QUrl.fromLocalFile(current_directory)
                self.local_path = f'<a href="{local_file_url.toString()}">结果已保存到：{self.path}</a>'
                self.result_display.setHtml(self.local_path)
                # 将链接的点击事件连接到槽函数
                if not self.link_connected:
                    self.result_display.anchorClicked.connect(self.open_directory)
                    self.link_connected = True
        else:
            self.result_display.setText("输入为空!!")
    
    def extract_addresses(self,input_data):
        def is_valid_cidr(cidr):
            try:
                ip, mask = cidr.split('/')
                ipaddress.ip_network(cidr)
                return True
            except ValueError:
                return False
    
        # 正则表达式匹配IP地址及CIDR表示法
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:\/\d{1,2})?\b'

        # 匹配IP地址
        ips = re.findall(ip_pattern, input_data)

        # 区分公网地址和私网地址
        public_ips = []
        private_ips = []
        for ip in ips:
            if '/' in ip:
                if not is_valid_cidr(ip):
                    continue
                public_ips.append(ip)
            else:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private:
                    private_ips.append(ip)
                else:
                    public_ips.append(ip)

        return public_ips, private_ips

    def apply_function(self, function_name):
        self.result_display.setText("执行中......")
        input_text = str(self.get_input_text()).strip()
        if function_name == "文本去重":
            lines = input_text.split('\n')
            new_list = [x for x in lines if x != '']
            if new_list:
                unique_lines = set(lines)
                self.result_text = '\n'.join(unique_lines)
            else:
                self.result_text = "输入为空"
        elif function_name == "去掉换行":
            self.result_text = input_text.replace('\n', '')
        elif function_name == "添加https://":
            lines = input_text.split('\n')
            new_list = [x for x in lines if x != '']
            if new_list:
                https_lines = ['https://' + line if not line.startswith('https://') else line for line in lines]
                self.result_text = '\n'.join(https_lines)
            else:
                self.result_text = "输入为空"
        elif function_name == "添加http://":
            lines = input_text.split('\n')
            new_list = [x for x in lines if x != '']
            if new_list:
                https_lines = ['http://' + line if not line.startswith('http://') else line for line in lines]
                self.result_text = '\n'.join(https_lines)
            else:
                self.result_text = "输入为空"
        elif function_name == "提取IP":
            ip_pattern = r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
            ips = re.findall(ip_pattern, input_text)
            self.result_text = '\n'.join(ips)
        elif function_name == "IP转C段":
            lines = input_text.split('\n')
            ipc = set()
            for line in lines:
                try:
                    ip = ipaddress.ip_interface(line)
                    # 检查网络前缀长度是否为 24
                    if ip.network.prefixlen == 24:
                        ipc.add(line)
                    else:
                        ip_parts = line.split('.')
                        cidr = '.'.join(ip_parts[:3]) + '.0/24'
                        ipc.add(cidr)
                except ValueError:
                    self.result_text = "输入不是合法IP"
            self.result_text = '\n'.join(list(ipc))
        
        elif function_name == "IP转B段":
            lines = input_text.split('\n')
            ipb = set()
            for line in lines:
                try:
                    ip = ipaddress.ip_interface(line)
                    # 获取网络对象
                    network = ip.network
                    # 检查网络前缀长度是否为 16,也就是是否已经是b段了
                    if network.prefixlen == 16:
                        ipb.add(line)
                    else:
                        b_network = str(network.network_address) + '/16'
                        ipb.add(b_network)
                except ValueError:
                    self.result_text = "输入不是合法IP"
            self.result_text = '\n'.join(list(ipb))
        
        elif function_name == "IP段转IP":
            lines = input_text.split('\n')
            ip_list = set() 
            for line in lines:
                line = line.strip()  # 去除空白字符
                try:
                    # 尝试解析输入为 IP 地址
                    ip = ipaddress.ip_address(line)
                    ip_list.add(str(ip))
                except ValueError:
                    try:
                        # 尝试解析输入为网络地址（CIDR）
                        network = ipaddress.ip_network(line, strict=False)  # strict=False 允许接受长度为 32（IPv4）或 128（IPv6）的地址
                        for ip in network.hosts():
                            ip_list.add(str(ip))
                    except ValueError:
                        print(f"无法解析输入: {line}，跳过该行")
                        traceback.print_exc()
                    self.result_text = "输入不是合法IP"
            self.result_text = '\n'.join(list(ip_list))

        elif function_name == "公网/私网地址分类": 

            public_ips, private_ips = self.extract_addresses(input_text)
            self.result_text = "--------公网地址---------\n" + '\n'.join(public_ips)
            self.result_text += "\n--------私网地址---------\n" + '\n'.join(private_ips)

        elif function_name == "提取邮箱":
            email_pattern = r'\b[A-Za-z0-9]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, input_text)
            self.result_text = '\n'.join(emails)
        
        elif function_name == "Base64 解码":
            try:
                decoded_text = base64.b64decode(input_text.encode('utf-8')).decode('utf-8')
                self.result_text = decoded_text
            except Exception as e:
                self.result_text = f"解码失败: {str(e)}"
        
        elif function_name == "Base64 编码":
            encoded_text = base64.b64encode(input_text.encode('utf-8')).decode('utf-8')
            self.result_text = encoded_text
        
        elif function_name == "URL 解码":
            decoded_url = unquote(input_text)
            self.result_text = decoded_url
        
        elif function_name == "URL 编码":
            encoded_url = quote(input_text)
            self.result_text = encoded_url
        
        elif function_name == "​​HTTP 请求原始格式换 Python 代码":
            self.result_text = self.convert_request_to_python(input_text)
        
        elif function_name == "Curl 转 Python":
            # 实现 Curl 转 Python 的功能
            self.result_text = self.curl_to_python(input_text)

        elif function_name == "Json格式化":
            input_lines = input_text.split('\n')
            new_list = [x for x in input_lines if x != '']
            if new_list:
                try:
                    json_data = json.loads(input_text)
                    self.result_text = json.dumps(json_data, indent=4, sort_keys=True)
                except:
                    self.result_text = "请检查输入是否正确"
            else:
                self.result_text = "请输入需要格式化的数据，例如：{\"name\": \"John\", \"age\": 30, \"city\": \"New York\", \"pets\": [\"dog\", \"cat\"]}"
        
        else:
            self.result_text = "未知功能"
        
        # 展示结果
        if self.input_model == 0:  # 输入形式
            if self.link_connected:
                self.link_connected = False
            self.result_display.clear()  # 清空文本内容并插入新文本
            if self.result_text:
                self.result_display.setPlainText(self.result_text)
            else:
                self.result_display.setPlainText("已完成，结果为空")
            self.result_display.setOpenExternalLinks(False)  # 禁止打开外部链接

        elif self.input_model == 1:  # 文件形式
            # 获取当前时间
            current_time = datetime.datetime.now()
            output_filename = current_time.strftime("%Y-%m-%d_%H-%M-%S")
            if function_name == "添加https://":
                save_path = "添加https_" + output_filename +  "_result.txt"
            else:
                save_path = function_name + "_" + output_filename + "_result.txt"
            with open(save_path, 'a+') as file:
                file.write(self.result_text)
            current_directory = os.getcwd()
            print("当前路径:", current_directory)
            self.path = f"{current_directory}\\{save_path}"
            # 将文本设置为超链接
            local_file_url = QUrl.fromLocalFile(current_directory)
            self.local_path = f'<a href="{local_file_url.toString()}">结果已保存到：{self.path}</a>'
            self.result_display.setHtml(self.local_path)
            # 将链接的点击事件连接到槽函数
            if not self.link_connected:
                self.result_display.anchorClicked.connect(self.open_directory)
                self.link_connected = True


    def convert_request_to_python(self, request_data):
        try:
            lines = request_data.split('\n')
            if (lines and lines[0] is None) or lines[0] == "":
                del lines[0]
            if len(lines) < 2:
                return "Invalid data"
            method, url_path, protocol = lines[0].split()
            headers = {}
            body = ""
            for line in lines[1:]:
                if line.strip() == '':
                    break
                key, value = line.split(': ', 1)
                headers[key] = value.strip()

            # 获取请求体数据
            if len(lines) > len(headers) + 2:
                body = '\n'.join(lines[len(headers) + 2:])

            url_path = str(url_path).replace("'", "\\'")
            # 生成 Python 代码字符串
            python_code = f"import requests\n\n"
            python_code += f"target = ''\n"
            python_code += f"proxies = {{}}\n"

            python_code += f"url = target + '{url_path}'\n"
            python_code += f"headers = {headers}\n"
            if method == 'POST':
                body = str(body).replace('"', '\\\"')
                print(body)
                python_code += f"body = \"{body}\"\n"
            else:
                python_code += f"body = ''\n\n"

            if method == 'GET':
                python_code += f"response = requests.get(url, headers=headers, timeout=10, verify=False, proxies=proxies)\n"
            elif method == 'POST':
                python_code += f"response = requests.post(url, headers=headers, data=body, timeout=10, verify=False, proxies=proxies)\n"
            else:
                python_code += f"response = None  # Unsupported HTTP method: {method}\n"

            python_code += f"print(response.text)\n" if method in ['GET', 'POST'] else ""

            return python_code
        except:
            return "convert error!!"

    def parse_curl_command(self, curl_command):
        parsed = shlex.split(curl_command)
        method = None
        url = None
        headers = {}
        data = None

        i = 0
        while i < len(parsed):
            if parsed[i] == 'curl':
                i += 1
                continue
            elif parsed[i].startswith('-'):
                if parsed[i] == '-X':
                    method = parsed[i + 1].lower()
                    i += 2
                elif parsed[i] == '-H':
                    header_str = parsed[i + 1]
                    header_parts = re.split(r'(?<!\\):', header_str)
                    header_name = header_parts[0].replace('\\"', '"').replace('$', '').strip()
                    header_value = header_parts[1].replace('\\"', '"').replace('$', '').strip()
                    headers[header_name] = header_value
                    i += 2
                elif parsed[i] == '--data-binary' or parsed[i] == '-d':
                    data = parsed[i + 1].replace('$', '').strip()
                    i += 2
                else:
                    i += 1
            else:
                url = parsed[i].replace('$', '').strip()
                i += 1

        return {'method': method, 'url': url, 'headers': headers, 'data': data}

    def generate_python_code(self, method, url, headers, data):
        code = "import requests\n\n"
        code += f"proxies = {{}}\n"
        code += f"url = '{url}'\n"
        code += "headers = {\n"
        for key, value in headers.items():
            code += f"    '{key}': '{value}',\n"
        code += "}\n"
        if data:
            data = str(data).replace("\"", "\\\"")
            code += f"data = \"{data}\"\n\n"
        else:
            code += "data = None\n\n"

        code += f"response = requests.{method}("

        if method == 'get' or method == 'delete':
            code += "url, headers=headers, timeout=10, verify=False, proxies=proxies)\n"
        elif method == 'post' or method == 'put':
            code += "url, headers=headers, data=data, timeout=10, verify=False, proxies=proxies)\n"

        code += "print(response.text)"
        return code

    def curl_to_python(self, curl_command):
        parsed = self.parse_curl_command(curl_command)
        method = parsed['method']
        url = parsed['url']
        headers = parsed['headers']
        data = parsed['data']
        python_code = self.generate_python_code(method, url, headers, data)
        return python_code

class PasswordGenerator(QWidget):
    def __init__(self,basic_style):
        super().__init__()
        self.basic_style = basic_style
        self.setStyleSheet(self.basic_style)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # layout.setContentsMargins(30, 60, 0, 0)  # 设置左边，顶部，右边，底部间距

        char_label = QLabel("所用字符：")
        char_layout = QHBoxLayout()
        self.numbers_checkbox = QCheckBox("数字")
        self.numbers_checkbox.setChecked(True)  # 默认选择
        self.letters_checkbox = QCheckBox("字母")
        self.letters_checkbox.setChecked(True)  # 默认选择
        self.uppercase_checkbox = QCheckBox("大写字母")
        self.uppercase_checkbox.setChecked(True)  # 默认选择
        self.punctuation_checkbox = QCheckBox("标点符号")
        self.punctuation_checkbox.setChecked(True)  # 默认选择
        self.unique_chars_checkbox = QCheckBox("字符不重复")
        self.unique_chars_checkbox.setChecked(True)  # 默认选择

        char_layout.addWidget(char_label)
        char_layout.addWidget(self.numbers_checkbox)
        char_layout.addWidget(self.letters_checkbox)
        char_layout.addWidget(self.uppercase_checkbox)
        char_layout.addWidget(self.punctuation_checkbox)
        char_layout.addWidget(self.unique_chars_checkbox)

        # 密码长度输入框
        length_layout = QHBoxLayout()
        length_layout.setContentsMargins(0, 20, 0, 0)  # 设置顶部间距为30px
        length_label = QLabel("密码长度：")
        self.length_input = QLineEdit()
        self.length_input.setPlaceholderText("密码长度")
        self.length_input.setText(" 8")  # 默认密码长度8个
        self.length_input.setFixedHeight(40)

        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_input)

        # 随机密码个数输入框
        num_passwords_layout = QHBoxLayout()
        num_passwords_layout.setContentsMargins(0, 30, 0, 0)  # 设置顶部间距为30px
        num_passwords_label = QLabel("随机密码个数：")
        self.num_passwords_input = QLineEdit()
        self.num_passwords_input.setFixedHeight(40)
        self.num_passwords_input.setPlaceholderText("随机生成的密码个数")
        self.num_passwords_input.setText(" 6")  # 默认随机密码个数为8个

        num_passwords_layout.addWidget(num_passwords_label)
        num_passwords_layout.addWidget(self.num_passwords_input)

        # 生成按钮
        self.generate_button = QPushButton("生成")
        self.generate_button.setFixedWidth(100)  # 设置按钮宽度
        self.generate_button.clicked.connect(self.generate_passwords)
        
        # 展示生成的密码
        self.password_display = QTextEdit()
        self.password_display.setReadOnly(True)

        layout.addLayout(char_layout)
        layout.addLayout(num_passwords_layout)
        layout.addLayout(length_layout)

        layout.addSpacing(20)  # 设置按钮距离上一个组件30px
        layout.addWidget(self.generate_button)

        layout.addSpacing(20)  # 设置按钮距离上一个组件30px
        layout.addWidget(self.password_display)

        self.setLayout(layout)

    def generate_passwords(self, event=None):
        try:
            characters = ""
            if self.numbers_checkbox.isChecked():
                characters += string.digits
            if self.letters_checkbox.isChecked():
                characters += string.ascii_letters
            if self.uppercase_checkbox.isChecked():
                characters += string.ascii_uppercase
            if self.punctuation_checkbox.isChecked():
                characters += string.punctuation
            if self.unique_chars_checkbox.isChecked():
                characters = ''.join(set(characters))  # 去除重复字符

            length = int(self.length_input.text().strip())
            num_passwords = int(self.num_passwords_input.text().strip())

            passwords = []
            for _ in range(num_passwords):
                password = ''.join(random.choice(characters) for _ in range(length))
                passwords.append(password)
            self.password_display.setPlainText('\n'.join(passwords))
        except:
            self.password_display.setPlainText("请按规定设置")

class MainWindow(QMainWindow):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style

        self.setWindowTitle("tools")
        # self.setGeometry(300, 100, 2000, 1200)  # 设置窗口大小
        self.setStyleSheet("background-color: white;")  # 设置背景色
        # 界面字体大小设置
        font = QFont("Microsoft YaHei", 14)  # 字体和大小
        QApplication.setFont(font)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.function_tabs = QTabWidget()

        self.TextProcessor = TextProcessor(self.basic_style,self.combo_box_style)
        self.password_generator_page = PasswordGenerator(self.basic_style)

    def create_layout(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: white")  #设置渐变背景色
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.function_tabs)
        self.setCentralWidget(central_widget)

    # 样式设置
    def create_connections(self):
        # font = QFont("Helvetica Neue", 12)  # 字体和大小
        # QApplication.setFont(font)

        self.function_tabs.setStyleSheet(
            """
            QTabBar::tab {
                background-color: #f0f0f0; /* 未选择时#1c154a; */
                color: #34499a;
            }
            QTabBar::tab:selected {
                background-color: #ffffff; /* 选择后白色 */
                color: green;
                
            }
            QTabWidget::pane {
                border: none; /* 去除边框 */
            }
            """
        )
        # 添加图标到选项卡
        self.function_tabs.addTab(self.TextProcessor, QIcon(this_dir +"/icon/text.png"), "文本处理")
        self.function_tabs.addTab(self.password_generator_page, QIcon(this_dir +"/icon/random.png"), "随机密码生成")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
