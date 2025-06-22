import json
import os
import random
import re
import string
import sys
from itertools import chain
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QLabel, QTextEdit, QListWidget, QListWidgetItem, QSplitter, QFileDialog,QCheckBox,QLineEdit, QComboBox,QMessageBox
from PyQt5.QtGui import QFont, QIcon, QColor, QCursor, QPixmap
from PyQt5.QtCore import Qt, QUrl ,QSize, QThread, pyqtSignal

from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import tldextract
import re
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

class WorkerThread(QThread):
    finished = pyqtSignal(dict)
    def __init__(self, current_type,input,proxy):
        super().__init__()
        self.input = input
        self.proxy = proxy
        self.current_type = current_type

    def run(self):
        if self.current_type == "用户输入":
            url_external_links_dict = self.get_external_links(self.input)
            if url_external_links_dict:
                for urls , external_links in url_external_links_dict.items():
                    subdomains = self.find_subdomain(external_links["external_links"])
                    url_external_links_dict[urls]["subdomains"] = subdomains
            else:
                url_external_links_dict[self.input]["subdomains"] = []
        else:
            url_external_links_dict = {}
            with open(self.input, "r") as fobject:
                links = fobject.read().split("\n")
            if links == []:
                return None
            for link in links:
                data = self.get_external_links(link)
                if data:
                    url_external_links_dict.update(data) 
                    for urls , external_links in data.items():
                        subdomains = self.find_subdomain(external_links["external_links"])
                        url_external_links_dict[urls]["subdomains"] = subdomains
        self.finished.emit(url_external_links_dict)
    def get_external_links(self, url):
        result = {}
        result[url] = {}
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc
        main_domain = '.'.join(base_domain.split('.')[-2:])  # 提取主域名（如 toscrape.com）
        external_links = set()

        try:
            response = requests.get(url, verify=False, timeout=10, proxies=self.proxy)
            soup = BeautifulSoup(response.content, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                
                # 跳过无效链接
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue

                # 处理相对路径（转换为绝对路径）
                if not href.startswith(('http://', 'https://')):
                    href = requests.compat.urljoin(url, href)

                parsed_href = urlparse(href)
                if not parsed_href.netloc:  # 跳过无域名的链接
                    continue

                # 判断是否为外链（主域名不同）
                href_domain = parsed_href.netloc
                if not href_domain.endswith(main_domain):  # 检查是否为主域名的子域名
                    external_links.add(href)

        except Exception as e:
            print(f"An error occurred: {e}")
            return result

        result[url]["external_links"] = external_links
        return result

    def find_last(self, string, str):
        positions = []
        last_position = -1
        while True:
            position = string.find(str, last_position + 1)
            if position == -1:
                break
            last_position = position
            positions.append(position)
        return positions

    def find_subdomain(self, urls):
        url_raw = urlparse(self.input)
        domain = url_raw.netloc
        main_domain = '.'.join(domain.split('.')[-2:])  # 提取主域名（如 example.com）

        subdomains = []
        for url in urls:
            parsed_url = urlparse(url)
            subdomain = parsed_url.netloc

            if not subdomain or subdomain == main_domain:
                continue

            # 检查是否是当前域名的子域名
            if subdomain.endswith(main_domain):
                if subdomain not in subdomains:
                    subdomains.append(subdomain)

        return subdomains

class get_external_links(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.result_dict = {}  #保存结果
        self.basic_style = basic_style
        self.combo_box_style = combo_box_style

        self.setWindowTitle('External Links Extractor')
        self.setWindowIcon(QIcon(this_dir+'/icon.png'))
        
        self._font = QFont()  
        self._font.setPointSize(12)
        # self._font.setBold(True)  #加粗
        self._font.setFamily("Microsoft YaHei")
        
        self.setStyleSheet(self.basic_style)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('jsFinder')
        self.resize(1400, 900)
        self.setFont(QFont("微软雅黑", 12))

        self.input_format_label = QLabel('输入形式:')
        self.input_format_label.setFont(self._font)
        self.input_format_combo = QComboBox()
        self.input_format_combo.setStyleSheet(self.combo_box_style)
        self.input_format_combo.setFont(QFont("Arial", 12))
        self.input_format_combo.addItem('用户输入')
        self.input_format_combo.addItem('文件')
        self.input_format_combo.currentIndexChanged.connect(self.toggle_input_options)
        self.input_format_combo.setFixedWidth(180)
        self.input_format_combo.setFixedHeight(40)

        # 保存形式选择下拉框和文件保存位置
        self.save_format_label = QLabel('结果保存形式:')
        self.save_format_label.setFont(self._font)
        self.save_format_combo = QComboBox()
        self.save_format_combo.setStyleSheet(self.combo_box_style)
        self.save_format_combo.setFont(QFont("Arial", 12))
        self.save_format_combo.addItem('输出到界面')
        # self.save_format_combo.addItem('保存到文件')
        # self.save_format_combo.currentIndexChanged.connect(self.toggle_output_options)
        self.save_format_combo.setFixedWidth(180)
        self.save_format_combo.setFixedHeight(40)

        self.export_button = QPushButton("导出")
        self.export_button.setFixedWidth(100)
        self.export_button.setFixedHeight(58)
        self.export_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.export_button.clicked.connect(self.export_data)

        # 输入域名和可选项
        self.domain_label = QLabel('url:')
        self.domain_label.setFont(self._font)
        self.url_input = QLineEdit()
        self.url_input.setFixedHeight(40)
        self.url_input.returnPressed.connect(self.get_set)  # 绑定回车事件

        self.generate_button = QPushButton('查询')
        self.generate_button.setFont(self._font)
        self.generate_button.setFixedWidth(100)
        self.generate_button.setFixedHeight(62)
        self.generate_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.generate_button.clicked.connect(self.get_set)

        optional_layout = QHBoxLayout()
        self.proxy_label = QLabel('proxy:')
        self.proxy_label.setFont(self._font)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText('可选')
        self.proxy_input.setFixedHeight(40)

        optional_layout.addWidget( self.proxy_label)
        optional_layout.addWidget(self.proxy_input)

        # 显示结果
        self.result_layout = QHBoxLayout()
        # 左侧显示区域-url
        self.url_layout = QVBoxLayout()
        self.result_display_label = QLabel('外链结果:')
        self.result_display_label.setFont(self._font)
        self.result_url_display = QTextEdit()
        self.result_url_display.setReadOnly(True)
        self.url_layout.addWidget(self.result_display_label)
        self.url_layout.addWidget(self.result_url_display)

        # 右侧显示区域-subdomain
        self.subdomain_layout = QVBoxLayout()
        self.subdomain_display_label = QLabel('子域名结果:')
        self.subdomain_display_label.setFont(self._font)
        self.result_sumdomain_display = QTextEdit()
        self.result_sumdomain_display.setReadOnly(True)
        self.subdomain_layout.addWidget(self.subdomain_display_label)
        self.subdomain_layout.addWidget(self.result_sumdomain_display)

        # 把左右布局添加到result_layout中
        self.result_layout.addLayout(self.url_layout, 4)
        self.result_layout.addLayout(self.subdomain_layout, 2)

        # 设置主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout_format = QHBoxLayout()
        # layout_format.addStretch(1)  # 添加一个弹簧，让其第一行靠右展示
        layout_format.addWidget(self.input_format_label)
        layout_format.addWidget(self.input_format_combo)
        layout_format.addWidget(self.save_format_label)
        layout_format.addWidget(self.save_format_combo)
        layout_format.addWidget(self.export_button)
        layout_format.addStretch(1)  # 添加一个弹簧，让其第一行居中展示

        layout.addLayout(layout_format)

        layout_file = QHBoxLayout()
        layout.addLayout(layout_file)

        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.url_input)
        domain_layout.addWidget(self.generate_button)

        layout.addLayout(domain_layout)
        layout.addLayout(optional_layout)

        layout.addLayout(self.result_layout)

        self.setLayout(layout)

    def toggle_input_options(self, index):
        if index == 0:  # 输入
            self.domain_label.setText('url:')
            self.url_input.clear()
            self.url_input.setPlaceholderText('')
            self.url_input.setEchoMode(QLineEdit.Normal)  # 恢复为正常输入模式
        elif index == 1:  # 文件
            self.domain_label.setText('文件:')
            self.url_input.clear()
            self.select_file()
            self.url_input.setReadOnly(True)  # 设置为只读状态，用户无法编辑其内容

    def select_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, '选择文件', '', 'Text Files (*.txt);;All Files (*)')
        if file_path:
            self.url_input.setText(file_path)  # 将选择的文件路径显示在输入框中

    def toggle_output_options(self, index):
        if index == 0:  # 输出到界面
            self.result_url_display.setVisible(True)
            self.result_url_display.clear()
            self.result_sumdomain_display.clear()
        elif index == 1:  # 保存到文件
            self.result_url_display.clear()
            self.result_url_display.setVisible(True)
            self.result_sumdomain_display.clear()

    def save_result_to_file(self, external_links, link, subdomains):

        now_time = datetime.now().strftime("%Y%m%d-%H%M%S")

        def extract_domain_or_ip(url):
            parsed_url = urlparse(url)
            if parsed_url.netloc:  # 如果 netloc 部分非空
                return parsed_url.netloc  # 返回域名
            elif parsed_url.hostname:  # 如果 hostname 部分非空
                return parsed_url.hostname  # 返回主机名
            else:
                return None

        ip_domain = extract_domain_or_ip(link)
        url_result_file_path = ip_domain + "_" + now_time + "_result.txt"
        for item in external_links:
            with open(url_result_file_path, "a+", encoding='utf-8') as fobject:
                fobject.write(item + "\n")

        for subdomain in subdomains:
            with open(url_result_file_path, "a+", encoding='utf-8') as fobject:
                fobject.write(subdomain + "\n")
        self.result_url_display.append("\n 结果已经保存到当前路径下: " + str(url_result_file_path))

    def get_set(self, event=None):
        self.generate_button.setEnabled(False)  # 将按钮设置为不可点击
        self.result_url_display.clear()
        self.result_sumdomain_display.clear()

        self.result_url_display.setTextColor(QColor("green"))
        self.result_url_display.setText("开始爬取")

        self.result_sumdomain_display.setTextColor(QColor("green"))
        # self.result_sumdomain_display.append("开始提取")

        current_type = self.input_format_combo.currentText()
        self.input = self.url_input.text()
        proxy = {"http":self.proxy_input.text(),"https":self.proxy_input.text()}  if self.proxy_input.text() else {}

        # 检查复选框是否被选中
        if current_type == "用户输入" and not self.input:
            QMessageBox.warning(self, '错误', '请提供url。')
            return
        if current_type == "文件" and not self.input:
            QMessageBox.warning(self, '错误', '请提供输入文件。')
            return

        self.thread1 = WorkerThread(current_type,self.input,proxy)
        self.thread1.finished.connect(self.handle_thread_finished)
        self.thread1.start()

    def handle_thread_finished(self,result_dict):
        if result_dict == None:
            self.result_url_display.append("[-] not find")
        
        self.result_dict = result_dict

        save_type = self.save_format_combo.currentIndex()
        content_url = ""
        content_subdomain = ""

        for input_url,urls in result_dict.items():   
            self.result_url_display.append("<font color='red'>" + input_url + " 共发现 " + str(len(urls["external_links"])) + " 个url</font>")
            for url in urls["external_links"]:
                content_url += url + "\n"
                if save_type == 0:  # 输出到界面:
                    self.result_url_display.append(url)
            
            self.result_sumdomain_display.append("<font color='red'>" + input_url + "共发现 " + str(len(urls["subdomains"])) + " 个子域</font>")        
            for subdomain in urls["subdomains"]:
                content_subdomain += subdomain + "\n"
                if save_type == 0:  # 输出到界面:
                    self.result_sumdomain_display.append(subdomain)

        if save_type == 1:   #输出到文件
            now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            url_result_file_path = now_time + "_external_links.json"
            for key,value in self.result_dict.items():
                self.result_dict[key]["external_links"] = list(self.result_dict[key]["external_links"])
                url_json_data = json.dumps(self.result_dict, indent=4)
                with open(url_result_file_path, "a+", encoding='utf-8') as fobject:
                    fobject.write(url_json_data)
            self.result_url_display.append("\n 结果已经保存到当前路径下: " + str(url_result_file_path))
        
        self.result_url_display.setTextColor(QColor("green"))
        self.result_url_display.append("查询完成")

        self.result_sumdomain_display.append("提取完成")
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击
    
    def export_data(self, event=None):
        if self.result_dict:
            now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            url_result_file_path = now_time + "_external_links.json"
            for key,value in self.result_dict.items():
                self.result_dict[key]["external_links"] = list(self.result_dict[key]["external_links"])
                url_json_data = json.dumps(self.result_dict, indent=4)
                with open(url_result_file_path, "a+", encoding='utf-8') as fobject:
                    fobject.write(url_json_data)
            
            QMessageBox.information(self, "导出提示",f"导出成功,文件: {url_result_file_path}")
        else:
            QMessageBox.warning(None, "警告", "没有数据可以导出", QMessageBox.Ok)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    basic_style="""
            QMainWindow, QPushButton,QLineEdit, QTextEdit,QCheckBox,QGroupBox,QListWidget,QTableWidget {color: black; font-family: '微软雅黑'; font-size: 12pt; }
            QLineEdit, QTextEdit {background-color: white; color: black; border:1px solid #5f68c3; border-radius: 15px; padding-left:10px;}
            QLabel, QCheckBox { font-family: '微软雅黑'; font-size: 12pt; color: #34499a; border: none; background: none;}
            QPushButton {
                /* background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0, stop: 0 #0c1dcd, stop: 1 #bd4ade); */
                /* border: 2px solid #65b5e9; */
                background: #353fbb;
                border: 2px solid #5f68c3;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                text-align: center;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0, stop: 0 #bd4ade, stop: 1 #0c1dcd);
                border: 2px solid #65b5e9;
            }
            QPushButton:pressed {
                background-color: #0c1dcd;
                border: 2px solid #65b5e9;
            }
            
            """
    combo_box_style = """
            /* 设置整个下拉框的样式 */
            QComboBox {
                border: 1px solid #5f68c3;  /* 设置边框样式 */
                border-radius: 10px;  /* 设置边框圆角 */
                padding: 1px 10px 1px 1px;  /* 设置内边距 */
                min-width: 8em;  /* 设置最小宽度 */
                background-color: white;  /* 设置背景色 */
                color: #34499a;  /* 设置字体颜色 */
                height: 45px;  /* 设置高度 */
                font-size: 20px;
            }

            /* 设置下拉箭头的样式 */
            QComboBox::down-arrow {
                image: url(%s/icon/down.png);  /* 替换为您想要的箭头图标路径 */
                height: 35px;  /* 设置箭头高度 */
            }

            /* 设置下拉按钮的样式 */
            QComboBox::drop-down {
                border: none;  /* 设置下拉按钮无边框 */
                background-color: white;  /* 设置下拉按钮背景色 */
                color: #fff;  /* 设置下拉按钮字体颜色 */
                margin: 5px;  /* 设置下拉按钮边距 */
            }
            /* 设置下拉选项的背景色和字体颜色 */
            QComboBox QAbstractItemView {
                background-color: #f0f0f0;  /* 下拉选项背景色 */
                color: #34499a;  /* 下拉选项字体颜色 */
            }
        """% (this_dir)
    window = get_external_links(basic_style,combo_box_style)
    window.show()
    sys.exit(app.exec_())