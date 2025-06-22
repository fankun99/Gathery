from PyQt5.QtWidgets import QApplication,  QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QLabel, QTextEdit, QFileDialog,QCheckBox,QLineEdit, QComboBox,QMessageBox
from PyQt5.QtGui import QFont, QColor, QCursor
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from datetime import datetime
from urllib.parse import urlparse
import re
import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import traceback
import urllib3
urllib3.disable_warnings()

import FunctionPage.common as common

this_dir = common.this_dir
combo_box_style = common.combo_box_style

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

class WorkerThread(QThread):
    finished = pyqtSignal(dict, dict)
    def __init__(self, save_type,current_type,input,deep,cookie,proxy):
        super().__init__()
        self.save_type = save_type
        self.input = input
        self.current_type = current_type
        self.deep = deep
        self.proxy = proxy
        self.cookie = cookie

    def run(self):
        if self.current_type == "用户输入":
            if self.deep is not True:
                url_result_dict = self.find_by_url(self.input)
                if url_result_dict:
                    for url, urls in url_result_dict.items():
                        domain_subdomains_dict = self.get_subdomains(urls, self.input)
                else:
                    domain_subdomains_dict = {}
            else:
                url_result_dict = self.find_by_url_deep(self.input)
                if url_result_dict:
                    for url, urls in url_result_dict.items():
                        domain_subdomains_dict = self.get_subdomains(urls, self.input)
                else:
                    domain_subdomains_dict = {}
        else:
            data = self.find_by_file(self.input)
            url_result_dict = {}
            domain_subdomains_dict = {}
            for url_data in data:
                url_result_dict.update(url_data)
                if url_data:
                    for url, urls in url_data.items():
                        subdomains_dict = self.get_subdomains(urls, urls[0])
                        if url in url_data:
                            # 将列表转换为集合，去除重复值，然后再转换回列表
                            domain_subdomains_dict[url] = list(set(domain_subdomains_dict[url] + subdomains_dict))
                        else:
                            domain_subdomains_dict[url] = subdomains_dict
                        # domain_subdomains_dict.update(subdomains_dict)

        self.finished.emit(url_result_dict, domain_subdomains_dict)
    
    def extract_URL(self,JS):
        pattern_raw = r"""
        (?:"|')                               # Start newline delimiter
        (
            ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
            [^"'/]{1,}\.                        # Match a domainname (any character + dot)
            [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
            |
            ((?:/|\.\./|\./)                    # Start with /,../,./
            [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
            [^"'><,;|()]{1,})                   # Rest of the characters can't be
            |
            ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
            [a-zA-Z0-9_\-/]{1,}                 # Resource name
            \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
            (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
            |
            ([a-zA-Z0-9_\-]{1,}                 # filename
            \.(?:php|asp|aspx|jsp|json|
                action|html|js|txt|xml)             # . + extension
            (?:\?[^"|']{0,}|))                  # ? mark with parameters
        )
        (?:"|')                               # End newline delimiter
        """
        pattern = re.compile(pattern_raw, re.VERBOSE)
        result = re.finditer(pattern, str(JS))
        if result == None:
            return None
        js_url = []
        return [match.group().strip('"').strip("'") for match in result
            if match.group() not in js_url]

    # Get the page source
    def Extract_html(self,URL):
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
        "Cookie": self.cookie}
        try:
            raw = requests.get(URL, headers = header, timeout=3, verify=False, proxies=self.proxy)
            raw = raw.content.decode("utf-8", "ignore")
            return raw
        except:
            traceback.print_exc()
            return None

    # Handling relative URLs
    def process_url(self,URL, re_URL):
        black_url = ["javascript:"]	# Add some keyword for filter url.
        URL_raw = urlparse(URL)
        ab_URL = URL_raw.netloc
        host_URL = URL_raw.scheme
        if re_URL[0:2] == "//":
            result = host_URL  + ":" + re_URL
        elif re_URL[0:4] == "http":
            result = re_URL
        elif re_URL[0:2] != "//" and re_URL not in black_url:
            if re_URL[0:1] == "/":
                result = host_URL + "://" + ab_URL + re_URL
            else:
                if re_URL[0:1] == ".":
                    if re_URL[0:2] == "..":
                        result = host_URL + "://" + ab_URL + re_URL[2:]
                    else:
                        result = host_URL + "://" + ab_URL + re_URL[1:]
                else:
                    result = host_URL + "://" + ab_URL + "/" + re_URL
        else:
            result = URL
        return result

    def find_last(self,string,str):
        positions = []
        last_position=-1
        while True:
            position = string.find(str,last_position+1)
            if position == -1:break
            last_position = position
            positions.append(position)
        return positions

    def find_by_url(self,url, js = False):
        url_result = {}
        if js == False:
            try:
                print("url:" + url)
            except:
                QMessageBox.warning(self, '错误', 'URL like https://www.baidu.com')
                return url_result
            html_raw = self.Extract_html(url)
            if html_raw == None: 
                print("Fail to access " + url)
                return url_result
            try:
                html = BeautifulSoup(html_raw, "html.parser")
                html_scripts = html.findAll("script")
                script_array = {}
                script_temp = ""
                for html_script in html_scripts:
                    script_src = html_script.get("src")
                    if script_src == None:
                        script_temp += html_script.get_text() + "\n"
                    else:
                        purl = self.process_url(url, script_src)
                        script_array[purl] = self.Extract_html(purl)
                script_array[url] = script_temp
                allurls = []
                for script in script_array:
                    #print(script)
                    temp_urls = self.extract_URL(script_array[script])
                    if len(temp_urls) == 0: continue
                    for temp_url in temp_urls:
                        allurls.append(self.process_url(script, temp_url)) 
                result = []
                for singerurl in allurls:
                    url_raw = urlparse(url)
                    domain = url_raw.netloc
                    positions = self.find_last(domain, ".")
                    miandomain = domain
                    if len(positions) > 1:miandomain = domain[positions[-2] + 1:]
                    #print(miandomain)
                    suburl = urlparse(singerurl)
                    subdomain = suburl.netloc
                    #print(singerurl)
                    if miandomain in subdomain or subdomain.strip() == "":
                        if singerurl.strip() not in result:
                            result.append(singerurl)
                url_result[url] = result
                return url_result    
            except:
                return url_result
        
        return sorted(set(self.extract_URL(self.Extract_html(url)))) or None

    def find_subdomain(self,urls, mainurl):
        domain_subdomains = {}
        url_raw = urlparse(mainurl)
        domain = url_raw.netloc
        miandomain = domain
        positions = self.find_last(domain, ".")
        if len(positions) > 1:miandomain = domain[positions[-2] + 1:]
        subdomains = []
        for url in urls:
            suburl = urlparse(url)
            subdomain = suburl.netloc
            #print(subdomain)
            if subdomain.strip() == "": continue
            if miandomain in subdomain:
                if subdomain not in subdomains:
                    subdomains.append(subdomain)
        domain_subdomains[domain] = subdomains
        return domain_subdomains

    def find_by_url_deep(self,url):
        url_result = {}
        html_raw = self.Extract_html(url)
        if html_raw == None: 
            print("Fail to access " + url)
            return url_result
        html = BeautifulSoup(html_raw, "html.parser")
        html_as = html.findAll("a")
        links = []
        for html_a in html_as:
            src = html_a.get("href")
            if src == "" or src == None: continue
            link = self.process_url(url, src)
            if link not in links:
                links.append(link)
        if links == []: return url_result
        print("ALL Find " + str(len(links)) + " links")
        i = len(links)
        for link in links:
            temp_urls = self.find_by_url(link)
            if temp_urls == None: continue
            # print("Remaining " + str(i) + " | Find " + str(len(temp_urls)) + " URL in " + link)
            url_result.update(temp_urls)
            i -= 1
        return url_result
        
    def find_by_file(self,file_path, js=False):
        urls = []
        try:
            with open(file_path, "r") as fobject:
                links = fobject.read().split("\n")
            if links == []: return None
            print("ALL Find " + str(len(links)) + " links")
            i = len(links)
            for link in links:
                if js == False:
                    temp_urls = self.find_by_url(link)
                    print("##",temp_urls)
                else:
                    temp_urls = self.find_by_url(link, js=True)
                if temp_urls == None: continue
                if temp_urls not in urls:
                    urls.append(temp_urls)
                i -= 1
        except:
            traceback.print_exc()

        return urls

    def get_subdomains(self,urls, domian):
        if urls == None:
            return {}
        domain_subdomains_dict = self.find_subdomain(urls, domian)
        return domain_subdomains_dict
        
