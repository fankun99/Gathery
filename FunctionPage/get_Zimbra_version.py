import random
import re
import string
import sys
from itertools import chain
import threading
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QLabel, QTextEdit, QListWidget, QListWidgetItem, QSplitter, QFileDialog,QCheckBox,QLineEdit, QComboBox,QMessageBox
from PyQt5.QtGui import QFont, QIcon, QColor, QCursor, QPixmap

from PyQt5.QtCore import Qt, QUrl ,QSize, QThread, pyqtSignal
from datetime import datetime
from urllib.parse import urlparse
import requests
import re
import urllib3
import socket
import ssl
urllib3.disable_warnings()

class WorkerThread(QThread):
    finished = pyqtSignal(dict)
    def __init__(self, save_type,current_type,input):
        super().__init__()
        self.save_type = save_type
        self.input = input
        self.current_type = current_type
        self.last_result = {}

    def run(self):
        if self.current_type == "用户输入":
            url = self.input
            if url[-1] == "/":
                url = url[:-1]
            if url:
                web_result = self.getversionweb(url)
                port,result = self.getversionimap(url)
                if len(result) == 0:
                    port,result = self.getversionimapoverssl(url)
                self.last_result[url] = {
                    "web_result" : web_result,
                    "port": str(port),
                    "result":result
                }
        else:
            urls = self.find_by_file(self.input)
            print("get urls:",urls)
            for url in urls:
                print("get url: " ,url)
                web_result = self.getversionweb(url)
                port,result = self.getversionimap(url)
                if len(result) == 0: 
                    port,result = self.getversionimapoverssl(url)
                self.last_result[url] = {
                    "web_result" : web_result,
                    "port": str(port),
                    "result":result
                }
        self.finished.emit(self.last_result)

    def find_by_file(self,file_path):
        with open(file_path, "r") as fobject:
            links= fobject.read().split("\n")
        return links    
    
    def getversionweb(self,url):
        try:  
            url = url + "/js/zimbraMail/share/model/ZmSettings.js"
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
            }
            response = requests.get(url, headers=headers, verify=False, timeout=5)

            if response.status_code == 200 and 'CLIENT_RELEASE' in response.text:
                VERSION_name = re.compile(r"CLIENT_VERSION\",					{type:ZmSetting.T_CONFIG, defaultValue:\"(.*?)\"}\);")
                CLIENT_VERSION = VERSION_name.findall(response.text)
                RELEASE_name = re.compile(r"CLIENT_RELEASE\",					{type:ZmSetting.T_CONFIG, defaultValue:\"(.*?)\"}\);")
                CLIENT_RELEASE = RELEASE_name.findall(response.text)
                result = "[+] Version: " + CLIENT_VERSION[0] + "    Release: " + CLIENT_RELEASE[0]
                return result
            else:
                result = ""
                return result
        except Exception as e:
            result = ""
            return result 

    def getversionimap(self,url):
        try:
            parsed_url = urlparse(url)
            ip = parsed_url.hostname
        except:
            return 443,""
        try:
            # print("[*] Try to connect: " + ip + ":143")
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((ip, 143))
            s.sendall(''.encode())
            response = s.recv(1024)
            if "OK" in response.decode('UTF-8'):
                pass
                print(" ok")
            else:
                s.close()
            s.sendall('A001 ID NIL\r\n'.encode())
            response = s.recv(1024)
            if "Zimbra" in response.decode('UTF-8'):
                versiondata=re.compile(r"VERSION\" \"(.*?)\"")
                version = versiondata.findall(response.decode('UTF-8'))[0]
                releasedata=re.compile(r"RELEASE\" \"(.*?)\"")
                release = releasedata.findall(response.decode('UTF-8'))[0]
                result = "[+] Version: " + version + "    Release: " + release
                return 443,result
            else:
                s.close()
            return 443,""
        except Exception as e:
            return 443,""
    
    def getversionimapoverssl(self,url):
        try:
            parsed_url = urlparse(url)
            # 获取主机名
            ip = parsed_url.hostname
        except:
            return 993,""
        try:
            hostname = socket.gethostbyaddr(ip)
            print("[*] Try to connect: " + hostname[0] + ":993")
            context = ssl.create_default_context()
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s = context.wrap_socket(s, server_hostname=hostname[0])
            s.settimeout(5)
            s.connect((ip, 993))
            s.sendall(''.encode())
            response = s.recv(1024)
            if "OK" in response.decode('UTF-8'):
                pass
            else:
                s.close()
            s.sendall('A001 ID NIL\r\n'.encode())
            response = s.recv(1024)
            if "Zimbra" in response.decode('UTF-8'):
                versiondata=re.compile(r"VERSION\" \"(.*?)\"")
                version = versiondata.findall(response.decode('UTF-8'))[0]
                releasedata=re.compile(r"RELEASE\" \"(.*?)\"")
                release = releasedata.findall(response.decode('UTF-8'))[0]
                result = "[+] Version: " + version + "    Release: " + release
                return 993,result
            else:
                s.close()
            return 993,""
        except Exception as e:
            print("[-] 错误:" + str(e))
            return 993,""      

