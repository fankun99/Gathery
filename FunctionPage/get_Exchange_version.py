import re
import sys
import threading
import traceback
from PyQt5.QtWidgets import QApplication,QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QLabel, QTextEdit, QFileDialog,QLineEdit, QComboBox,QMessageBox
from PyQt5.QtGui import QFont, QColor, QCursor
from PyQt5.QtCore import Qt, QUrl ,QSize, QThread, pyqtSignal


from PyQt5.QtCore import Qt, QSize
from urllib.parse import urlparse
import requests
import re
import urllib3
urllib3.disable_warnings()

class WorkerThread(QThread):
    finished = pyqtSignal(dict)
    def __init__(self, save_type,current_type,input,proxy):
        super().__init__()
        self.save_type = save_type
        self.input = input
        self.input_type = current_type
        self.proxy = proxy
        self.last_result = {}   #存储结果
        self.versionarray = [
            ["Exchange Server 2019 CU12 May22SU", "05/10/2022", "15.2.1118.9"],
            ["Exchange Server 2019 CU12 (2022H1)", "04/20/2022", "15.2.1118.7"],
            ["Exchange Server 2019 CU11 May22SU", "05/10/2022", "15.2.986.26"],
            ["Exchange Server 2019 CU11 Mar22SU", "03/08/2022", "15.2.986.22"],
            ["Exchange Server 2019 CU11 Jan22SU", "01/11/2022", "15.2.986.15"],
            ["Exchange Server 2019 CU11 Nov21SU", "11/09/2021", "15.2.986.14"],
            ["Exchange Server 2019 CU11 Oct21SU", "10/12/2021", "15.2.986.9"],
            ["Exchange Server 2019 CU11", "09/28/2021", "15.2.986.5"],
            ["Exchange Server 2019 CU10 Mar22SU", "03/08/2022", "15.2.922.27"],
            ["Exchange Server 2019 CU10 Jan22SU", "01/11/2022", "15.2.922.20"],
            ["Exchange Server 2019 CU10 Nov21SU", "11/09/2021", "15.2.922.19"],
            ["Exchange Server 2019 CU10 Oct21SU", "10/12/2021", "15.2.922.14"],
            ["Exchange Server 2019 CU10 Jul21SU", "07/13/2021", "15.2.922.13"],
            ["Exchange Server 2019 CU10", "07/29/2021", "15.2.922.7"],
            ["Exchange Server 2019 CU9 Jul21SU", "07/13/2021", "15.2.858.15"],
            ["Exchange Server 2019 CU9 May21SU", "05/11/2021", "15.2.858.12"],
            ["Exchange Server 2019 CU9 Apr21SU", "04/13/2021", "15.2.858.10"],
            ["Exchange Server 2019 CU9", "03/16/2021", "15.2.858.5"],
            ["Exchange Server 2019 CU8 May21SU", "05/11/2021", "15.2.792.15"],
            ["Exchange Server 2019 CU8 Apr21SU", "04/13/2021", "15.2.792.13"],
            ["Exchange Server 2019 CU8 Mar21SU", "03/02/2021", "15.2.792.10"],
            ["Exchange Server 2019 CU8", "12/15/2020", "15.2.792.3"],
            ["Exchange Server 2019 CU7 Mar21SU", "03/02/2021", "15.2.721.13"],
            ["Exchange Server 2019 CU7", "09/15/2020", "15.2.721.2"],
            ["Exchange Server 2019 CU6 Mar21SU", "03/02/2021", "15.2.659.12"],
            ["Exchange Server 2019 CU6", "06/16/2020", "15.2.659.4"],
            ["Exchange Server 2019 CU5 Mar21SU", "03/02/2021", "15.2.595.8"],
            ["Exchange Server 2019 CU5", "03/17/2020", "15.2.595.3"],
            ["Exchange Server 2019 CU4 Mar21SU", "03/02/2021", "15.2.529.13"],
            ["Exchange Server 2019 CU4", "12/17/2019", "15.2.529.5"],
            ["Exchange Server 2019 CU3 Mar21SU", "03/02/2021", "15.2.464.15"],
            ["Exchange Server 2019 CU3", "09/17/2019", "15.2.464.5"],
            ["Exchange Server 2019 CU2 Mar21SU", "03/02/2021", "15.2.397.11"],
            ["Exchange Server 2019 CU2", "06/18/2019", "15.2.397.3"],
            ["Exchange Server 2019 CU1 Mar21SU", "03/02/2021", "15.2.330.11"],
            ["Exchange Server 2019 CU1", "02/12/2019", "15.2.330.5"],
            ["Exchange Server 2019 RTM Mar21SU", "03/02/2021", "15.2.221.18"],
            ["Exchange Server 2019 RTM", "10/22/2018", "15.2.221.12"],
            ["Exchange Server 2019 Preview", "07/24/2018", "15.2.196.0"],
            ["Exchange Server 2016 CU23 May22SU", "05/10/2022", "15.1.2507.9"],
            ["Exchange Server 2016 CU23 (2022H1)", "04/20/2022", "15.1.2507.6"],
            ["Exchange Server 2016 CU22 May22SU", "05/10/2022", "15.1.2375.28"],
            ["Exchange Server 2016 CU22 Mar22SU", "03/08/2022", "15.1.2375.24"],
            ["Exchange Server 2016 CU22 Jan22SU", "01/11/2022", "15.1.2375.18"],
            ["Exchange Server 2016 CU22 Nov21SU", "11/09/2021", "15.1.2375.17"],
            ["Exchange Server 2016 CU22 Oct21SU", "10/12/2021", "15.1.2375.12"],
            ["Exchange Server 2016 CU22", "09/28/2021", "15.1.2375.7"],
            ["Exchange Server 2016 CU21 Mar22SU", "03/08/2022", "15.1.2308.27"],
            ["Exchange Server 2016 CU21 Jan22SU", "01/11/2022", "15.1.2308.21"],
            ["Exchange Server 2016 CU21 Nov21SU", "11/09/2021", "15.1.2308.20"],
            ["Exchange Server 2016 CU21 Oct21SU", "10/12/2021", "15.1.2308.15"],
            ["Exchange Server 2016 CU21 Jul21SU", "07/13/2021", "15.1.2308.14"],
            ["Exchange Server 2016 CU21", "07/29/2021", "15.1.2308.8"],
            ["Exchange Server 2016 CU20 Jul21SU", "07/13/2021", "15.1.2242.12"],
            ["Exchange Server 2016 CU20 May21SU", "05/11/2021", "15.1.2242.10"],
            ["Exchange Server 2016 CU20 Apr21SU", "04/13/2021", "15.1.2242.8"],
            ["Exchange Server 2016 CU20", "03/16/2021", "15.1.2242.4"],
            ["Exchange Server 2016 CU19 May21SU", "05/11/2021", "15.1.2176.14"],
            ["Exchange Server 2016 CU19 Apr21SU", "04/13/2021", "15.1.2176.12"],
            ["Exchange Server 2016 CU19 Mar21SU", "03/02/2021", "15.1.2176.9"],
            ["Exchange Server 2016 CU19", "12/15/2020", "15.1.2176.2"],
            ["Exchange Server 2016 CU18 Mar21SU", "03/02/2021", "15.1.2106.13"],
            ["Exchange Server 2016 CU18", "09/15/2020", "15.1.2106.2"],
            ["Exchange Server 2016 CU17 Mar21SU", "03/02/2021", "15.1.2044.13"],
            ["Exchange Server 2016 CU17", "06/16/2020", "15.1.2044.4"],
            ["Exchange Server 2016 CU16 Mar21SU", "03/02/2021", "15.1.1979.8"],
            ["Exchange Server 2016 CU16", "03/17/2020", "15.1.1979.3"],
            ["Exchange Server 2016 CU15 Mar21SU", "03/02/2021", "15.1.1913.12"],
            ["Exchange Server 2016 CU15", "12/17/2019", "15.1.1913.5"],
            ["Exchange Server 2016 CU14 Mar21SU", "03/02/2021", "15.1.1847.12"],
            ["Exchange Server 2016 CU14", "09/17/2019", "15.1.1847.3"],
            ["Exchange Server 2016 CU13 Mar21SU", "03/02/2021", "15.1.1779.8"],
            ["Exchange Server 2016 CU13", "06/18/2019", "15.1.1779.2"],
            ["Exchange Server 2016 CU12 Mar21SU", "03/02/2021", "15.1.1713.10"],
            ["Exchange Server 2016 CU12", "02/12/2019", "15.1.1713.5"],
            ["Exchange Server 2016 CU11 Mar21SU", "03/02/2021", "15.1.1591.18"],
            ["Exchange Server 2016 CU11", "10/16/2018", "15.1.1591.10"],
            ["Exchange Server 2016 CU10 Mar21SU", "03/02/2021", "15.1.1531.12"],
            ["Exchange Server 2016 CU10", "06/19/2018", "15.1.1531.3"],
            ["Exchange Server 2016 CU9 Mar21SU", "03/02/2021", "15.1.1466.16"],
            ["Exchange Server 2016 CU9", "03/20/2018", "15.1.1466.3"],
            ["Exchange Server 2016 CU8 Mar21SU", "03/02/2021", "15.1.1415.10"],
            ["Exchange Server 2016 CU8", "12/19/2017", "15.1.1415.2"],
            ["Exchange Server 2016 CU7", "09/19/2017", "15.1.1261.35"],
            ["Exchange Server 2016 CU6", "06/27/2017", "15.1.1034.26"],
            ["Exchange Server 2016 CU5", "03/21/2017", "15.1.845.34"],
            ["Exchange Server 2016 CU4", "12/13/2016", "15.1.669.32"],
            ["Exchange Server 2016 CU3", "09/20/2016", "15.1.544.27"],
            ["Exchange Server 2016 CU2", "06/21/2016", "15.1.466.34"],
            ["Exchange Server 2016 CU1", "03/15/2016", "15.1.396.30"],
            ["Exchange Server 2016 RTM", "10/01/2015", "15.1.225.42"],
            ["Exchange Server 2016 Preview", "07/22/2015", "15.1.225.16"],
            ["Exchange Server 2013 CU23 May22SU", "05/10/2022", "15.0.1497.36"],
            ["Exchange Server 2013 CU23 Mar22SU", "03/08/2022", "15.0.1497.33"],
            ["Exchange Server 2013 CU23 Jan22SU", "01/11/2022", "15.0.1497.28"],
            ["Exchange Server 2013 CU23 Nov21SU", "11/09/2021", "15.0.1497.26"],
            ["Exchange Server 2013 CU23 Oct21SU", "10/12/2021", "15.0.1497.24"],
            ["Exchange Server 2013 CU23 Jul21SU", "07/13/2021", "15.0.1497.23"],
            ["Exchange Server 2013 CU23 May21SU", "05/11/2021", "15.0.1497.18"],
            ["Exchange Server 2013 CU23 Apr21SU", "04/13/2021", "15.0.1497.15"],
            ["Exchange Server 2013 CU23 Mar21SU", "03/02/2021", "15.0.1497.12"],
            ["Exchange Server 2013 CU23", "06/18/2019", "15.0.1497.2"],
            ["Exchange Server 2013 CU22 Mar21SU", "03/02/2021", "15.0.1473.6"],
            ["Exchange Server 2013 CU22", "02/12/2019", "15.0.1473.3"],
            ["Exchange Server 2013 CU21 Mar21SU", "03/02/2021", "15.0.1395.12"],
            ["Exchange Server 2013 CU21", "06/19/2018", "15.0.1395.4"],
            ["Exchange Server 2013 CU20", "03/20/2018", "15.0.1367.3"],
            ["Exchange Server 2013 CU19", "12/19/2017", "15.0.1365.1"],
            ["Exchange Server 2013 CU18", "09/19/2017", "15.0.1347.2"],
            ["Exchange Server 2013 CU17", "06/27/2017", "15.0.1320.4"],
            ["Exchange Server 2013 CU16", "03/21/2017", "15.0.1293.2"],
            ["Exchange Server 2013 CU15", "12/13/2016", "15.0.1263.5"],
            ["Exchange Server 2013 CU14", "09/20/2016", "15.0.1236.3"],
            ["Exchange Server 2013 CU13", "06/21/2016", "15.0.1210.3"],
            ["Exchange Server 2013 CU12", "03/15/2016", "15.0.1178.4"],
            ["Exchange Server 2013 CU11", "12/15/2015", "15.0.1156.6"],
            ["Exchange Server 2013 CU10", "09/15/2015", "15.0.1130.7"],
            ["Exchange Server 2013 CU9", "06/17/2015", "15.0.1104.5"],
            ["Exchange Server 2013 CU8", "03/17/2015", "15.0.1076.9"],
            ["Exchange Server 2013 CU7", "12/09/2014", "15.0.1044.25"],
            ["Exchange Server 2013 CU6", "08/26/2014", "15.0.995.29"],
            ["Exchange Server 2013 CU5", "05/27/2014", "15.0.913.22"],
            ["Exchange Server 2013 SP1 Mar21SU", "03/02/2021", "15.0.847.64"],
            ["Exchange Server 2013 SP1", "02/25/2014", "15.0.847.32"],
            ["Exchange Server 2013 CU3", "11/25/2013", "15.0.775.38"],
            ["Exchange Server 2013 CU2", "07/09/2013", "15.0.712.24"],
            ["Exchange Server 2013 CU1", "04/02/2013", "15.0.620.29"],
            ["Exchange Server 2013 RTM", "12/03/2012", "15.0.516.32"]
        ]

        self.vularray = [
        ["CVE-2020-0688", "02/11/2020"],
        ["CVE-2021-26855+CVE-2021-27065", "03/02/2021"],
        ["CVE-2021-28482", "04/13/2021"],
        ["CVE-2021-34473+CVE-2021-34523+CVE-2021-31207", "04/13/2021"],
        ["CVE-2021-31195+CVE-2021-31196", "05/11/2020"],
        ["CVE-2021-31206", "07/13/2021"],
        ["CVE-2021-42321", "11/09/2021"],
        ["CVE-2022-23277", "03/08/2022"],
        ]        

    def run(self):
       # 结果保存类型
        if self.input_type == "用户输入":
            url = self.input
            if url[-1] == "/":
                url = url[:-1]
            if url:
                self.GetVersion_MatchVul(url)
        self.finished.emit(self.last_result)

    def vulscan(self,version,date):
        vulns = {}
        for value in self.vularray:
            if (date.split('/')[2] < value[1].split('/')[2]):
                # self.result_url_display.append("[+] " + value[0] + ", " + value[1])
                # print("[+] " + value[0] + ", " + value[1])
                vulns[version] = value[0] + ", " + value[1]
            else:
                if (date.split('/')[2] == value[1].split('/')[2]) & (date.split('/')[0] < value[1].split('/')[0]):
                    # self.result_url_display.append("[+] " + value[0] + ", " + value[1])
                    # print("[+] " + value[0] + ", " + value[1])
                    vulns[version] = value[0] + ", " + value[1]
                else:
                    if (date.split('/')[2] == value[1].split('/')[2]) & (date.split('/')[0] == value[1].split('/')[0]) & (date.split('/')[1] < value[1].split('/')[1]):
                        # print("[+] " + value[0] + ", " + value[1])
                        vulns[version] = value[0] + ", " + value[1]
                        # self.result_url_display.append("[+] " + value[0] + ", " + value[1])
        return vulns
    def matchversion(self,version):
        version_vulns = {}
        for value in self.versionarray:
            if version in value:
                vulns_dict = self.vulscan(version,value[1])
                version_vulns[version] = vulns_dict
        return version_vulns
            
    def guessversion(self,version):
        version_vulns = {}
        guessversion_info = ""
        for value in self.versionarray:
            if version in value[2][:value[2].rfind(".")]:
                print("[+] Guessed Version: " + value[2])
                print("    Product: " + value[0])
                print("    Date: " + value[1])
                guessversion_info += "--> Guessed Version" + value[2] + "    Product: " + value[0] + "    Date: " + value[1] + "<br>"
                vulns_dict = self.vulscan(version,value[1])
                version_vulns[version] = vulns_dict
        return version_vulns,guessversion_info
    
    def GetVersion_MatchVul(self,url):
        try:
            print("[*] Trying to access EWS")
            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
            } 
            url1 = url + "/ews"
            req = requests.get(url1, headers = headers, verify=False, timeout=10, proxies=self.proxy)
            if "X-FEServer" not in req.headers:
                print("[!] Exchange 2010 or older")
                print("[*] Trying to access OWA")
                url2 = url + "/owa"
                req = requests.get(url2, headers = headers, verify=False, timeout=10, proxies=self.proxy)
                pattern_version = re.compile(r"/owa/(.*?)/themes/resources/favicon.ico")
                version = pattern_version.findall(req.text)[0]
                if "auth" in version:
                    version = version.split('/')[1]
                    print("[+] Version:" + version)
                    version_vulns,guessversion_info = self.guessversion(version)
                else:
                    version = ""
                    version_vulns = {}
                self.last_result[url] = {
                    "Version": version,
                    "version_vulns": version_vulns,
                    "guessversion_info":guessversion_info,
                    "other_info":"Exchange 2010 or older"
                }
                return self.last_result
            else:
                print("[+] X-FEServer:" + req.headers["X-FEServer"])
                other_info = "X-FEServer is " + str(req.headers["X-FEServer"])  
            if "X-OWA-Version" in req.headers:
                version = req.headers["X-OWA-Version"]
                print("[+] X-OWA-Version:" + version)
                print("[*] Trying to get the full version and match the vul")
                version_vulns = self.matchversion(version)
                guessversion_info = ""
            else:
                print("[!] No X-OWA-Version")
                print("[*] Trying to access OWA")
                url2 = url + "/owa"
                req = requests.get(url2, headers = headers, verify=False, timeout=10, proxies=self.proxy)
                pattern_version = re.compile(r"/owa/auth/(.*?)/themes/resources/favicon.ico")
                version = pattern_version.findall(req.text)[0]
                print("[+] Version:" + version)
                print("[*] Trying to guess the full version and match the vul")
                version_vulns,guessversion_info = self.guessversion(version)

            other_info if other_info else ""  
            self.last_result[url] = {
                    "Version": version,
                    "version_vulns": version_vulns,
                    "guessversion_info":guessversion_info,
                    "other_info": other_info
            }
            return self.last_result
        except Exception as e:
            traceback.print_exc()
            print("[!] error: "+str(e))
            # print("[!] "+str(e))
            self.last_result[url] = {}
            return 


