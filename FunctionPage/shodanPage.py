from datetime import datetime
import json
import os
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QPushButton, QComboBox, \
    QTextEdit, QHBoxLayout, QCheckBox, QLineEdit,QFileDialog,QGroupBox,QScrollArea,QMessageBox,\
    QListWidget,QTableWidget,QHeaderView,QTableWidgetItem,QAbstractItemView,QGridLayout,QSizePolicy,\
    QListWidgetItem

from PyQt5.QtGui import QFont, QCursor,QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import configparser
import requests
import urllib3
from googletrans import Translator
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

class ShodanHostThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, model,input,api_key,proxy):
        super().__init__()
        self.model = model
        self.input = input
        self.api_key = api_key
        self.proxy = proxy
        self.data_list  = []

    def run(self):
        result = {}
        if self.model == "input":
            url = f"https://api.shodan.io/shodan/host/{self.input}?key={self.api_key}"
            # print("get url:",url)
            if url:
                try:
                    response = requests.get(url, verify=False, timeout=10, proxies=self.proxy)
                    json_data = response.json()
                    result[self.input] = json_data
                except:
                    result[self.input] = {}
        else:
            with open(self.input, "r") as f:
                Ips = f.read().split("\n")
            if Ips == []:
                return None
            for Ip in Ips:
                ip = Ip.strip()
                if len(ip) > 0:
                    try:
                        url = f"https://api.shodan.io/shodan/host/{ip}?key={self.api_key}"
                        response = requests.get(url, verify=False, timeout=10, proxies=self.proxy)
                        json_data = response.json()
                        result[Ip] = json_data
                    except:
                        result = {}
        self.data_list.append(result)        
        self.finished.emit(self.data_list)

class ShodanDomainThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, model,input,api_key,proxy):
        super().__init__()
        self.model = model
        self.input = input
        self.api_key = api_key
        self.proxy = proxy
        self.data_list  = []

    def run(self):
        result = {}
        if self.model == "input":
            url = f"https://api.shodan.io/dns/domain/{self.input}?key={self.api_key}"
            # print("get url:",url)
            if url:
                try:
                    response = requests.get(url, verify=False, timeout=10, proxies=self.proxy)
                    json_data = response.json()
                    result[self.input] = json_data
                except:
                    result = {}
                    traceback.print_exc()
        else:
            with open(self.input, "r") as f:
                Domains = f.read().split("\n")
            if Domains == []:
                return None
            for domain in Domains:
                domain = domain.strip()
                if len(domain) > 0:
                    try:
                        url = f"https://api.shodan.io/dns/domain/{domain}?key={self.api_key}"
                        response = requests.get(url, verify=False, timeout=10, proxies=self.proxy)
                        json_data = response.json()
                        result[domain] = json_data
                    except:
                        result = {}
                        traceback.print_exc()
        self.data_list.append(result)        
        self.finished.emit(self.data_list)    

class NVDGetVulnInfoThread(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, cve_id,proxy):
        super().__init__()
        self.cve_id = cve_id
        self.proxy = proxy
        self.result_dict = {}
    
    def run(self):
        api_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={self.cve_id}"
        response = requests.get(api_url,verify=False,timeout=10,proxies=self.proxy)
        if response.status_code == 200:
            cve_data = response.json()
            self.result_dict = cve_data
            try:
                for key ,value in self.result_dict.items():
                    if key == "vulnerabilities":
                        for item in value:
                            Description =  item.get("cve").get("descriptions")[0].get("value")
                            try:
                                self. translator = Translator(proxies=self.proxy,timeout=5)
                                Description_data = self.translate(Description)
                                if Description_data:
                                    item.get("cve").get("descriptions")[0]["value"] = Description + "\n"  + Description_data
                            except:
                                traceback.print_exc()
                                pass
            except:
                traceback.print_exc()
                self.result_dict = cve_data   
        else:
            self.result_dict = {}
        self.finished.emit(self.result_dict)    
    def translate(self,str, dest="zh-CN"):
        trans_result = self.translator.translate(str, dest)
        print(trans_result.text)
        return trans_result.text

class ShodanIpThread(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, model,input,api_key,proxy):
        super().__init__()
        self.model = model
        self.input = input
        self.api_key = api_key
        self.proxy = proxy
        self.data_dict = {}

    def run(self):
        if self.model == "input":
            url = f"https://internetdb.shodan.io/{self.input}"
            # print("get url:",url)
            if url:
                try:
                    response = requests.get(url, verify=False, timeout=10, proxies=self.proxy)
                    json_data = response.json()
                    self.data_dict[self.input] = json_data
                except:
                    self.data_dict[self.input] = {}
        else:
            with open(self.input, "r") as f:
                Ips = f.read().split("\n")
            if Ips == []:
                return None
            for Ip in Ips:
                ip = Ip.strip()
                if len(ip) > 0:
                    try:
                        url = f"https://internetdb.shodan.io/{ip}"
                        response = requests.get(url, verify=False, timeout=10, proxies=self.proxy)
                        json_data = response.json()
                        self.data_dict[Ip] = json_data
                    except:
                        self.data_dict = {}
        self.finished.emit(self.data_dict)