class get_Zimbra_version(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style
        self.setStyleSheet(self.basic_style)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('get_fortigate_version')
        self.resize(1400, 900)
        self.setFont(QFont("微软雅黑", 12))

        self.input_format_label = QLabel('输入形式:')

        self.input_format_combo = QComboBox()
        self.input_format_combo.setStyleSheet(self.combo_box_style)
        self.input_format_combo.addItem('用户输入')
        self.input_format_combo.addItem('文件')
        self.input_format_combo.currentIndexChanged.connect(self.toggle_input_options)
        self.input_format_combo.setFixedWidth(180)
        self.input_format_combo.setFixedHeight(40)
        # self.input_format_combo.setFont(self._font) 

        self.save_format_label = QLabel('结果形式:')
        self.save_format_combo = QComboBox()
        self.save_format_combo.setStyleSheet(self.combo_box_style)
        self.save_format_combo.addItem('输出到界面')
        # self.save_format_combo.addItem('保存到文件')
        # self.save_format_combo.currentIndexChanged.connect(self.toggle_output_options)
        self.save_format_combo.setFixedWidth(180)
        self.save_format_combo.setFixedHeight(40)

        # 输入url和可选项
        self.domain_label = QLabel('url:')
        self.url_input = QLineEdit()
        self.url_input.setFixedHeight(40)
        self.url_input.returnPressed.connect(self.get_set)  # 绑定回车事件

        self.generate_button = QPushButton('查询')
        self.generate_button.setFixedWidth(100)
        self.generate_button.setFixedHeight(62)
        self.generate_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.generate_button.clicked.connect(self.get_set)

         # 显示结果的布局
        self.result_layout = QHBoxLayout()

        # 左侧显示区域-url
        self.url_layout = QVBoxLayout()
        self.result_display_label = QLabel('结果:')
        self.result_url_display = QTextEdit()
        self.result_url_display.setReadOnly(True)
        self.url_layout.addWidget(self.result_display_label)
        self.url_layout.addWidget(self.result_url_display)

        # 把左右布局添加到result_layout中
        self.result_layout.addLayout(self.url_layout)
        
        # 设置主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout_format = QHBoxLayout()
        # layout_format.addStretch(1)  # 添加一个弹簧，让其第一行靠右展示
        layout_format.addWidget(self.input_format_label)
        layout_format.addWidget(self.input_format_combo)
        layout_format.addWidget(self.save_format_label)
        layout_format.addWidget(self.save_format_combo)
        layout_format.addStretch(1)
        
        layout.addLayout(layout_format)

        layout_file = QHBoxLayout()
        layout.addLayout(layout_file)

        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.url_input)
        domain_layout.addWidget(self.generate_button)

        layout.addLayout(domain_layout)

        layout.addLayout(self.result_layout)
        
        self.setLayout(layout)

    def toggle_input_options(self, index):
        if index == 0:  # 输入
            self.domain_label.setText('url:')
            self.url_input.clear()
            self.url_input.setPlaceholderText('')
            self.url_input.setEchoMode(QLineEdit.Normal)  # 恢复为正常输入模式
        elif index == 1:  # 来着文件
            self.domain_label.setText('文件:')
            self.url_input.clear()
            self.select_file()
            self.url_input.setReadOnly(True) #设置为只读状态，用户无法编辑其内容

    def select_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, '选择文件', '', 'Text Files (*.txt);;All Files (*)')
        if file_path:
            self.url_input.setText(file_path)  # 将选择的文件路径显示在输入框中   

    def toggle_output_options(self, index):
        if index == 0:  # 输出到界面
            self.result_url_display.setVisible(True)
            self.result_url_display.clear()
        elif index == 1:  # 保存到文件
            self.result_url_display.clear()
            self.result_url_display.setVisible(True)

    def save_result_to_file(self,url,web_result,result):
        now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.url_result_file_path = now_time + "_urls_subdomain.txt"
        with open(self.url_result_file_path, "a+", encoding='utf-8') as fobject:
            if len(result) > 0 or len(web_result) > 0:
                fobject.write("[+] " +url + "\n" + "web result:" + web_result + "\n" + result + "\n")
            else:
                fobject.write("[-] " + str(url) + " not find" + "\n")

    def get_set(self, event=None):
        self.generate_button.setEnabled(False)  # 将按钮设置为不可点击
        self.result_url_display.clear()
        self.result_url_display.setTextColor(QColor("green"))
        self.result_url_display.append("start....")
        QApplication.processEvents()  # 立即处理事件循环，以确保新内容立即显示

        current_type = self.input_format_combo.currentText()
        self.input = self.url_input.text()
        
        # 检查复选框是否被选中
        if current_type == "用户输入" and not self.input:
            QMessageBox.warning(self, '错误', '请提供url。')
            self.result_url_display.append("finish!!")
            return
        if current_type == "文件" and not self.input:
            QMessageBox.warning(self, '错误', '请提供输入文件。')
            self.result_url_display.append("finish")
            return
       
        save_type = self.save_format_combo.currentIndex()
        self.thread1 = WorkerThread(save_type,current_type,self.input)
        self.thread1.finished.connect(self.handle_thread_finished)
        self.thread1.start()
    
    def handle_thread_finished(self,result):
        save_type = self.save_format_combo.currentIndex()
        if save_type == 1:   #输出到文件
            for url, value in result.items():
                self.save_result_to_file(url,value["web_result"],value["result"])
            self.result_url_display.append("\n 结果已经保存到当前路径下: " + str(self.url_result_file_path))
        else:
            for url, value in result.items():
                port = str(value["port"])
                if value["result"] !="":
                    self.result_url_display.append('<font color="red">[+]  ' + str(url) + "\n" + "---> web_result:" + value["web_result"] + "\n" + f"---> {str(port)}_result:" + value["result"])
                elif len(value["web_result"]) > 0:
                    self.result_url_display.append("[+] " + str(url) + "---> web_result:" + value["web_result"]  + f"{str(port)}_result:" + value["result"])
                else:
                    self.result_url_display.append('<font color="green">[-] ' + str(url) + ' not find</font>')
        self.result_url_display.setTextColor(QColor("green"))
        self.result_url_display.append("finish")
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = get_Zimbra_version()
    window.show()
    sys.exit(app.exec_())