class get_Exchange_version(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style
        self.setStyleSheet(self.basic_style)

        self._font = QFont()  
        self._font.setPointSize(12)
        self._font.setFamily("Microsoft YaHei")
        
        self.proxy = {}
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('get_fortigate_version')
        self.resize(1400, 900)
        self.setFont(QFont("微软雅黑", 12))

        self.input_format_label = QLabel('输入形式:')
        self.input_format_label.setFont(self._font)
        self.input_format_combo = QComboBox()
        self.input_format_combo.setStyleSheet(self.combo_box_style)
        self.input_format_combo.setFont(QFont("Arial", 12))
        self.input_format_combo.addItem('用户输入')
        # self.input_format_combo.addItem('文件')
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

        self.proxy_label = QLabel('proxy:')
        self.proxy_label.setFont(self._font)
        self.proxy_input = QLineEdit()
        self.proxy_input.setFont(self._font)
        self.proxy_input.setPlaceholderText('可选')
        self.proxy_input.setFixedHeight(40)


         # 显示结果的布局
        self.result_layout = QHBoxLayout()

        # 左侧显示区域-url
        self.url_layout = QVBoxLayout()
        self.result_display_label = QLabel('结果:')
        self.result_display_label.setFont(self._font)
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

        optional_layout = QHBoxLayout()
        optional_layout.addWidget(self.proxy_label)
        optional_layout.addWidget(self.proxy_input)

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

    def toggle_output_options(self, index):
        if index == 0:  # 输出到界面
            self.result_url_display.setVisible(True)
            self.result_url_display.clear()
        elif index == 1:  # 保存到文件
            self.result_url_display.clear()
            self.result_url_display.setVisible(True)

    def get_set(self, event=None):
        self.generate_button.setEnabled(False)  # 将按钮设置为不可点击
        self.result_url_display.clear()
        
        self.result_url_display.setTextColor(QColor("green"))
        self.result_url_display.append("start....")
        QApplication.processEvents()  # 立即处理事件循环，以确保新内容立即显示

        current_type = self.input_format_combo.currentText()
        self.input = self.url_input.text()
        self.proxy = {"http":self.proxy_input.text(),"https":self.proxy_input.text()}  if self.proxy_input.text() else {}
        
        # 检查复选框是否被选中
        if current_type == "用户输入" and not self.input:
            QMessageBox.warning(self, '错误', '请提供url。')
            self.result_url_display.append("finish ")
            return
        
        # thread1 = threading.Thread(target=self.thread_start,args=(current_type,))
        # thread1.start()
        save_type = self.save_format_combo.currentIndex()
        
        self.thread1 = WorkerThread(save_type,current_type,self.input,self.proxy)
        self.thread1.finished.connect(self.handle_thread_finished)
        self.thread1.start()
    
    def handle_thread_finished(self,result):
        for url, value in result.items():
            if value:
                Version = value.get("Version", "")
                version_vulns = value.get("version_vulns", {})
                guessversion_info = value.get("guessversion_info", "")
                other_info = value.get("other_info", "")
                info = ""
                if other_info:
                    info +=  other_info + '<br> '
                if Version:
                    info += '    -->版本: ' + Version + '<br> '
                if version_vulns:
                    info += '    --> 版本可能存在的漏洞: ' + str(version_vulns) + "<br> "
                if guessversion_info:
                    info += '    --> 推测版本: ' + guessversion_info + '<br> '

                if info:
                    self.result_url_display.append('<font color="red">[+]  ' + url + "<br>" + '    --> ' + info + '</font>')
                else:
                    self.result_url_display.append('<font color="green">[-] ' + url + ' not find</font>')
            else:
                self.result_url_display.append('<font color="green">[-] ' + url + ' not find</font>')
        self.result_url_display.setTextColor(QColor("green"))
        self.result_url_display.append("finish")   
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = get_Exchange_version()
    window.show()
    sys.exit(app.exec_())                