class ShodanIp(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style
        self.result_list = None
        self.result_dict = {}  #存储结果
        
        self.init_ui()
        self.setStyleSheet(self.basic_style)

    def init_ui(self):
        # 存储 IP 地址的集合
        self.ip_set = set()
        self.setWindowTitle('ShodanIp')
        # self.resize(1400, 900)
        self.setStyleSheet("background-color: #32337e;")

        self.input_format_label = QLabel('输入形式:')
        self.input_format_combo = QComboBox()
        self.input_format_combo.setStyleSheet(self.combo_box_style)
        self.input_format_combo.addItem('用户输入')
        self.input_format_combo.addItem('文件')
        self.input_format_combo.setFixedWidth(180)
        self.input_format_combo.setFixedHeight(40)
        self.input_format_combo.currentIndexChanged.connect(self.toggle_input_options) 

        self.save_format_label = QLabel('结果形式:')
        self.save_format_combo = QComboBox()
        self.save_format_combo.setStyleSheet(self.combo_box_style)
        self.save_format_combo.addItem('输出到界面再导出保存')
        # self.save_format_combo.addItem('保存到文件')
        self.save_format_combo.setFixedWidth(180)
        self.save_format_combo.setFixedHeight(40)

        self.export_button = QPushButton("导出")
        self.export_button.setFixedWidth(100)
        self.export_button.setFixedHeight(58)
        self.export_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.export_button.clicked.connect(self.export_data)

        # 输入url和可选项
        self.domain_label = QLabel('IP:')
        self.domain_input = QLineEdit()
        self.domain_input.setFixedHeight(50)
        self.domain_input.returnPressed.connect(self.get_set)  # 绑定回车事件

        self.generate_button = QPushButton('查询')
        self.generate_button.setFixedWidth(100)
        self.generate_button.setFixedHeight(58)
        self.generate_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.generate_button.clicked.connect(self.get_set)

        # 创建主窗口和主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # 创建输入格式和结果格式的布局
        format_layout = QHBoxLayout()
        format_layout.addWidget(self.input_format_label)
        format_layout.addWidget(self.input_format_combo)
        format_layout.addWidget(self.save_format_label)
        format_layout.addWidget(self.save_format_combo)
        format_layout.addWidget(self.export_button)
        
        format_layout.addStretch(1)
        main_layout.addLayout(format_layout)

        # 创建输入IP地址的布局
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.domain_input)
        domain_layout.addWidget(self.generate_button)
        main_layout.addLayout(domain_layout)

        # 创建结果展示框
        self.result_group_box = QGroupBox("结果:")
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(5, 10, 5, 5)  # 设置内边距
        result_layout.addWidget(self.create_result_widget())
        self.result_group_box.setLayout(result_layout)
        main_layout.addWidget(self.result_group_box)

        # 设置布局
        self.setLayout(main_layout)

    def create_result_widget(self):
        result_widget = QWidget()
        result_main_layout = QHBoxLayout()

        # 创建左侧滚动区域
        left_scroll_area = QScrollArea()
        left_scroll_area.setWidgetResizable(True)
        left_scroll_area.setStyleSheet(scroll_style)
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        search_label = QLabel("IP:")
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.search_ip)
        left_layout.addWidget(search_label)
        left_layout.addWidget(self.search_input)
        self.ip_list_widget = QListWidget()
        left_layout.addWidget(self.ip_list_widget)
        left_widget.setLayout(left_layout)
        left_scroll_area.setWidget(left_widget)

        # 创建右侧滚动区域
        right_scroll_area = QScrollArea()
        right_scroll_area.setStyleSheet(scroll_style)
        right_scroll_area.setWidgetResizable(True)
        right_widget = QWidget()
        right_layout = QHBoxLayout()

        # 创建基本信息部分
        basic_info_group = QGroupBox("基本信息")
        basic_info_layout = QVBoxLayout()
        basic_info_layout.setContentsMargins(10, 30, 10, 10)  # 设置内边距
        self.basic_info_table = QTableWidget()
        self.basic_info_table.setColumnCount(2)
        self.basic_info_table.horizontalHeader().hide()  #隐藏表格的水平表头
        self.basic_info_table.verticalHeader().hide()   #隐藏表格的垂直表头
        self.basic_info_table.setShowGrid(False)
        self.basic_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.basic_info_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.basic_info_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.basic_info_table.setAlternatingRowColors(True)
        self.basic_info_table.setStyleSheet("QTableView { alternate-background-color: #f0f0f0; border:none;}")
        
        self.basic_info_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.basic_info_table.setColumnWidth(0, 200)  # 设置第一列的宽度为100像素

        basic_info_layout.addWidget(self.basic_info_table)
        basic_info_group.setLayout(basic_info_layout)

        self.CVE_info_group = QGroupBox("CVE信息")
        self.cve_info_layout = QVBoxLayout()
        self.cve_info_layout.setContentsMargins(10, 30, 10, 10)  # 设置内边距
        self.CVE_info_group.setLayout(self.cve_info_layout)

        # ---------------------端口信息部分
        self.function_tabs = QTabWidget()
       

        #中间三部分的比例为3：1：4
        right_layout.addWidget(basic_info_group,6)
        right_layout.addWidget(self.CVE_info_group,1)
        right_layout.addWidget(self.function_tabs,9)

        right_widget.setLayout(right_layout)
        right_scroll_area.setWidget(right_widget)

        # 将IP和右侧信息展示部分添加到结果展示布局中，两边比例为1：7
        result_main_layout.addWidget(left_scroll_area,1)
        result_main_layout.addWidget(right_scroll_area,7)
        # 设置结果展示布局
        result_widget.setLayout(result_main_layout)
        return result_widget
    
    def toggle_input_options(self, index):
        if index == 0:  # 输入
            self.domain_label.setText('domain:')
            self.domain_input.clear()
            self.domain_input.setPlaceholderText('')
            self.domain_input.setReadOnly(False)
            
        elif index == 1:  # 来着文件
            self.domain_label.setText('文件:')
            self.domain_input.clear()
            self.select_file()
            self.domain_input.setReadOnly(True) #设置为只读状态，用户无法编辑其内容

    def select_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, '选择文件', '', 'Text Files (*.txt);;All Files (*)')
        if file_path:
            self.domain_input.setText(file_path)  # 将选择的文件路径显示在输入框中   

    # 定义函数用于更新表格内容
    def update_table(self,ip):
        self.basic_info_table.setRowCount(0)  # 清除现有行数
        while self.cve_info_layout.count():   #清除cve_info_layout中的组件
            item = self.cve_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        data = self.result_dict[ip]  # 根据 IP 获取对应的数据
        for key, value in data.items():
            # 基本信息
            self.basic_info_table.resizeRowsToContents()  # 自动调整行高
            if value and key != "vulns":
                row_position = self.basic_info_table.rowCount()
                self.basic_info_table.insertRow(row_position)
                
                if key == "hostnames":
                    self.basic_info_table.setItem(row_position, 0, QTableWidgetItem(str(key)))
                    num_columns = 1  # 每行最多显示的按钮数量
                    _row = 0
                    _col = 0
                    port_widget = QWidget()
                    if row_position % 2 != 0:
                        port_widget.setStyleSheet("background-color: #f0f0f0 ")
                    port_layout = QGridLayout(port_widget)  # 使用 QVBoxLayout
                    port_layout.setContentsMargins(10, 10, 10, 10)  # 设置上、右、下、左的内边距
                    for item in value:
                        port_label = QLabel(item, self)
                        port_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许鼠标选择文本
                        port_layout.addWidget(port_label,_row, _col)  # 将按钮添加到布局中
                        _col += 1
                        if _col == num_columns:
                            _col = 0
                            _row += 1
                    self.basic_info_table.setRowHeight(row_position, int(len(value)) * 35)  # 设置第一行的高度为100像素
                    self.basic_info_table.setCellWidget(row_position, 1,port_widget)  # 增加表格行数
                elif key == "tags" or key == "cpes":
                    self.basic_info_table.setItem(row_position, 0, QTableWidgetItem(str(key)))
                    num_columns = 1  # 每行最多显示的按钮数量
                    _row = 0
                    _col = 0    
                    domains_widget = QWidget()
                    if row_position % 2 != 0:
                        domains_widget.setStyleSheet("background-color: #f0f0f0 ")
                    domains_layout = QGridLayout(domains_widget)  # 使用 QVBoxLayout
                    domains_layout.setContentsMargins(10, 10, 10, 10)  # 设置上、右、下、左的内边距
                    for item in value:
                        domains_label = QLabel(item, self)
                        domains_layout.addWidget(domains_label, _row, _col)  # 将按钮添加到布局中
                        _col += 1
                        if _col == num_columns:
                            _col = 0
                            _row += 1
                    self.basic_info_table.setRowHeight(row_position, int(len(value)) * 35)  # 设置第一行的高度为100像素
                    self.basic_info_table.setCellWidget(row_position, 1,domains_widget)  # 增加表格行数
                else:
                    self.basic_info_table.setItem(row_position, 0, QTableWidgetItem(str(key)))
                    self.basic_info_table.setItem(row_position, 1, QTableWidgetItem(str(value)))
            elif key == "vulns":
                self.button_list = []
                if not value:
                    self.CVE_info_group.setVisible(False)
                    self.function_tabs.setVisible(False)
                else:
                    self.CVE_info_group.setVisible(True)
                    self.function_tabs.setVisible(True)

                for cve in value:
                    vuln_button = QPushButton(str(cve).strip())
                    vuln_button.setStyleSheet("""
                                              QPushButton {
                                               background-color: gray;
                                                border: 2px solid #65b5e9;
                                                border-radius: 10px;
                                                color: white;
                                                font-weight: bold;
                                                padding: 10px 20px;
                                                text-align: center;
                                                margin: 5px;
                                              }
                                            """)
                    self.cve_info_layout.addWidget(vuln_button)
                    self.button_list.append(vuln_button)
                    
                    vuln_button.clicked.connect(lambda state, port=cve,port_button=vuln_button: self.get_vuln_info(port,port_button))
                self.cve_info_layout.addStretch()

    def get_vuln_info(self,cve_id,vuln_button):
        for btn in self.button_list:
            btn.setStyleSheet("""
                    QPushButton {
                        background-color: gray;
                        border: 2px solid #65b5e9;
                        border-radius: 10px;
                        color: white;
                        font-weight: bold;
                        padding: 10px 20px;
                        text-align: center;
                        margin: 5px;
                    }
                """)
        vuln_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                border: 2px solid #65b5e9;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                text-align: center;
                margin: 5px;
            }
        """)
        self.function_tabs.clear()  #删除所有标签页
        self.thread1 = NVDGetVulnInfoThread(cve_id,self.proxy)
        self.thread1.finished.connect(self.handle_thread_finished)
        self.thread1.start()

    def handle_thread_finished(self,cve_data):
        for key,value in cve_data.items():
            if key == "vulnerabilities":
                # 基本信息
                for item in value:
                    # print(item)
                    tmp_data = {"CVE_id": item.get("cve").get("id"),
                                "Cisainfo": {
                                    "cisaExploitAdd": item.get("cve").get("cisaExploitAdd"),
                                    "cisaActionDue": item.get("cve").get("cisaActionDue"),
                                    "cisaRequiredAction": item.get("cve").get("cisaRequiredAction"),
                                    "cisaVulnerabilityName": item.get("cve").get("cisaVulnerabilityName")
                                },
                                "Description": item.get("cve").get("descriptions")[0].get("value"),
                                "Severity":item.get("cve").get("metrics"),
                                "Hyperlink":item.get("cve").get("references"),
                            }
                    Hyperlink_data = {"Hyperlink":item.get("cve").get("references"),}  
                    Configuration_data = {"Configuration":item.get("cve").get("configurations"),} 

                # 创建标签页并添加数据
                if tmp_data:
                    self.BasiceQTab(tmp_data, "基本信息")
                if Hyperlink_data:
                    self.BasiceQTab(Hyperlink_data, "咨询/解决方案/工具参考")
                if Configuration_data:
                    self.BasiceQTab(Configuration_data, "已知受影响的软件配置")

    def format_dict(self,d, indent=0):
        result = ""
        for key, value in d.items():
            if value:  # Check if value is not empty
                formatted_key = "    " * indent + key + ":\n"
                if isinstance(value, dict):
                    formatted_value = self.format_dict(value, indent + 1)
                elif isinstance(value, list):
                    result += "    " * indent + f"{key}:\n"
                    for item in value:
                        result += "    " * (indent + 1) + f"- {item}\n"
                else:
                    formatted_value = "    " * (indent + 1) + str(value) + "\n"
                result += formatted_key + formatted_value
        return result

    def BasiceQTab(self,data,page_name):
        # 创建垂直布局管理器
        layout = QVBoxLayout()
        if "基本信息" in page_name:
            CVE_id = data.get("CVE_id")
            Description = data.get("Description")
            Severity = data.get("Severity")
            Cisainfo = data.get("Cisainfo")
            label_text = f"<span style='color: black;font-size: 16pt;'>{CVE_id}  详细信息 </span>"
            label = QLabel()
            label.setText(label_text)
            layout.addWidget(label)
            
            Dlabel = f"<span style='color: black;font-size: 14pt;'> 描述 </span>"
            Description_label = QLabel()
            Description_label.setText(Dlabel)
            layout.addWidget(Description_label)
    
            if Description:
                request_data = QTextEdit()
                request_data.setMaximumHeight(350)  #最大显示高度
                request_data.setStyleSheet("font-size: 12pt;")  # 设置 QTextEdit 的字体大小
                request_data.setText(Description)
                
                # 创建 QScrollArea 组件并添加 QTextEdit
                D_scroll_area = QScrollArea()
                D_scroll_area.setStyleSheet(scroll_style)
                D_scroll_area.setWidget(request_data)
                D_scroll_area.setWidgetResizable(True)  # 允许内容可调整大小
                D_scroll_area.setMaximumHeight(350)  #最大显示高度
                layout.addWidget(D_scroll_area)
            if Severity:
                Slabel = f"<span style='color: black;font-size: 14pt;'> 严重性 </span>"
                Severity_label = QLabel()
                Severity_label.setText(Slabel)
                layout.addWidget(Severity_label)
                Severity_data = QTextEdit()
                Severity_data.setMaximumHeight(300)  #最小显示高度
                Severity_data.setStyleSheet("font-size: 12pt;")  # 设置 QTextEdit 的字体大小
                # severity_json = json.dumps(Severity, indent=4)
                # Severity_data.setText(severity_json)
                for key, value in Severity.items():
                    if value:
                        for cvssdata in value:
                            try:
                                cvss_data = cvssdata.get("cvssData")
                                version = cvss_data.get("version")
                                baseSeverity = cvss_data.get("baseSeverity")
                                baseScore = cvss_data.get("baseScore")
                            except (KeyError, AttributeError):
                                version = None
                                baseSeverity = None
                                baseScore = None
                            if version == "2.0":
                                baseSeverity = cvssdata.get("baseSeverity")
                        a = f"<span style='color: black;font-size: 12pt;font-weight: bold;'> Cvss Version: </span> <span> {version}   </span> <br>"
                        a += f"<span style='color: black;font-size: 12pt;font-weight: bold;'> 基础分数 </span> <span>: {baseScore}   </span> <br>"
                        a += f"<span style='color: black;font-size: 12pt;font-weight: bold;'> 矢量 </span> <span>: {baseSeverity}   </span>"
                        Severity_data.setText(a)
                
                # 创建 QScrollArea 组件并添加 QTextEdit
                S_scroll_area = QScrollArea()
                S_scroll_area.setStyleSheet(scroll_style)
                S_scroll_area.setWidget(Severity_data)
                S_scroll_area.setWidgetResizable(True)  # 允许内容可调整大小
                S_scroll_area.setMaximumHeight(300)  #最大显示高度
                layout.addWidget(S_scroll_area)
            
            if Cisainfo:
                Cisainfo_label = QLabel()
                _text = f"<span style='color: black;font-size: 16pt;'>此CVE在CISA已被利用漏洞目录中</span>"
                Cisainfo_label.setText(_text)
                layout.addWidget(Cisainfo_label)

                # 垂直滚动区域
                Cisainfo_scroll_area = QScrollArea()
                Cisainfo_scroll_area.setStyleSheet(scroll_style)
                Cisainfo_scroll_area.setWidgetResizable(True)
                Cisainfo_scroll_widget = QWidget()
                self.Cisainfo_scroll_layout = QVBoxLayout()

                # # 创建表格并添加内容
                self.Cisainfo_table = QTableWidget()
               
                # 隐藏表格的垂直表头（行号）
                self.Cisainfo_table.verticalHeader().hide()
                # 设置表格的水平表头的调整模式为Stretch，即自动调整列宽以填充整个表格宽度
                self.Cisainfo_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.Cisainfo_table.horizontalHeader().setSectionsMovable(True)  ##设置可以拖动表头
                # self.Cisainfo_table.setColumnWidth(0, 200)  # 设置第一列的宽度为100像素
                # 禁止表格单元格的编辑
                self.Cisainfo_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                # 启用交替行颜色，即相邻行使用不同的背景颜色
                self.Cisainfo_table.setAlternatingRowColors(True)
                # 设置表格的样式表，包括交替行的背景色和水平表头的样式
                self.Cisainfo_table.setStyleSheet("QTableView { alternate-background-color: #f0f0f0;border:none;}")
                self.Cisainfo_table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #353fbb; color: white}")
                self.Cisainfo_table.setColumnCount(4)  # 设置表格的列数
                headers = ["漏洞名称", "添加日期","到期日","所需采取的行动"]
                self.Cisainfo_table.setHorizontalHeaderLabels(headers)
                # 将表格添加到滚动区域的布局中
                self.Cisainfo_scroll_layout.addWidget(self.Cisainfo_table)

                # 将滚动区域的布局应用到滚动区域内的小部件上
                Cisainfo_scroll_widget.setLayout(self.Cisainfo_scroll_layout)
                Cisainfo_scroll_area.setWidget(Cisainfo_scroll_widget)

                # 将滚动区域添加到其他信息布局中
                layout.addWidget(Cisainfo_scroll_area)
                
                row_position = self.Cisainfo_table.rowCount()
                self.Cisainfo_table.insertRow(row_position)

                cisaVulnerabilityName = Cisainfo.get("cisaVulnerabilityName","")
                cisaExploitAdd = Cisainfo.get("cisaExploitAdd","")
                cisaActionDue = Cisainfo.get("cisaActionDue","")
                cisaRequiredAction = Cisainfo.get("cisaRequiredAction","")
                self.Cisainfo_table.setItem(row_position, 0, QTableWidgetItem(str(cisaVulnerabilityName)))
                self.Cisainfo_table.setItem(row_position, 1, QTableWidgetItem(str(cisaExploitAdd))) 
                self.Cisainfo_table.setItem(row_position, 2, QTableWidgetItem(str(cisaActionDue))) 
                self.Cisainfo_table.setItem(row_position, 3, QTableWidgetItem(str(cisaRequiredAction))) 
                # 设置悬浮提示
                self.Cisainfo_table.item(row_position, 0,).setToolTip((str(cisaVulnerabilityName))) 
                self.Cisainfo_table.item(row_position, 1,).setToolTip((str(cisaExploitAdd))) 
                self.Cisainfo_table.item(row_position, 2,).setToolTip((str(cisaActionDue))) 
                self.Cisainfo_table.item(row_position, 3,).setToolTip((str(cisaRequiredAction))) 
            layout.addStretch()

        elif "咨询/解决方案/工具参考" in page_name:
            Hyperlink = data.get("Hyperlink")
            if Hyperlink:
                Hyperlinklabel = f"<span style='color: black;font-size: 14pt;'> Hyperlink </span>"
                Hyperlink_label = QLabel()
                Hyperlink_label.setText(Hyperlinklabel)
                layout.addWidget(Hyperlink_label)
                list_widget = QListWidget()
                # 垂直滚动区域
                other_info_scroll_area = QScrollArea()
                other_info_scroll_area.setStyleSheet(scroll_style)
                other_info_scroll_area.setWidgetResizable(True)
                other_info_scroll_widget = QWidget()
                self.other_info_scroll_layout = QVBoxLayout()

                # # 创建表格并添加内容
                self.other_info_table = QTableWidget()
                # 设置表格的列数为2
                self.other_info_table.setColumnCount(2)
                # 隐藏表格的水平表头（列标签）
                # self.other_info_table.horizontalHeader().hide()
                # 隐藏表格的垂直表头（行号）
                self.other_info_table.verticalHeader().hide()
                # 设置表格的水平表头的调整模式为Stretch，即自动调整列宽以填充整个表格宽度
                self.other_info_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                # 禁止表格单元格的编辑
                self.other_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                # 启用交替行颜色，即相邻行使用不同的背景颜色
                self.other_info_table.setAlternatingRowColors(True)
                # 设置表格的样式表，包括交替行的背景色和水平表头的样式
                self.other_info_table.setStyleSheet("QTableView { alternate-background-color: #f0f0f0;border:none;}")
                self.other_info_table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #353fbb; color: white}")
                headers = ["Hyperlink", "Resource"]
                self.other_info_table.setHorizontalHeaderLabels(headers)
                # 将表格添加到滚动区域的布局中
                self.other_info_scroll_layout.addWidget(self.other_info_table)

                # 将滚动区域的布局应用到滚动区域内的小部件上
                other_info_scroll_widget.setLayout(self.other_info_scroll_layout)
                other_info_scroll_area.setWidget(other_info_scroll_widget)

                # 将滚动区域添加到其他信息布局中
                layout.addWidget(other_info_scroll_area)
                
                for item in Hyperlink:
                    row_position = self.other_info_table.rowCount()
                    self.other_info_table.insertRow(row_position)
                    self.other_info_table.setItem(row_position, 0, QTableWidgetItem(str(item.get("url"))))
                    self.other_info_table.setItem(row_position, 1, QTableWidgetItem(str(item.get("tags",""))))  

        elif "已知受影响的软件配置" in page_name:
            Configuration = data.get("Configuration")
            if Configuration:
                i = 1
                for item in Configuration:
                    Configurationlabel = f"<span style='color: black;font-size: 14pt;'> Configuration {i} </span>"
                    Configuration_label = QLabel()
                    Configuration_label.setText(Configurationlabel)
                    layout.addWidget(Configuration_label)
                    i +=1
                    # 垂直滚动区域
                    Configuration_scroll_area = QScrollArea()
                    Configuration_scroll_area.setMinimumHeight(200)  #最小显示高度
                    Configuration_scroll_area.setStyleSheet(scroll_style)
                    Configuration_scroll_area.setWidgetResizable(True)
                    Configuration_scroll_widget = QWidget()
                    Configuration_scroll_layout = QVBoxLayout()
                    # # 创建表格并添加内容
                    Configuration_table = QTableWidget()
                    # 设置表格的列数
                    Configuration_table.setColumnCount(3)
                    headers = ["CPE", "影响版本-从(含)","影响版本-截至（含）"]
                    Configuration_table.setHorizontalHeaderLabels(headers)
                    Configuration_table.verticalHeader().hide()   # 隐藏表格的垂直表头（行号）
                    
                    Configuration_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch) #第1列自动扩展
                    Configuration_table.setColumnWidth(1, 200)  # 设置第一列的宽度
                    Configuration_table.setColumnWidth(2, 200)  # 设置第一列的宽度
                    # 禁止表格单元格的编辑
                    Configuration_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                    # 启用交替行颜色，即相邻行使用不同的背景颜色
                    Configuration_table.setAlternatingRowColors(True)
                    # 设置表格的样式表，包括交替行的背景色和水平表头的样式
                    Configuration_table.setStyleSheet("QTableView { alternate-background-color: #f0f0f0;border:none;}")
                    Configuration_table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #353fbb; color: white}")
                    # 将表格添加到滚动区域的布局中
                    Configuration_scroll_layout.addWidget(Configuration_table)

                    # 将滚动区域的布局应用到滚动区域内的小部件上
                    Configuration_scroll_widget.setLayout(Configuration_scroll_layout)
                    Configuration_scroll_area.setWidget(Configuration_scroll_widget)

                    # 将滚动区域添加到其他信息布局中
                    layout.addWidget(Configuration_scroll_area)
                    
                    for nodes in item.get("nodes"):
                        for cpe in nodes.get("cpeMatch"):
                            row_position = Configuration_table.rowCount()
                            Configuration_table.insertRow(row_position)

                            criteria = cpe.get("criteria","")
                            versionStartIncluding = cpe.get("versionStartIncluding","")
                            versionEndExcluding = cpe.get("versionEndExcluding","")
                            
                            Configuration_table.setItem(row_position, 0, QTableWidgetItem(str(criteria)))
                            Configuration_table.setItem(row_position, 1, QTableWidgetItem(str(versionStartIncluding)))  
                            Configuration_table.setItem(row_position, 2, QTableWidgetItem(str(versionEndExcluding))) 

                            Configuration_table.item(row_position, 0,).setToolTip((str(criteria))) 
                            Configuration_table.item(row_position, 1,).setToolTip((str(versionStartIncluding))) 
                            Configuration_table.item(row_position, 2,).setToolTip((str(versionEndExcluding))) 
        # # 创建 QWidget 作为选项卡页面
        basic_info_page = QWidget()
        basic_info_page.setLayout(layout)

        # 将页面添加到选项卡中
        self.function_tabs.addTab(basic_info_page, page_name)

    # 创建函数用于更新右侧内容
    def update_right_widget(self, event=None):
        current_item = self.ip_list_widget.currentItem()
        if current_item:
            self.update_table(current_item.text())

    # 定义搜索功能
    def search_ip(self, event=None):
        keyword = self.search_input.text().strip().lower()
        if not keyword:  # 如果搜索框为空，展示所有 IP
            for i in range(self.ip_list_widget.count()):
                self.ip_list_widget.item(i).setHidden(False)
        else:
            for i in range(self.ip_list_widget.count()):
                if keyword in self.ip_list_widget.item(i).text().lower():
                    self.ip_list_widget.item(i).setHidden(False)
                else:
                    self.ip_list_widget.item(i).setHidden(True)

    def ReadConfigFile(self,):
        config = configparser.ConfigParser()
        try:
            config.read('config/shodan_config.ini')
            api_key = config.get('API', 'api_key')
            is_use_proxy = config.get('Proxy', 'is_use_proxy')
            proxy_type = config.get('Proxy', 'proxy_type')
            proxy_server_ip = config.get('Proxy', 'proxy_server_ip')
            proxy_port = config.get('Proxy', 'proxy_port')
            
            if is_use_proxy == "1" and proxy_server_ip and proxy_port and proxy_type:
                proxy = {"http":f"{proxy_type}://{proxy_server_ip}:{proxy_port}","https":f"{proxy_type}://{proxy_server_ip}:{proxy_port}"}
            else:
                proxy = {}  
        except:
            api_key = ""
            proxy = {}
            traceback.print_exc()
        return api_key,proxy

    def get_set(self, event=None):
        self.generate_button.setEnabled(False)  # 将按钮设置为不可点击
        api_key,self.proxy = self.ReadConfigFile()
        current_type = self.input_format_combo.currentText()
        self.input = self.domain_input.text()

        # 检查复选框是否被选中
        if current_type == "用户输入" and not self.input:
            QMessageBox.warning(self, '错误', '请提供IP。')
            return
        if current_type == "文件" and not self.input:
            QMessageBox.warning(self, '错误', '请提供输入文件。')
            return 
        if current_type == "用户输入":
            model="input"
        else:
            model="file"

        # 清空 QListWidget
        self.ip_list_widget.clear()
        self.function_tabs.clear()  #删除所有标签页

        self.thread1 = ShodanIpThread(model,self.input,api_key,self.proxy)
        self.thread1.finished.connect(self.post_thread_finished)
        self.thread1.start()
        
    def post_thread_finished(self,result_dict):
        self.result_dict = result_dict
        if self.result_dict:
            save_type = self.save_format_combo.currentIndex()
            if save_type == 1:   #保存到文件
                now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                url_result_file_path = now_time + "_ShodanIP.json"
                # 将 data_list 写入到 JSON 文件
                with open(url_result_file_path, 'w') as json_file:
                    json.dump(self.result_dict, json_file, indent=4)
                QMessageBox.information(self, "查询完成","结果已经保存到当前运行路径下："+ url_result_file_path)
            else:
                for key,value in self.result_dict.items():
                        self.ip_set.add(key)  # 添加到 IP 集合
                        self.ip_list_widget.addItem(key)
                # 初始化右侧部分内容
                self.ip_list_widget.setCurrentRow(0)  # 默认选中第一行
                self.update_right_widget()
                # 连接信号和槽，确保切换 IP 时右侧内容更新
                self.ip_list_widget.currentItemChanged.connect(self.update_right_widget)        
        else:
            QMessageBox.information(self, '提示', '结果为空', QMessageBox.Ok)
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击

    def export_data(self, event=None):
        try:
            if self.result_list:
                now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                url_result_file_path = now_time + "_shodan_host.json"
                json_data = json.dumps(self.result_list, indent=4)
                with open(url_result_file_path, "w+", encoding='utf-8') as f:
                    f.write(json_data)
                QMessageBox.information(self, "导出提示",f"导出成功,文件：{url_result_file_path}")
            else:
                QMessageBox.warning(None, "警告", "没有数据可以导出", QMessageBox.Ok)
        except:
            traceback.print_exc()
class ShodanHost(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style

        self.result_list = None
        
        self.init_ui()
        self.setStyleSheet(self.basic_style)

    def init_ui(self):
        # 存储 IP 地址的集合
        self.ip_set = set()
        self.setWindowTitle('ShodanHost')
        # self.resize(1400, 900)
        self.setStyleSheet("background-color: #32337e;")

        self.input_format_label = QLabel('输入形式:')
        self.input_format_combo = QComboBox()
        self.input_format_combo.setStyleSheet(self.combo_box_style)
        self.input_format_combo.addItem('用户输入')
        self.input_format_combo.addItem('文件')
        self.input_format_combo.setFixedWidth(180)
        self.input_format_combo.setFixedHeight(40)
        self.input_format_combo.currentIndexChanged.connect(self.toggle_input_options) 

        self.save_format_label = QLabel('结果形式:')
        self.save_format_combo = QComboBox()
        self.save_format_combo.setStyleSheet(self.combo_box_style)
        self.save_format_combo.addItem('输出到界面再导出保存')
        # self.save_format_combo.addItem('保存到文件')
        self.save_format_combo.setFixedWidth(180)
        self.save_format_combo.setFixedHeight(40)

        self.export_button = QPushButton("导出")
        self.export_button.setFixedWidth(100)
        self.export_button.setFixedHeight(58)
        self.export_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.export_button.clicked.connect(self.export_data)

        # 输入url和可选项
        self.domain_label = QLabel('IP:')
        self.domain_input = QLineEdit()
        self.domain_input.setFixedHeight(50)
        self.domain_input.returnPressed.connect(self.get_set)  # 绑定回车事件

        self.generate_button = QPushButton('查询')
        self.generate_button.setFixedWidth(100)
        self.generate_button.setFixedHeight(58)
        self.generate_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.generate_button.clicked.connect(self.get_set)

        # 创建主窗口和主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # 创建输入格式和结果格式的布局
        format_layout = QHBoxLayout()
        format_layout.addWidget(self.input_format_label)
        format_layout.addWidget(self.input_format_combo)
        format_layout.addWidget(self.save_format_label)
        format_layout.addWidget(self.save_format_combo)
        format_layout.addWidget(self.export_button)
        
        format_layout.addStretch(1)
        main_layout.addLayout(format_layout)

        # 创建输入IP地址的布局
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.domain_input)
        domain_layout.addWidget(self.generate_button)
        main_layout.addLayout(domain_layout)

        # 创建结果展示框
        self.result_group_box = QGroupBox("结果:")
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(5, 10, 5, 5)  # 设置内边距
        result_layout.addWidget(self.create_result_widget())
        self.result_group_box.setLayout(result_layout)
        main_layout.addWidget(self.result_group_box)

        # 设置布局
        self.setLayout(main_layout)

    def create_result_widget(self):
        result_widget = QWidget()
        result_main_layout = QHBoxLayout()

        # 创建左侧滚动区域
        left_scroll_area = QScrollArea()
        left_scroll_area.setWidgetResizable(True)
        left_scroll_area.setStyleSheet(scroll_style)
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        search_label = QLabel("IP:")
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.search_ip)
        left_layout.addWidget(search_label)
        left_layout.addWidget(self.search_input)
        self.ip_list_widget = QListWidget()
        left_layout.addWidget(self.ip_list_widget)
        left_widget.setLayout(left_layout)
        left_scroll_area.setWidget(left_widget)

        # 创建右侧滚动区域
        right_scroll_area = QScrollArea()
        right_scroll_area.setStyleSheet(scroll_style)
        right_scroll_area.setWidgetResizable(True)
        right_widget = QWidget()
        right_layout = QHBoxLayout()

        # 创建基本信息部分
        basic_info_group = QGroupBox("基本信息")
        basic_info_layout = QVBoxLayout()
        basic_info_layout.setContentsMargins(10, 30, 10, 10)  # 设置内边距
        self.basic_info_table = QTableWidget()
        self.basic_info_table.setColumnCount(2)
        self.basic_info_table.horizontalHeader().hide()  #隐藏表格的水平表头
        self.basic_info_table.verticalHeader().hide()   #隐藏表格的垂直表头
        self.basic_info_table.setShowGrid(False)
        self.basic_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.basic_info_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.basic_info_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.basic_info_table.setAlternatingRowColors(True)
        self.basic_info_table.setStyleSheet("QTableView { alternate-background-color: #f0f0f0;border:none;}")
        
        self.basic_info_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.basic_info_table.setColumnWidth(0, 200)  # 设置第一列的宽度为100像素

        basic_info_layout.addWidget(self.basic_info_table)
        basic_info_group.setLayout(basic_info_layout)
        

        port_info_group = QGroupBox("端口信息")
        self.port_info_layout = QVBoxLayout()
        self.port_info_layout.setContentsMargins(10, 30, 10, 10)  # 设置内边距
        port_info_group.setLayout(self.port_info_layout)

        # ---------------------端口信息部分
        self.function_tabs = QTabWidget()
       

        #中间三部分的比例为3：1：4
        right_layout.addWidget(basic_info_group,6)
        right_layout.addWidget(port_info_group,1)
        right_layout.addWidget(self.function_tabs,9)

        right_widget.setLayout(right_layout)
        right_scroll_area.setWidget(right_widget)

        # 将IP和右侧信息展示部分添加到结果展示布局中，两边比例为1：7
        result_main_layout.addWidget(left_scroll_area,1)
        result_main_layout.addWidget(right_scroll_area,7)
        # 设置结果展示布局
        result_widget.setLayout(result_main_layout)
        return result_widget
    
    def toggle_input_options(self, index):
        if index == 0:  # 输入
            self.domain_label.setText('domain:')
            self.domain_input.clear()
            self.domain_input.setPlaceholderText('')
            self.domain_input.setReadOnly(False)
            
        elif index == 1:  # 来着文件
            self.domain_label.setText('文件:')
            self.domain_input.clear()
            self.select_file()
            self.domain_input.setReadOnly(True) #设置为只读状态，用户无法编辑其内容

    def select_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, '选择文件', '', 'Text Files (*.txt);;All Files (*)')
        if file_path:
            self.domain_input.setText(file_path)  # 将选择的文件路径显示在输入框中   

    # 定义函数用于更新表格内容
    def update_table(self,ip):
        self.basic_info_table.setRowCount(0)  # 清除现有行数
        while self.port_info_layout.count():  #清除port_info_layout端口信息
            item = self.port_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        data = self.result_list[0][ip]  # 根据 IP 获取对应的数据
        for key in ["ip_str"]:
            if key in data:
                row_position = self.basic_info_table.rowCount()
                self.basic_info_table.insertRow(row_position)
                self.basic_info_table.setItem(row_position, 0, QTableWidgetItem(str(key)))
                self.basic_info_table.setItem(row_position, 1, QTableWidgetItem(str(data[key])))

        for key, value in data.items():
            # 基本信息
            if value and key != "ports" and key !="data":
                row_position = self.basic_info_table.rowCount()
                self.basic_info_table.insertRow(row_position)
                self.basic_info_table.resizeRowsToContents()  # 自动调整行高
                if key == "hostnames":
                    self.basic_info_table.setItem(row_position, 0, QTableWidgetItem(str(key)))
                    num_columns = 1  # 每行最多显示的按钮数量
                    _row = 0
                    _col = 0
                    port_widget = QWidget()
                    if row_position % 2 != 0:
                        port_widget.setStyleSheet("background-color: #f0f0f0 ")
                    port_layout = QGridLayout(port_widget)  # 使用 QVBoxLayout
                    port_layout.setContentsMargins(10, 10, 10, 10)  # 设置上、右、下、左的内边距
                    for item in value:
                        port_label = QLabel(item, self)
                        port_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许鼠标选择文本
                        port_layout.addWidget(port_label,_row, _col)  # 将按钮添加到布局中
                        _col += 1
                        if _col == num_columns:
                            _col = 0
                            _row += 1
                    self.basic_info_table.setRowHeight(row_position, int(len(value)) * 35)  # 设置第一行的高度为100像素
                    self.basic_info_table.setCellWidget(row_position, 1,port_widget)  # 增加表格行数
                elif key == "domains":
                    self.basic_info_table.setItem(row_position, 0, QTableWidgetItem(str(key)))
                    num_columns = 1  # 每行最多显示的按钮数量
                    _row = 0
                    _col = 0    
                    domains_widget = QWidget()
                    if row_position % 2 != 0:
                        domains_widget.setStyleSheet("background-color: #f0f0f0 ")
                    domains_layout = QGridLayout(domains_widget)  # 使用 QVBoxLayout
                    domains_layout.setContentsMargins(10, 10, 10, 10)  # 设置上、右、下、左的内边距
                    for item in value:
                        domains_label = QLabel(item, self)
                        domains_layout.addWidget(domains_label, _row, _col)  # 将按钮添加到布局中
                        _col += 1
                        if _col == num_columns:
                            _col = 0
                            _row += 1
                    self.basic_info_table.setRowHeight(row_position, int(len(value)) * 35)  # 设置第一行的高度为100像素
                    self.basic_info_table.setCellWidget(row_position, 1,domains_widget)  # 增加表格行数
                else:
                    self.basic_info_table.setItem(row_position, 0, QTableWidgetItem(str(key)))
                    self.basic_info_table.setItem(row_position, 1, QTableWidgetItem(str(value)))
            elif key == "ports":
                self.button_list = []
                for port in value:
                    port_button = QPushButton(str(port).strip())
                    port_button.setStyleSheet("""
                                              QPushButton {
                                               background-color: gray;
                                                border: 2px solid #65b5e9;
                                                border-radius: 10px;
                                                color: white;
                                                font-weight: bold;
                                                padding: 10px 20px;
                                                text-align: center;
                                                margin: 5px;
                                              }
                                            """)
                    self.port_info_layout.addWidget(port_button)
                    self.button_list.append(port_button)
                    port_button.clicked.connect(lambda state, port=port,data=data,port_button=port_button: self.get_port_info(int(port),data,port_button))
                self.port_info_layout.addStretch()

    def get_port_info(self,port,data,port_button):
        for btn in self.button_list:
            btn.setStyleSheet("""
                    QPushButton {
                        background-color: gray;
                        border: 2px solid #65b5e9;
                        border-radius: 10px;
                        color: white;
                        font-weight: bold;
                        padding: 10px 20px;
                        text-align: center;
                        margin: 5px;
                    }
                """)
        
        port_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                border: 2px solid #65b5e9;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                text-align: center;
                margin: 5px;
            }
        """)
        
        self.function_tabs.clear()  #删除所有标签页
        data_list = data["data"]
        for _data in data_list:
            _port = int(_data.get("port"))
            if _port and _port == port:
                # 基本信息
                tmp_data = {"product": _data.get("product"),
                             "data": _data.get("data"),
                             "transport":_data.get("transport"),
                             "lasttime":_data.get("timestamp")
                             }
                #  SSL 数据
                ssl_data = _data.get("ssl", {})
                
                # 其他数据
                other_data = {key: value for key, value in _data.items() if key not in ["product", "data", "ssl","_shodan","org","port","timestamp","transport","location","isp","ip_str","ip","asn"]}
                
                # 创建标签页并添加数据
                if tmp_data:
                    self.BasiceQTab(tmp_data, "基本信息")
                if ssl_data:
                    self.BasiceQTab(ssl_data, "SSL信息")
                if other_data:
                    self.BasiceQTab(other_data, "其他信息")

    def format_dict(self,d, indent=0):
        result = ""
        for key, value in d.items():
            if value:  # Check if value is not empty
                formatted_key = "    " * indent + key + ":\n"
                if isinstance(value, dict):
                    formatted_value = self.format_dict(value, indent + 1)
                    result += formatted_key + formatted_value
                elif isinstance(value, list):
                    result += "    " * indent + f"{key}:\n"
                    for item in value:
                        result += "    " * (indent + 1) + f"- {item}\n"
                else:
                    formatted_value = "    " * (indent + 1) + str(value) + "\n"
                    result += formatted_key + formatted_value
        return result

    def BasiceQTab(self,data,page_name):
        # 创建垂直布局管理器
        layout = QVBoxLayout()

        if "基本信息" in page_name:
            # 创建 label 组件
            lasttime = data.get("lasttime")
            product = data.get("product")
            transport = data.get("transport")

            # 创建 label 文本
            label_text = f"<span style='color: red;font-size: 16pt;'>// {product} / {transport} </span><span style='color: gray;font-size: 16pt;'> /    {lasttime}</span>" if product else f"<span style='color: red;font-size: 16pt;'>{transport}</span><span style='color: gray;font-size: 16pt;'> /    {lasttime}</span>"
            # 创建 label 组件并设置样式
            label = QLabel()
            label.setText(label_text)
            layout.addWidget(label)
            
            # 如果存在数据，则创建 QTextEdit 组件并添加到布局中
            request_data = QTextEdit()
            if data.get("data"):
                request_data.setStyleSheet("font-size: 12pt;")  # 设置 QTextEdit 的字体大小
                request_data.setText(data["data"])
                
                # 创建 QScrollArea 组件并添加 QTextEdit
                scroll_area = QScrollArea()
                scroll_area.setStyleSheet(scroll_style)
                scroll_area.setWidget(request_data)
                scroll_area.setWidgetResizable(True)  # 允许内容可调整大小
                # scroll_area.setMaximumHeight(3000)  # 设置最大高度为200像素
                layout.addWidget(scroll_area)
                # layout.addStretch()     
        if "SSL信息" in page_name:
            self.text_edit = QTextEdit(self)
            self.text_edit.setGeometry(10, 10, 780, 580)
            formatted_text = self.format_dict(data)
            self.text_edit.setText(formatted_text)
            layout.addWidget(self.text_edit)

        if "其他信息" in page_name:
            # 垂直滚动区域
            other_info_scroll_area = QScrollArea()
            other_info_scroll_area.setStyleSheet(scroll_style)
            other_info_scroll_area.setWidgetResizable(True)
            other_info_scroll_widget = QWidget()
            self.other_info_scroll_layout = QVBoxLayout()

            # # 创建表格并添加内容
            self.other_info_table = QTableWidget()
            # 设置表格的列数为2
            self.other_info_table.setColumnCount(2)
            # 隐藏表格的水平表头（列标签）
            self.other_info_table.horizontalHeader().hide()
            # 隐藏表格的垂直表头（行号）
            self.other_info_table.verticalHeader().hide()
            # 设置表格的水平表头的调整模式为Stretch，即自动调整列宽以填充整个表格宽度
            self.other_info_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # 禁止表格单元格的编辑
            self.other_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            # 启用交替行颜色，即相邻行使用不同的背景颜色
            self.other_info_table.setAlternatingRowColors(True)
            # 设置表格的样式表，包括交替行的背景色和水平表头的样式
            self.other_info_table.setStyleSheet("QTableView { alternate-background-color: #f0f0f0;border:none;}")
            self.other_info_table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #353fbb; color: white}")
            
            self.other_info_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
            self.other_info_table.setColumnWidth(0, 200)  # 设置第一列的宽度为100像素
            # 将表格添加到滚动区域的布局中
            self.other_info_scroll_layout.addWidget(self.other_info_table)

            # 将滚动区域的布局应用到滚动区域内的小部件上
            other_info_scroll_widget.setLayout(self.other_info_scroll_layout)
            other_info_scroll_area.setWidget(other_info_scroll_widget)

            # 将滚动区域添加到其他信息布局中
            layout.addWidget(other_info_scroll_area)

            for key,value in data.items():
                row_position = self.other_info_table.rowCount()
                self.other_info_table.insertRow(row_position)
                if isinstance(value, dict) or (isinstance(value, list) and len(value) > 1):
                    if value:
                        self.other_info_table.setItem(row_position, 0, QTableWidgetItem(str(key))) 

                        text_displat = QTextEdit()
                        _data_str = json.dumps(value, indent=4)
                        text_displat.setPlainText(_data_str)
                        domains_widget = QWidget()
                        if row_position % 2 != 0:
                            domains_widget.setStyleSheet("background-color: #f0f0f0 ")
                        domains_layout = QGridLayout(domains_widget)  # 使用 QVBoxLayout
                        domains_layout.setContentsMargins(10, 10, 10, 10)  # 设置上、右、下、左的内边距
                        domains_layout.addWidget(text_displat)
                        
                        self.other_info_table.setRowHeight(row_position, 200)  # 设置第一行的高度为100像素
                        self.other_info_table.setCellWidget(row_position, 1,text_displat)  # 增加表格行数
                else:
                    if isinstance(value, list):
                        if value:
                            self.other_info_table.setItem(row_position, 0, QTableWidgetItem(str(key)))
                            self.other_info_table.setItem(row_position, 1, QTableWidgetItem(str(value[0])))

        # # 创建 QWidget 作为选项卡页面
        basic_info_page = QWidget()
        basic_info_page.setLayout(layout)

        # 将页面添加到选项卡中
        self.function_tabs.addTab(basic_info_page, page_name)

    # 创建函数用于更新右侧内容
    def update_right_widget(self, event=None):
        current_item = self.ip_list_widget.currentItem()
        if current_item:
            self.update_table(current_item.text())

    # 定义搜索功能
    def search_ip(self, event=None):
        keyword = self.search_input.text().strip().lower()
        if not keyword:  # 如果搜索框为空，展示所有 IP
            for i in range(self.ip_list_widget.count()):
                self.ip_list_widget.item(i).setHidden(False)
        else:
            for i in range(self.ip_list_widget.count()):
                if keyword in self.ip_list_widget.item(i).text().lower():
                    self.ip_list_widget.item(i).setHidden(False)
                else:
                    self.ip_list_widget.item(i).setHidden(True)

    def ReadConfigFile(self,):
        config = configparser.ConfigParser()
        try:
            config.read('config/shodan_config.ini')
            api_key = config.get('API', 'api_key')
            is_use_proxy = config.get('Proxy', 'is_use_proxy')
            proxy_type = config.get('Proxy', 'proxy_type')
            proxy_server_ip = config.get('Proxy', 'proxy_server_ip')
            proxy_port = config.get('Proxy', 'proxy_port')
            
            if is_use_proxy == "1" and proxy_server_ip and proxy_port and proxy_type:
                proxy = {"http":f"{proxy_type}://{proxy_server_ip}:{proxy_port}","https":f"{proxy_type}://{proxy_server_ip}:{proxy_port}"}
            else:
                proxy = {}  
        except:
            api_key = ""
            proxy = {}
            traceback.print_exc()
        return api_key,proxy

    def get_set(self, event=None):
        self.ip_list_widget.clear()  # 清空 QListWidget
        self.generate_button.setEnabled(False)  # 将按钮设置为不可点击

        api_key,proxy = self.ReadConfigFile()
        current_type = self.input_format_combo.currentText()
        self.input = self.domain_input.text()

        # 检查复选框是否被选中
        if current_type == "用户输入" and not self.input:
            QMessageBox.warning(self, '错误', '请提供IP。')
            return
        if current_type == "文件" and not self.input:
            QMessageBox.warning(self, '错误', '请提供输入文件。')
            return 
        if current_type == "用户输入":
            model="input"
        else:
            model="file"
        self.thread1 = ShodanHostThread(model,self.input,api_key,proxy)
        self.thread1.finished.connect(self.post_thread_finished)
        self.thread1.start()
        
    def post_thread_finished(self,result_list):
        self.result_list = result_list
        if self.result_list:
            save_type = self.save_format_combo.currentIndex()
            if save_type == 1:   #保存到文件
                now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                url_result_file_path = now_time + "_ShodanHost.json"
                # 将 data_list 写入到 JSON 文件
                with open(url_result_file_path, 'w') as json_file:
                    json.dump(result_list, json_file, indent=4)
                QMessageBox.information(self, "查询完成","结果已经保存到当前运行路径下："+ url_result_file_path)
            else:
                for data in result_list:
                    for ip in data.keys():
                        self.ip_set.add(ip)  # 添加到 IP 集合
                        self.ip_list_widget.addItem(ip)
                # 初始化右侧部分内容
                self.ip_list_widget.setCurrentRow(0)  # 默认选中第一行
                self.update_right_widget()
                # 连接信号和槽，确保切换 IP 时右侧内容更新
                self.ip_list_widget.currentItemChanged.connect(self.update_right_widget)        
        else:
            QMessageBox.information(self, '提示', '结果为空', QMessageBox.Ok)
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击

    def export_data(self, event=None):
        try:
            if self.result_list:
                now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                url_result_file_path = now_time + "_shodan_host.json"
                json_data = json.dumps(self.result_list, indent=4)
                with open(url_result_file_path, "w+", encoding='utf-8') as f:
                    f.write(json_data)
                QMessageBox.information(self, "导出提示",f"导出成功,文件：{url_result_file_path}")
            else:
                QMessageBox.warning(None, "警告", "没有数据可以导出", QMessageBox.Ok)
        except:
            traceback.print_exc()

