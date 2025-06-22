import csv
import datetime
import json
import os
import sys
import threading

import whois
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QPushButton, QComboBox, \
    QTextEdit, QHBoxLayout, QCheckBox, QLineEdit,QFileDialog,QGroupBox,QMessageBox,QVBoxLayout, QGridLayout, QGroupBox,\
        QTableWidget,QTableWidgetItem,QAbstractItemView,QScrollArea,QTextBrowser,QHeaderView,QErrorMessage,QFrame
from PyQt5.QtGui import QPalette,QFont, QCursor,QColor,QIcon
from PyQt5.QtCore import Qt, QUrl ,QSize, QThread, pyqtSignal
import configparser
import urllib3

import random
import requests
import socket
import re
import FunctionPage.common as common
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    QScrollArea { border: 1px solid #5f68c3;}
"""

class WhoisWorkerThread(QThread):
    finished = pyqtSignal(dict)
    
    def __init__(self, domain_text):
        super().__init__()
        self.domain = domain_text
        self.result = {}
    def run(self):
        result = self.query_whois(self.domain)
        if result:
            self.result = result
            
        self.finished.emit(self.result)
        
    def query_whois(self,domain):
        whois_result = whois.whois(domain)
        return whois_result

class EmailThread(QThread):
    finished = pyqtSignal(dict)
    
    def __init__(self, domain_text):
        super().__init__()
        self.email = domain_text
        self.result = {}
    def run(self):
        try:
            # 提取邮箱域名
            email_domain = self.email.split('@')[-1]

            # 使用 WHOIS 查询邮箱域名的注册信息
            domain_info = whois.whois(email_domain)
            if domain_info:
                self.result =  domain_info
        except:
            pass
        self.finished.emit(self.result)
        
    def query_whois(self,domain):
        whois_result = whois.whois(domain)
        return whois_result

class ReverseIpThread(QThread):
    finished = pyqtSignal(dict)
    
    def __init__(self, domain_text,result_display,log_display):
        super().__init__()
        self.email = domain_text
        self.result = {}
        self.result_display = result_display
        self.log_display = log_display

    def run(self):
        self.result = self.get_base_info(self.email)
        self.finished.emit(self.result)
        
    # 获取ip地址所属位置
    def check_ip(self,ip):
        ip_list = []
        for i in ip:
            url = "https://ip.cn/ip/{}.html".format(i)
            res = requests.get(url=url, timeout=10, headers=self.headers_lib())
            html = res.text
            site = re.findall('<div id="tab0_address">(.*?)</div>', html, re.S)[0]
            result = "{}-{}".format(i, site).replace("  ", "-").replace(" ", "-")
            ip_list.append(result)
        return ip_list

    # 请求头库
    def headers_lib(self):
        lib = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:57.0) Gecko/20100101 Firefox/57.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:57.0) Gecko/20100101 Firefox/57.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:57.0) Gecko/20100101 Firefox/57.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.58",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"]
        headers = {
            "User-Agent": random.choice(lib)}
        return headers

    # 判断输入是IP还是域名
    def isIP(self,str):
        try:
            check_ip = re.compile(
                '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
            if check_ip.match(str):
                return True
            else:
                return False
        except:
            return False

    # 获取网页标题
    def get_title(self,url):
        try:
            res = requests.get(url=url, headers=self.headers_lib(), verify=False, timeout=3)
            res.encoding = res.apparent_encoding
            html = res.text
            title = re.findall("<title>(.*?)</title>", html, re.S)[0]
        except:
            title = "None"
        return title.replace(" ", "").replace("\r", "").replace("\n", "")

    # 格式化url
    def get_domain(self,url):
        if "https://" in url or "http://" in url:
            url = url.replace("https://", "").replace("http://", "")
        domain = "{}".format(url).split("/")[0]
        return domain

    # 美化输出whatcms内容
    def format_print(self,res_info):
        res_info = dict(res_info)
        for key in res_info.keys():
            try:
                if res_info[key] is not None:
                    isList = True if type(res_info[key]) == list else False
                    if isList:
                        if isinstance(res_info[key][0], str):
                            print("[{}]:{}".format(key, ','.join(res_info[key])))
                        else:
                            value = ""
                            for item in res_info[key]:
                                value += "{},".format(item.strftime('%Y-%m-%d %H:%M:%S'))
                            print("[{}]:{}".format(key,
                                                                                value.rstrip(",")))
                    else:
                        print("[{}]:{}".format(key, res_info[key]))
            except Exception as e:
                print('\033[Error]:{}'.format(e))

    def get_base_info(self,url):
        result = {}
        domain_url = self.get_domain(url)
        ip = []
        try:
            addrs = socket.getaddrinfo(domain_url, None)  
            for item in addrs:
                if item[4][0] not in ip:
                    ip.append(item[4][0])
            if len(ip) > 1:
                result["info"] = "[Ip]:{} \033 PS:CDN may be used".format(self.check_ip(ip))
                self.result_display.append("[Ip]:{} \033 PS:CDN may be used".format(self.check_ip(ip)))
                print("[Ip]:{} \033 PS:CDN may be used".format(self.check_ip(ip)))
            else:
                result["info"] = "[Ip]:{} \033 PS:CDN may be used".format(self.check_ip(ip))
                print("[Ip]:{}".format(self.check_ip(ip)[0]))
                self.result_display.append("[Ip]:{}".format(self.check_ip(ip)[0]))

        except Exception as e:
            print("[Ip_Error]:{}".format(e))
            self.result_display.append("[Ip_Error]:{}".format(e))
        if self.isIP(domain_url):
            url_d = "https://site.ip138.com/{}/".format(domain_url)
            res = requests.get(url=url_d, headers=self.headers_lib())
            html = res.text
            site = re.findall('<span class="date">(.*?)</span><a href="/(.*?)/" target="_blank">(.*?)</a>', html, re.S)
            if len(site) > 0:
                result["domain_name"] = site
                self.result_display.append("[The bound domain_name]:")
                print("[The bound domain_name]:")
                for a, b, c in site:
                    self.result_display.append("{} {}".format(a, b))
                    print("{} {}".format(a, b))
        else:
            whois_info = whois.whois(domain_url)
            self.format_print(whois_info)
        return result

class WhoisWidget(QWidget):
    def __init__(self,basic_style):
        super().__init__()
        self.result = None
        self.basic_style = basic_style
        self.key_translation = {
                "domain_name": "域名名称",
                "registrar": "注册商（域名注册服务提供商）",
                "whois_server": "WHOIS 服务器",
                "creation_date": "域名创建日期",
                "expiration_date": "域名过期日期",
                "updated_date": "域名信息更新日期",
                "status": "域名状态",
                "name_servers": "域名使用的 DNS 服务器列表",
                "emails": "注册联系邮箱",
                "registrant": "注册人信息",
                "registrant_state_province":"注册人所在地的州/省",
                "registrant_street":"注册人所在地址的街道信息",
                "registrant_organization":"注册人的组织或者公司名称",
                "registrant_city":"注册人所在城市",
                "registrant_country":"注册人所在的国家",
                "registrant_phone":"注册人的电话号码",
                "registrant_email":"注册人的邮箱",
                "registrant_name":"注册人的名称",
                "registrar_url":"域名的注册商的网址",
                "admin":"管理员的名称/标识",
                "admin_email":"管理员的邮箱地址",
                "admin_phone":"管理员的电话号码",
                "admin_fax":"管理员的传真号码",
                "tech":"技术联系人的名称或者标识",
                "tech_phone":"技术联系人的电话号码",
                "tech_email":"技术联系人的邮箱",
                "tech_fax":"技术联系人的传真号码",
                "admin_contact": "管理联系人信息",
                "tech_contact": "技术联系人信息",
                "dnssec": "DNS安全扩展",
                "state": "地区",
                "country": "国家",
                "org": "组织",
        }
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('whois')
        # self.resize(1200, 600)
        self.setStyleSheet(self.basic_style)
        layout = QVBoxLayout()

        # 第一排输入框和按钮
        options_layout = QHBoxLayout()
        self.port_input_label = QLabel("域名:")
        options_layout.addWidget(self.port_input_label)
        self.domain_input = QLineEdit()
        self.domain_input.setFixedHeight(62)
        self.domain_input.setPlaceholderText("请输入有效的域名,例如: baidu.com")
        options_layout.addWidget(self.domain_input)

        self.start_button = QPushButton('开始')
        self.start_button.setFixedWidth(100)
        self.start_button.setFixedHeight(62)
        
        options_layout.addWidget(self.start_button)
        self.start_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.start_button.clicked.connect(self.start_task)

        self.save_to_file_button = QPushButton('导出')
        self.save_to_file_button.setFixedWidth(100)
        self.save_to_file_button.setFixedHeight(62)
        options_layout.addWidget(self.save_to_file_button)
        self.save_to_file_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_to_file_button.clicked.connect(self.save_to_file)

        layout.addLayout(options_layout,1)

        
        # 显示结果和日志
        result_log_scroll_area = QScrollArea()
        # 设置无边框样式
        result_log_scroll_area.setStyleSheet("border: none;")
        
        result_log_layout = QHBoxLayout()
        result_log_scroll_area.setWidgetResizable(True)
       

        result_display_layout = QVBoxLayout()

        self.result_display_label = QLabel("Results:")
        result_display_layout.addWidget(self.result_display_label)

        self.result_display =  QTableWidget()
        self.result_display.setColumnCount(2)
        self.result_display.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_display.setColumnWidth(0, 300) 
        # self.result_display.setHorizontalHeaderLabels(['属性', '值'])
        self.result_display.horizontalHeader().hide()  #隐藏表格的水平表头
        self.result_display.verticalHeader().hide()   #隐藏表格的垂直表头
        self.result_display.horizontalHeader().setSectionsMovable(True)
        self.result_display.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)

        result_display_layout.addWidget(self.result_display)
        result_log_layout.addLayout(result_display_layout,5)

        log_display_layout = QVBoxLayout()
        self.log_display_label = QLabel("Log:")
        log_display_layout.addWidget(self.log_display_label)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: white; color: black; border: 1px solid #5f68c3; border-radius: 30px; padding-left: 15px;")
        log_display_layout.addWidget(self.log_display)
        result_log_layout.addLayout(log_display_layout,1)

        result_log_scroll_area.setLayout(result_log_layout)
        layout.addWidget(result_log_scroll_area,2)

        self.setLayout(layout)

    def start_task(self, event=None):
        self.start_button.setEnabled(False)  # 将按钮设置为不可点击
        self.log_display.append(f"开始查询")
        self.result_display.clearContents()
        self.result_display.setRowCount(0)
        domain_text = self.domain_input.text()
        if domain_text:
            self.thread1 = WhoisWorkerThread(domain_text)
            self.thread1.finished.connect(self.handle_thread_finished)
            self.thread1.start()
        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("请提供有效的域名")
            return
        
    def handle_thread_finished(self,result):
        self.result = result
        self.start_button.setEnabled(True)  # 将按钮设置为可点击
        
        for i, (key, value) in enumerate(result.items()):
            if value:
                if key in self.key_translation:
                    key = self.key_translation[key]
                else:
                    key = key.capitalize()  # 如果没有映射，将首字母大写
                if isinstance(value, list):  # 如果值是列表
                    tmp_list = []
                    for i in value:
                        tmp_list.append(str(i))
                    content = "\n".join(tmp_list)
                    self.result_display.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                    row_position = self.result_display.rowCount()
                    self.result_display.insertRow(row_position)
                    self.result_display.setItem(row_position, 0, QTableWidgetItem(str(key)))

                    item = QTableWidgetItem(content)
                    self.result_display.setItem(row_position, 1, item)
                else:
                    row_position = self.result_display.rowCount()
                    self.result_display.insertRow(row_position)
                    self.result_display.setItem(row_position, 0, QTableWidgetItem(key))
                    item = QTableWidgetItem(str(value))
                    self.result_display.setItem(row_position, 1, item)
        self.log_display.append("查询成功")

    def export_txt(self, file_path):
        for i, (key, value) in enumerate(self.result.items()):
            if value:
                if key in self.key_translation:
                    key = self.key_translation[key]
                else:
                    key = key.capitalize()  # 如果没有映射，将首字母大写
                with open(file_path, 'a+') as f:
                    f.write( str(key) + ":  " + str(value) + "\n")

    def save_to_file(self, event=None):
        if self.result:
            file_format, _ = QFileDialog.getSaveFileName(self, '保存文件', '', 'Text Files (*.txt)')
            if file_format:
                self.export_txt(file_format)
                self.log_display.append(f"导出成功")
        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("没有数据可以导出")
  
class OtherWidget(QWidget):
    def __init__(self,basic_style):
        super().__init__()
        self.result = None
        self.basic_style = basic_style
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('工具')
        # self.resize(1200, 600)
        self.setStyleSheet(self.basic_style)
        layout = QVBoxLayout()

        text = QTextBrowser()
        # 设置打开外部链接的方式为在默认浏览器中打开
        text.setOpenExternalLinks(True)

        # 创建滚动区域并设置文本编辑框为其子部件
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 设置滚动区域自适应大小
        scroll_area.setWidget(text)  # 设置文本编辑框为滚动区域的子部件
        scroll_area.setStyleSheet(scroll_style)

        text.setHtml("""
        <br>
        <p> whois查询: </p> 
        <p> - 国外WHOIS信息查询地址: <a href='https://who.is/'> https://who.is/ </a> 支持whois,IP历史绑定的域名查询等</p>
        <p> - 站长之家: <a href='http://whois.chinaz.com/'>http://whois.chinaz.com/ </a> 支持whois,IP历史绑定的域名查询等</p>
        <br>
                     
        <p> 邮箱反查的网站: </p>
        <p> - 爱站长: <a href='https://whois.aizhan.com'> https://whois.aizhan.com</a></p>
        <p> - reversewhois: <a href='https://www.reversewhois.io'> https://www.reversewhois.io </a> </p>    
        <p> - viewdns.info: <a href='https://viewdns.info/reversewhois/'> https://viewdns.info/reversewhois/ </a> </p>
        <br>
                     
        <p> IP反查(IP历史绑定的域名) </p>
        <p> - viewdns.info: <a href='https://viewdns.info/reverseip'> https://viewdns.info/reverseip </a></p>
        <br>
        
        <p> 历史DNS解析记录:   </p>
        <p> - 在线域名信息查询，可获取网站报告: <a href='http://toolbar.netcraft.com/site_report'> http://toolbar.netcraft.com/site_report </a></p>
        <p> - dnsdumpster: <a href='https://dnsdumpster.com/'> https://dnsdumpster.com/ </a></p>
        <p> - 同时会输出whois信息: <a href='https://who.is/dns/'> https://who.is/dns/ </a></p>
        <br>    
                             
        """)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

class reverseipWidget(QWidget):
    def __init__(self,basic_style):
        super().__init__()
        self.result = None
        self.basic_style = basic_style
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('ip反查域名')
        # self.resize(1200, 600)
        self.setStyleSheet(self.basic_style)
        layout = QVBoxLayout()

        # 第一排输入框和按钮
        options_layout = QHBoxLayout()
        self.port_input_label = QLabel("IP:")
        options_layout.addWidget(self.port_input_label)
        self.domain_input = QLineEdit()
        self.domain_input.setFixedHeight(62)
        self.domain_input.setPlaceholderText("请输入有效的IP")
        options_layout.addWidget(self.domain_input)

        self.start_button = QPushButton('查询')
        self.start_button.setFixedWidth(100)
        self.start_button.setFixedHeight(62)
        
        options_layout.addWidget(self.start_button)
        self.start_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.start_button.clicked.connect(self.start_task)

        self.save_to_file_button = QPushButton('导出')
        self.save_to_file_button.setFixedWidth(100)
        self.save_to_file_button.setFixedHeight(62)
        options_layout.addWidget(self.save_to_file_button)
        self.save_to_file_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_to_file_button.clicked.connect(self.save_to_file)

        layout.addLayout(options_layout,1)

        
        # 显示结果和日志
        result_log_scroll_area = QScrollArea()
        # 设置无边框样式
        result_log_scroll_area.setStyleSheet("border: none;")
        
        result_log_layout = QHBoxLayout()
        result_log_scroll_area.setWidgetResizable(True)

        result_display_layout = QVBoxLayout()
        self.result_display_label = QLabel("Results:")
        result_display_layout.addWidget(self.result_display_label)

        self.result_display =  QTextEdit()

        result_display_layout.addWidget(self.result_display)
        result_log_layout.addLayout(result_display_layout,5)

        log_display_layout = QVBoxLayout()
        self.log_display_label = QLabel("Log:")
        log_display_layout.addWidget(self.log_display_label)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: white; color: black; border: 1px solid #5f68c3; border-radius: 30px; padding-left: 15px;")
        log_display_layout.addWidget(self.log_display)
        result_log_layout.addLayout(log_display_layout,1)

        result_log_scroll_area.setLayout(result_log_layout)
        layout.addWidget(result_log_scroll_area,2)

        self.setLayout(layout)

    def start_task(self, event=None):
        self.start_button.setEnabled(False)  # 将按钮设置为不可点击

        self.result_display.clear()
        self.log_display.append("开始查询")
        domain_text = self.domain_input.text()
        
        if domain_text:
            self.thread1 = ReverseIpThread(domain_text,self.result_display,self.log_display)
            self.thread1.finished.connect(self.handle_thread_finished)
            self.thread1.start()
        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("请提供有效的邮箱")
            return
        
    def handle_thread_finished(self,result):
        self.result = result
        self.start_button.setEnabled(True)  # 将按钮设置为可点击
        self.log_display.append("查询成功")

    def export_text(self, file_path):  
        for i, (key, value) in enumerate(self.result.items()):
            if value:
                with open(file_path, 'a+') as f:
                    f.write( str(key) + ":  " + str(value) + "\n")

    def save_to_file(self, event=None):
        if self.result:
            file_format, _ = QFileDialog.getSaveFileName(self, '保存文件', '', 'Text Files (*.txt)')
            if file_format:
                self.export_text(file_format)
                self.log_display.append(f"导出完成....")
        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("没有数据可以导出....")

class MainWindow(QMainWindow):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style

        self.setWindowTitle("oneforall")
        self.setGeometry(300, 100, 2000, 1200)  # 设置窗口大小
        self.setStyleSheet("background-color: white;")  # 设置背景色
        # 界面字体大小设置
        font = QFont("Microsoft YaHei", 14)  # 字体和大小
        QApplication.setFont(font)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.function_tabs = QTabWidget()
        self.whois = WhoisWidget(self.basic_style)
        self.other = OtherWidget(self.basic_style)
        self.reverseip = reverseipWidget(self.basic_style)

    def create_layout(self):
        central_widget = QWidget()

        central_widget.setStyleSheet("background-color: white")  #设置渐变背景色

        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.function_tabs)
        self.setCentralWidget(central_widget)
    # 样式设置
    def create_connections(self):
        font = QFont("Helvetica Neue", 12)  # 字体和大小
        QApplication.setFont(font)

        # 设置窗口背景色
        self.setStyleSheet("background-color: #ffffff;")

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
        self.function_tabs.addTab(self.whois, QIcon(this_dir+"/icon/text.png"), "whois查询")
        self.function_tabs.addTab(self.reverseip, QIcon(this_dir+"/icon/config.png"), "ip反查域名")
        self.function_tabs.addTab(self.other, QIcon(this_dir+"/icon/config.png"), "其他")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