class JSFinder(QWidget):
    def __init__(self,basic_style):
        super().__init__()
        self.urls_dict = {}
        self.subdomains_dict = {}
        self.basic_style = basic_style
        self.combo_box_style = combo_box_style
        self.setStyleSheet(self.basic_style)
        self._font = QFont()  
        self._font.setPointSize(12)
        self._font.setFamily("Microsoft YaHei")
        
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

        self.save_format_label = QLabel('结果形式:')
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

        # 输入url和可选项
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

        self.cookie_label = QLabel('cookie:')
        self.cookie_label.setFont(self._font)
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText('可选')
        self.cookie_input.setFixedHeight(40)

        self.proxy_label = QLabel('proxy:')
        self.proxy_label.setFont(self._font)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText('可选')
        self.proxy_input.setFixedHeight(40)

        self.deep_checkbox = QCheckBox('深度爬取')
        self.deep_checkbox.setFont(self._font)
        self.deep_checkbox.setChecked(False)
        self.deep_checkbox.setToolTip('深入一层页面爬取JS,时间会消耗的更长') #设置悬浮提示 

         # 显示结果的布局
        self.result_layout = QHBoxLayout()

        # 左侧显示区域-url
        self.url_layout = QVBoxLayout()
        self.result_display_label = QLabel('url结果:')
        self.result_display_label.setFont(self._font)
        self.result_url_display = QTextEdit()
        self.result_url_display.verticalScrollBar().setStyleSheet(scroll_style)
        self.result_url_display.setReadOnly(True)
        self.url_layout.addWidget(self.result_display_label)
        self.url_layout.addWidget(self.result_url_display)

        # 右侧显示区域-subdomain
        self.subdomain_layout = QVBoxLayout()
        self.subdomain_display_label = QLabel('子域名结果:')
        self.subdomain_display_label.setFont(self._font)
        self.result_sumdomain_display = QTextEdit()
        self.result_sumdomain_display.verticalScrollBar().setStyleSheet(scroll_style)
        self.result_sumdomain_display.setReadOnly(True)
        self.subdomain_layout.addWidget(self.subdomain_display_label)
        self.subdomain_layout.addWidget(self.result_sumdomain_display)

        # 把左右布局添加到result_layout中
        self.result_layout.addLayout(self.url_layout,5)
        self.result_layout.addLayout(self.subdomain_layout,2)
        
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
        layout_format.addStretch(1)
        
        layout.addLayout(layout_format)

        layout_file = QHBoxLayout()
        layout.addLayout(layout_file)

        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.url_input)
        domain_layout.addWidget(self.generate_button)

        layout.addLayout(domain_layout)

        optional_layout = QHBoxLayout()
        optional_layout.addWidget(self.cookie_label)
        optional_layout.addWidget(self.cookie_input)
        optional_layout.addWidget( self.proxy_label)
        optional_layout.addWidget(self.proxy_input)
        optional_layout.addWidget(self.deep_checkbox)

        layout.addLayout(optional_layout)
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

    def get_set(self, event=None):
        self.generate_button.setEnabled(False)  # 将按钮设置为不可点击
        self.result_sumdomain_display.clear()
        self.result_url_display.clear()

        current_type = self.input_format_combo.currentText()
        self.input = self.url_input.text()
        self.cookie = int(self.cookie_input.text()) if self.cookie_input.text() else None
        proxy = {"http":self.proxy_input.text(),"https":self.proxy_input.text()}  if self.proxy_input.text() else {}

        # 检查复选框是否被选中
        deep = True if self.deep_checkbox.isChecked() else False
        if current_type == "用户输入" and not self.input:
            QMessageBox.warning(self, '错误', '请提供url。')
            return
        if current_type == "文件" and not self.input:
            QMessageBox.warning(self, '错误', '请提供输入文件。')
            return 
        
        self.result_url_display.setTextColor(QColor("green"))
        self.result_url_display.setText("开始查询")
        self.result_sumdomain_display.setTextColor(QColor("green"))
        # self.result_sumdomain_display.append("开始提取")

        save_type = self.save_format_combo.currentIndex()
        self.thread1 = WorkerThread(save_type,current_type,self.input,deep,self.cookie,proxy)
        self.thread1.finished.connect(self.handle_thread_finished)
        self.thread1.start()
    
    def handle_thread_finished(self,urls_dict,subdomains_dict):
        if urls_dict == None:
            self.result_url_display.append("[-] not find")
        
        self.urls_dict = urls_dict
        self.subdomains_dict = subdomains_dict
        
        save_type = self.save_format_combo.currentIndex()
        content_url = ""
        content_subdomain = ""
        for input_url,urls in urls_dict.items():   
            self.result_url_display.append("<font color='red'>" + input_url + " 共发现 " + str(len(urls)) + " 个url</font>")
            for url in urls:
                content_url += url + "\n"
                if save_type == 0:  # 输出到界面:
                    self.result_url_display.append(url)

        for input_url,subdomains in subdomains_dict.items():
            self.result_sumdomain_display.append("<font color='red'>" + input_url + "共发现 " + str(len(subdomains)) + " 个子域</font>")
            for subdomain in subdomains:
                content_subdomain += subdomain + "\n"
                if save_type == 0:  # 输出到界面:
                    self.result_sumdomain_display.append(subdomain)

        if save_type == 1:   #输出到文件
            now_time = datetime.now().strftime("%Y%m%d-%H%M%S")

            subdomain_result_file_path = now_time + "_subdomain.json"
            url_result_file_path = now_time + "_urls.json"

            url_json_data = json.dumps(self.urls_dict, indent=4)
            subdomain_json_data = json.dumps(self.subdomains_dict, indent=4)

            with open(url_result_file_path, "a+", encoding='utf-8') as fobject:
                fobject.write(url_json_data)
            with open(subdomain_result_file_path, "a+", encoding='utf-8') as f:
                f.write(subdomain_json_data)
            self.result_url_display.append("\n 结果已经保存到当前路径下: " + str(url_result_file_path))
            self.result_url_display.append("\n 子域名结果已经保存到当前路径下: " + str(subdomain_result_file_path))
        
        self.result_url_display.setTextColor(QColor("green"))
        self.result_url_display.append("查询完成")
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击

    def export_data(self, event=None):
        if self.urls_dict:
            now_time = datetime.now().strftime("%Y%m%d-%H%M%S")

            subdomain_result_file_path = now_time + "_subdomain.json"
            url_result_file_path = now_time + "_urls.json"

            subdomain_json_data = json.dumps(self.subdomains_dict, indent=4)
            url_json_data = json.dumps(self.urls_dict, indent=4)

            with open(url_result_file_path, "a+", encoding='utf-8') as fobject:
                fobject.write(url_json_data)
            with open(subdomain_result_file_path, "a+", encoding='utf-8') as f:
                f.write(subdomain_json_data)
            QMessageBox.information(self, "导出提示",f"导出成功,url文件: {url_result_file_path}\n子域名文件: {subdomain_result_file_path}")
        else:
            QMessageBox.warning(None, "警告", "没有数据可以导出", QMessageBox.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JSFinder()
    window.show()
    sys.exit(app.exec_())