class ShodanDomain(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()
        self.basic_style = basic_style
        self.combo_box_style = combo_box_style
        self.result_list = None
        self.setStyleSheet("background-color: white")
        self.setStyleSheet(self.basic_style)
        self.init_ui()
        
    def init_ui(self):
        self.domain_set = set()  # 存储 Domain 地址的集合
        self.setWindowTitle('ShodanHost')
        # self.resize(1400, 900)
        self.input_format_label = QLabel('输入形式:')
        self.input_format_combo = QComboBox()
        self.input_format_combo.setStyleSheet(self.combo_box_style)
        self.input_format_combo.addItem('用户输入')
        self.input_format_combo.addItem('文件')
        self.input_format_combo.setFixedWidth(180)
        self.input_format_combo.setFixedHeight(35)
        self.input_format_combo.currentIndexChanged.connect(self.toggle_input_options) 

        self.save_format_label = QLabel('结果形式:')
        self.save_format_combo = QComboBox()
        self.save_format_combo.setStyleSheet(self.combo_box_style)
        self.save_format_combo.addItem('输出到界面再导出保存')
        # self.save_format_combo.addItem('保存到文件')
        self.save_format_combo.setFixedWidth(180)
        self.save_format_combo.setFixedHeight(35)

        self.export_button = QPushButton("导出")
        self.export_button.setFixedWidth(100)
        self.export_button.setFixedHeight(58)
        self.export_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.export_button.clicked.connect(self.export_data)

        # 输入url和可选项
        self.domain_label = QLabel('Domain:')
        self.domain_input = QLineEdit()
        self.domain_input.setFixedHeight(40)
        self.domain_input.returnPressed.connect(self.get_set)  # 绑定回车事件

        self.generate_button = QPushButton('查询')
        self.generate_button.setFixedWidth(100)
        self.generate_button.setFixedHeight(58)
        self.generate_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.generate_button.clicked.connect(self.get_set)

        # 创建主窗口和主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # 创建输入格式和结果格式的布局
        format_layout = QHBoxLayout()
        format_layout.addWidget(self.input_format_label)
        format_layout.addWidget(self.input_format_combo)
        format_layout.addWidget(self.save_format_label)
        format_layout.addWidget(self.save_format_combo)
        format_layout.addWidget(self.export_button)
        
        format_layout.addStretch(1)
        main_layout.addLayout(format_layout)

        # 创建输入IP地址的布局
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.domain_input)
        domain_layout.addWidget(self.generate_button)
        main_layout.addLayout(domain_layout)

        # 创建结果展示框
        self.result_group_box = QGroupBox("结果")
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(5, 1, 5, 5)  # 设置内边距
        result_layout.addWidget(self.create_result_widget())
        self.result_group_box.setLayout(result_layout)
        main_layout.addWidget(self.result_group_box)

        # 设置布局
        self.setLayout(main_layout)

    def clear_layout(self,layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.clear_layout(item.layout())

    def create_result_widget(self):
        result_widget = QWidget()
        result_main_layout = QHBoxLayout()

        # 创建左侧滚动区域
        self.left_scroll_area = QScrollArea()
        self.left_scroll_area.setStyleSheet(scroll_style)
        self.left_scroll_area.setWidgetResizable(True)
        self.left_widget = QWidget()
        left_layout = QVBoxLayout()
        self.search_label = QLabel("Domain:")
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.search_domain)
        
        left_layout.addWidget(self.search_label)
        left_layout.addWidget(self.search_input)
        self.ip_list_widget = QListWidget()
        left_layout.addWidget(self.ip_list_widget)
        self.left_widget.setLayout(left_layout)
        self.left_scroll_area.setWidget(self.left_widget)

        # 创建右侧滚动区域
        right_layout = QHBoxLayout()

        # 创建基本信息部分
        self.basic_info_group = QGroupBox("域名记录")
        basic_info_layout = QVBoxLayout()
        basic_info_layout.setContentsMargins(10, 10, 10, 10)  # 设置内边距
        self.basic_info_table = QTableWidget()
        self.basic_info_table.verticalScrollBar().setStyleSheet(scroll_style)
        self.basic_info_table.setColumnCount(4)
        self.basic_info_table.horizontalHeader().hide()  #隐藏表格的水平表头
        self.basic_info_table.verticalHeader().hide()   #隐藏表格的垂直表头
        self.basic_info_table.setShowGrid(False)
        self.basic_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.basic_info_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.basic_info_table.setAlternatingRowColors(True)  # 启用交替行的背景色
        self.basic_info_table.setStyleSheet("QTableView { alternate-background-color: #f0f0f0;border:none;}")  # 设置交替行的背景颜色

        self.basic_info_table.horizontalHeader().resizeSection(0, 430)  
        self.basic_info_table.horizontalHeader().resizeSection(1, 100)
        self.basic_info_table.horizontalHeader().resizeSection(2, 430)
        self.basic_info_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) #第4列自动扩展

        basic_info_layout.addWidget(self.basic_info_table)
        self.basic_info_group.setLayout(basic_info_layout)

        port_info_group = QGroupBox("子域名")
        self.port_info_layout = QVBoxLayout()
        self.port_info_layout.setContentsMargins(10, 30, 10, 10)  # 设置内边距
        port_info_group.setLayout(self.port_info_layout)
       
        #中间部分的比例
        right_layout.addWidget(self.basic_info_group,9)
        right_layout.addWidget(port_info_group,2)

        # 将IP和右侧信息展示部分添加到结果展示布局中，两边比例为1：7
        result_main_layout.addWidget(self.left_scroll_area,1)
        result_main_layout.addLayout(right_layout,7)
        # 设置结果展示布局
        result_widget.setLayout(result_main_layout)
        return result_widget
    
    def select_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, '选择文件', '', 'Text Files (*.txt);;All Files (*)')
        if file_path:
            self.domain_input.setText(file_path)  # 将选择的文件路径显示在输入框中   

    def toggle_input_options(self, index):
        if index == 0:  # 输入
            self.domain_label.setText('domain:')
            self.domain_input.clear()
            self.domain_input.setPlaceholderText('')
            self.domain_input.setReadOnly(False)
            
        elif index == 1:  # 来自文件
            self.domain_label.setText('文件:')
            self.domain_input.clear()
            self.select_file()
            self.domain_input.setReadOnly(True) #设置为只读状态，用户无法编辑其内容
    
    def ReadConfigFile(self,):
        config = configparser.ConfigParser()
        try:
            config.read('config/shodan_config.ini')
            api_key = config.get('API', 'api_key')
            is_use_proxy = config.get('Proxy', 'is_use_proxy')
            proxy_type = config.get('Proxy', 'proxy_type')
            proxy_server_ip = config.get('Proxy', 'proxy_server_ip')
            proxy_port = config.get('Proxy', 'proxy_port')
            
            if is_use_proxy == "1" and proxy_server_ip and proxy_port and proxy_type:
                proxy = {"http":f"{proxy_type}://{proxy_server_ip}:{proxy_port}","https":f"{proxy_type}://{proxy_server_ip}:{proxy_port}"}
            else:
                proxy = {}  
        except:
            api_key = ""
            proxy = {}
            traceback.print_exc()
        return api_key,proxy

    def get_set(self, event=None):
        # 清空 QListWidget
        self.ip_list_widget.clear()
        self.generate_button.setEnabled(False)  # 将按钮设置为不可点击

        api_key,proxy = self.ReadConfigFile()
        current_type = self.input_format_combo.currentText()
        self.input = self.domain_input.text()

        # 检查复选框是否被选中
        if current_type == "用户输入" and not self.input:
            QMessageBox.warning(self, '错误', '请输入域名。')
            return
        if current_type == "文件" and not self.input:
            QMessageBox.warning(self, '错误', '请提供输入文件。')
            return 
        if current_type == "用户输入":
            model="input"
        else:
            model="file"
        self.thread1 = ShodanDomainThread(model,self.input,api_key,proxy)
        self.thread1.finished.connect(self.post_thread_finished)
        self.thread1.start()

    def post_thread_finished(self,result_list):
        self.result_list = result_list
        if self.result_list:
            save_type = self.save_format_combo.currentIndex()
            if save_type == 1:   #保存到文件
                now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                url_result_file_path = now_time + "_ShodanHost.json"
                # 将 data_list 写入到 JSON 文件
                with open(url_result_file_path, 'w') as json_file:
                    json.dump(result_list, json_file, indent=4)
                QMessageBox.information(self, "查询完成","结果已经保存到当前运行路径下："+ url_result_file_path)
            else:
                for data in result_list:
                    for ip in data.keys():
                        if "error" in data[ip]:
                            QMessageBox.critical(self, '错误', data[ip].get("error","请检查输入"), QMessageBox.Ok)
                            break
                        self.domain_set.add(ip)  # 添加到 IP 集合
                        self.ip_list_widget.addItem(ip)
                # 初始化右侧部分内容
                self.ip_list_widget.setCurrentRow(0)  # 默认选中第一行
                self.update_right_widget()
                # 连接信号和槽，确保切换 IP 时右侧内容更新
                self.ip_list_widget.currentItemChanged.connect(self.update_right_widget)
        else:
            QMessageBox.information(self, '查询完成', '结果为空', QMessageBox.Ok)         
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击
        # 创建函数用于更新右侧内容
    
    def update_right_widget(self, event=None,event1=None):
        self.clear_layout(self.port_info_layout)
        current_item = self.ip_list_widget.currentItem()
        if current_item:
            self.update_table(current_item.text())
    
    def update_table(self,domain):
        self.basic_info_table.setRowCount(0)  # 清除现有行数
        data = self.result_list[0][domain]  # 根据 domain 获取对应的数据
        for key, value in data.items():
            # 基本信息
            if value and key != "subdomains":
                if key == "data":
                    self.basic_info_table.setRowCount(len(value))
                    for row, item in enumerate(value):
                        subdomain = item.get("subdomain", "")
                        subdomain = str(subdomain) + "." + str(domain)
                        type = item.get("type", "")
                        value = item.get("value", "")
                        subdomain_item = QTableWidgetItem(subdomain)
                        type_item = QTableWidgetItem(type)
                        value_item = QTableWidgetItem(value)
                        self.basic_info_table.setItem(row, 0, subdomain_item)
                        self.basic_info_table.setItem(row, 1, type_item)
                        self.basic_info_table.setItem(row, 2, value_item)
                        # 设置悬浮提示信息
                        subdomain_item.setToolTip(subdomain)
                        type_item.setToolTip(type)
                        value_item.setToolTip(value)

                        ports = item.get("ports", [])
                        button_widget = QWidget()
                        if row % 2 != 0:
                            button_widget.setStyleSheet("background-color: #f0f0f0 ")
                        else:
                            button_widget.setStyleSheet("background-color:#ffffff ")
                        button_layout = QGridLayout(button_widget)
                        button_layout.setContentsMargins(10, 10, 10, 10)
                        _row = 0
                        _col = 0
                        port_num_columns = 5  # 每行最多显示的按钮数量
                        row_num = (len(ports) - 1) // port_num_columns + 1
                        for port in ports:
                            button = QPushButton(str(port))
                            button.setStyleSheet("background-color: #007acc; font-size: 16px;")
                            button.setMinimumWidth(100)  # Set button width
                            button.setMinimumHeight(50)  # Set button height
                            button_layout.addWidget(button,_row, _col)
                            _col += 1
                            if _col == port_num_columns:
                                _col = 0
                                _row += 1
                        button_layout.setAlignment(Qt.AlignLeft)  # 设置按钮布局的对齐方式为左对齐
                        if row_num > 1:
                            row_height = row_num * 60
                            self.basic_info_table.setRowHeight(row, row_height)  # 设置第一行的高度为100像素 
                        else:
                            row_height = 60
                            self.basic_info_table.setRowHeight(row, row_height)  # 设置第一行的高度为100像素
                        tags = item.get("tags", "")
                        if tags:
                            if not ports:
                                _row = 0
                                _col = 0
                                tags_num_columns = 5
                                row_height = 60
                                row_num = (len(tags) - 1) // tags_num_columns + 1
                            else:
                                tags_num_columns = 5   #每行最多显示的个数
                                row_num = (len(tags) + len(ports) - 1) // tags_num_columns + 1
                            for tag in tags:
                                tag_button = QPushButton(str(tag))
                                tag_button.setToolTip(str(tag))
                                tag_button.setStyleSheet("background-color: black; font-size: 16px;")
                                tag_button.setMinimumWidth(100)  # Set button width
                                tag_button.setMinimumHeight(50)  # Set button height
                                button_layout.addWidget(tag_button,_row, _col)
                                _col += 1
                                if _col == tags_num_columns:
                                    _col = 0
                                    _row += 1
                            button_layout.setAlignment(Qt.AlignLeft)  # 设置按钮布局的对齐方式为左对齐
                            if row_num > 1:
                                self.basic_info_table.setRowHeight(row, row_num * 60)  # 设置第一行的高度为100像素 
                            else:
                                self.basic_info_table.setRowHeight(row, row_height)  # 设置第一行的高度为100像素
                            # 设置最后一列的宽度
                            self.basic_info_table.setColumnWidth(3, 900)
                        self.basic_info_table.setCellWidget(row, 3, button_widget)
            elif key == "subdomains":                  
                self.list_widget = QListWidget()
                self.list_widget.verticalScrollBar().setStyleSheet(scroll_style)
                self.list_widget.setSelectionMode(QListWidget.MultiSelection)  # 设置列表允许多选
                self.list_widget.itemClicked.connect(self.on_item_clicked)  #选项复制事件
                for subdomain in value:
                    list_item = QListWidgetItem("• "  + subdomain + "." + domain ) #选项文本
                    self.list_widget.addItem(list_item)  ## 将项添加到列表中
                    self.port_info_layout.addWidget(self.list_widget)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C and QApplication.keyboardModifiers() == Qt.ControlModifier:
            selected_items = self.list_widget.selectedItems()
            if selected_items:
                selected_texts = [item.text() for item in selected_items]
                QApplication.clipboard().setText('\n'.join(selected_texts))
                QMessageBox.information(self, "复制成功", "已复制选中的项")

    def on_item_clicked(self, item):
        #对多选的选项按”control +c "进行复制
        if QApplication.keyboardModifiers() == Qt.ControlModifier:  # 如果同时按下了Ctrl键
            selected_text = item.text()
            QApplication.clipboard().setText(selected_text)
            QMessageBox.information(self, "复制成功", f"已复制选中的项：{selected_text}")
    
    # 搜索功能
    def search_domain(self, event=None):
        keyword = self.search_input.text().strip().lower()
        if not keyword:  # 如果搜索框为空，展示所有 IP
            for i in range(self.ip_list_widget.count()):
                self.ip_list_widget.item(i).setHidden(False)
        else:
            for i in range(self.ip_list_widget.count()):
                if keyword in self.ip_list_widget.item(i).text().lower():
                    self.ip_list_widget.item(i).setHidden(False)
                else:
                    self.ip_list_widget.item(i).setHidden(True)

    def export_data(self, event=None):
        try:
            if self.result_list:
                if not os.path.exists(this_dir+"/domain_save"):
                    os.makedirs(this_dir+"/domain_save")
                now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                
                for data in self.result_list:
                    for key, value in data.items():
                        if value:
                            file_path = this_dir + "/domain_save/" + key + "_" + now_time + ".txt"
                            for _key,_val in value.items():
                                if _key == "subdomains":
                                    for subdomain in _val:
                                        with open(file_path, 'a+') as f:
                                                f.write(subdomain + "." + key  + "\n")

                QMessageBox.information(self, "导出提示",f"导出成功,保存到当前程序路径下的domain_save文件夹下")
            else:
                QMessageBox.warning(None, "警告", "没有数据可以导出", QMessageBox.Ok)
        except:
            traceback.print_exc()

class ConfigPage(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style
        # self.resize(1200, 600)
        self.init_ui()
        self.SetStyle()
        self.ReadConfigFile()
        self.set_conn()  #绑定按钮点击事件
        self.setStyleSheet(self.basic_style)

    def SetStyle(self):
        self.setStyleSheet("background-color: white")
        self.protocol_combobox.setStyleSheet(self.combo_box_style)

    def init_ui(self):
        layout = QHBoxLayout()  # 创建左右布局，QHBoxLayout 表示左右布局
        layout.setContentsMargins(10, 20, 0, 0)  # 设置该页面整体的左边距，上边距，右边距，底部边距
        # ----------------------------------------------------------------------开始设置左侧布局
        left_layout = QVBoxLayout()  # 设置左侧界面整体使用上下布局 ; QVBoxLayout表示：上下布局
        # =========================================api配置
        shodan_group = QGroupBox("API配置")
        shodan_layout = QHBoxLayout()  # 左右布局QHBoxLayout  上下布局：QVBoxLayout
        shodan_layout.setContentsMargins(10, 30, 10, 30)  # 设置内边距
        github_token_label = QLabel("api_key:")
        self.shodan_api_key_input = QLineEdit()

        shodan_layout.addWidget(github_token_label)
        shodan_layout.addWidget(self.shodan_api_key_input)

        shodan_group.setLayout(shodan_layout)
        left_layout.addWidget(shodan_group)
        # =========================================创建代理配置
        proxy_group = QGroupBox("代理配置")
        proxy_layout = QVBoxLayout()

        set_proxy_layout = QHBoxLayout()
        proxy_info_layout = QHBoxLayout()

        self.is_use_proxy_checkbox = QCheckBox("是否使用代理")
        set_proxy_layout.addWidget(self.is_use_proxy_checkbox)

        protocol_label = QLabel("协议:")
        self.protocol_combobox = QComboBox()
        self.protocol_combobox.addItems(["http", "socks5"])
        # 创建IP地址输入框部分
        ip_label = QLabel("IP地址:")
        self.proxy_ip_input = QLineEdit()
        # 创建端口输入框部分
        port_label = QLabel("端口:")
        self.proxy_port_input = QLineEdit()

        proxy_info_layout.addWidget(protocol_label)
        proxy_info_layout.addWidget(self.protocol_combobox)
        proxy_info_layout.addWidget(ip_label)
        proxy_info_layout.addWidget(self.proxy_ip_input)
        proxy_info_layout.addWidget(port_label)
        proxy_info_layout.addWidget(self.proxy_port_input)

        proxy_layout.addLayout(set_proxy_layout)
        proxy_layout.addLayout(proxy_info_layout)

        # 将proxy_layout
        proxy_group.setLayout(proxy_layout)
        # 将新配置框添加到左侧布局中
        left_layout.addWidget(proxy_group)
        # ----------------------------------------------------------------------------创建右侧布局
        right_layout = QVBoxLayout()

        # 创建配置说明框
        config_info_group = QGroupBox("配置说明")
        # config_info_group.setFixedHeight(800)  # 设置高度为200像素
        config_info_layout = QVBoxLayout()
        config_info_label = QLabel(
            '''首次启动，需要先配置\n要使用的引擎的api\n信息然后点击“保存”\n再点击“重新加载”即可。''')
        config_info_layout.addWidget(config_info_label)
        config_info_group.setLayout(config_info_layout)

        # 添加配置说明框和保存按钮到右侧布局
        right_layout.addWidget(config_info_group)
        self.reload_config_button = QPushButton("重新加载")
        right_layout.addWidget(self.reload_config_button)
        self.save_button = QPushButton("保存")
        right_layout.addWidget(self.save_button)

        # 将左右布局添加到主布局中
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        self.setLayout(layout)

    def ReadConfigFile(self):
        config = configparser.ConfigParser()
        try:
            config.read('config/shodan_config.ini')
            api_key = config.get('API', 'api_key')
            is_use_proxy = config.get('Proxy', 'is_use_proxy')
            proxy_type = config.get('Proxy', 'proxy_type')
            proxy_server_ip = config.get('Proxy', 'proxy_server_ip')
            proxy_port = config.get('Proxy', 'proxy_port')
            self.shodan_api_key_input.setText(api_key)
           
            self.protocol_combobox.setCurrentText(proxy_type)
            if is_use_proxy == "1":
                self.is_use_proxy_checkbox.setChecked(True)
            else:
                self.is_use_proxy_checkbox.setChecked(False)
            
            self.proxy_ip_input.setText(proxy_server_ip)
            self.proxy_port_input.setText(proxy_port)
        except:
            traceback.print_exc()

    def set_conn(self):
        self.save_button.clicked.connect(self.save_config)  # 连接保存所有配置的槽函数
    
    def write_config(filename, section, key, value):
        config = configparser.ConfigParser()
        config.read(filename)
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, key, value)
        with open(filename, 'w') as configfile:
            config.write(configfile)
    
    # 写入配置
    def write_config_file(self):
        filename = "config/shodan_config.ini"
        # 如果配置文件不存在，则创建一个新的配置文件
        if not os.path.exists(filename):
            config = configparser.ConfigParser()
            config['API'] = {}
            config['Proxy'] = {}
            with open(filename, 'w') as configfile:
                config.write(configfile)
        # 读取配置文件
        config = configparser.ConfigParser()
        config.read(filename)
        # 更新ApiSetting部分的值
        config.set('API', 'api_key', self.shodan_api_key_input.text())

        # 更新Proxy部分的值
        config.set('Proxy', 'is_use_proxy', '1' if self.is_use_proxy_checkbox.isChecked() else '0')
        config.set('Proxy', 'proxy_type', self.protocol_combobox.currentText())
        config.set('Proxy', 'proxy_server_ip', self.proxy_ip_input.text())
        config.set('Proxy', 'proxy_port', self.proxy_port_input.text())

        # 将更改写回配置文件
        with open(filename, 'w') as configfile:
            config.write(configfile)

    def save_config(self, event=None):
        choice = QMessageBox.question(self,'确认','是否保存？')
        if choice == QMessageBox.Yes:
            self.write_config_file()
            QMessageBox.information(self, "保存提示","保存成功")

class MainWindow(QMainWindow):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style

        self.setWindowTitle("tools")
        # self.setGeometry(300, 100, 2000, 1200)  # 设置窗口大小
        self.setStyleSheet("background-color: white;")  # 设置背景色
        # 界面字体大小设置
        # font = QFont("Microsoft YaHei", 14)  # 字体和大小
        # QApplication.setFont(font)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.function_tabs = QTabWidget()

        self.ShodanHostPage = ShodanHost(self.basic_style,self.combo_box_style)
        self.ShodanDomainPage = ShodanDomain(self.basic_style,self.combo_box_style)
        self.ShodanIpPage = ShodanIp(self.basic_style,self.combo_box_style)
        self.ConfigPage = ConfigPage(self.basic_style,self.combo_box_style)

    def create_layout(self):
        central_widget = QWidget()
        
        central_widget.setStyleSheet("background-color: white")  #设置背景色

        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.function_tabs)
        self.setCentralWidget(central_widget)
    # 样式设置
    def create_connections(self):
        font = QFont("Helvetica Neue", 12)  # 字体和大小
        QApplication.setFont(font)
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
        # 添加选项卡
        self.function_tabs.addTab(self.ShodanDomainPage, QIcon(this_dir+"/icon/text.png"), "Domain解析信息")
        self.function_tabs.addTab(self.ShodanHostPage, QIcon(this_dir+"/icon/text.png"), "IP信息收集")
        self.function_tabs.addTab(self.ShodanIpPage, QIcon(this_dir+"/icon/text.png"), "IP查找开放端口和漏洞")
        self.function_tabs.addTab(self.ConfigPage, QIcon(this_dir+"/icon/config.png"), "config")

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
    window = MainWindow(basic_style,combo_box_style)
    window.show()
    sys.exit(app.exec_())
