from datetime import datetime
import json
import os
import sys
import threading
import traceback
from urllib.parse import quote, unquote
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QPushButton, QComboBox, \
    QTextEdit, QHBoxLayout, QCheckBox, QLineEdit,QFileDialog,QGroupBox,QScrollArea,QTextBrowser,QMessageBox,QLayout,QSplitter,\
    QListWidget,QTableWidget,QHeaderView,QTableWidgetItem,QCompleter,QAbstractItemView

from PyQt5.QtGui import QFont, QCursor,QColor,QIcon
import string
from PyQt5.QtCore import Qt, QUrl ,QSize, QThread, pyqtSignal
import configparser
import requests
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
    QScrollArea { border: 2px solid #9cc4e4; border-radius: 15px; }
"""

class PostShodanThread(QThread):
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
            print("get url:",url)
            response = requests.get(url, verify=False, timeout=10, proxies=self.proxy)
            json_data = response.json()
            result[self.input] = json_data
        else:
            with open(self.input, "r") as f:
                Ips = f.read().split("\n")
            if Ips == []:
                return None
            for Ip in Ips:
                url = f"https://api.shodan.io/shodan/host/{Ip}?key={self.api_key}"
                response = requests.get(self.input, verify=False, timeout=10, proxies=self.proxy)
                json_data = response.json()
                result[Ip] = json_data
        self.data_list.append(result)        
        self.finished.emit(self.data_list)

class ShodanHost(QWidget):
    def __init__(self):
        super().__init__()
        self.combo_box_style = """
            QComboBox {
                border: 1px solid #5f68c3;
                border-radius: 10px;
                padding: 1px 10px 1px 1px;
                min-width: 8em;
                background-color: #32337e;
                color: #fff;
                height: 45px;
            }
            QComboBox::down-arrow {
                image: url(%s/icon/down.png);  /* 替换为您想要的箭头图标路径 */
                height: 35px;
            }
            QComboBox::drop-down {
                border: none;  /* 设置下拉按钮无边框 */
                background-color: #32337e;
                color: #fff;
                margin:5px;
                height: 30px; /* 调整下拉按钮的高度 */
            }
        """% (this_dir)
        self.init_ui()
        self.setStyleSheet("QMainWindow, QPushButton,QLineEdit, QTextEdit,QCheckBox,QGroupBox,QListWidget,QTableWidget {color: #bac5cf; font-family: '微软雅黑'; font-size: 12pt; }"
            "QLineEdit, QTextEdit {background-color: #32337e; color: white; border:1px solid #5f68c3; border-radius: 10px;padding-left:15px;}"
            "QLabel { font-family: '微软雅黑'; font-size: 12pt; color: #bac5cf; border: none; background: none;}"
            "QComboBox QAbstractItemView { color: white; }"
            "QGroupBox { border: none;}"
            """
                QPushButton {
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
        )
                
    def init_ui(self):
        # 存储 IP 地址的集合
        self.ip_set = set()
        self.setWindowTitle('jsFinder')
        self.resize(1400, 900)
        self.setStyleSheet("background-color: #32337e;")

        self.input_format_label = QLabel('输入形式:')
        self.input_format_combo = QComboBox()
        self.input_format_combo.setStyleSheet("QComboBox { background-color: white;}")
        self.input_format_combo.addItem('用户输入')
        self.input_format_combo.addItem('文件')
        self.input_format_combo.setFixedWidth(180)
        self.input_format_combo.setFixedHeight(40) 

        self.save_format_label = QLabel('结果形式:')
        self.save_format_combo = QComboBox()
        self.save_format_combo.setStyleSheet("QComboBox { background-color: white;}")
        self.save_format_combo.addItem('输出到界面再导出保存')
        # self.save_format_combo.addItem('保存到文件')
        self.save_format_combo.setFixedWidth(180)
        self.save_format_combo.setFixedHeight(40)

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
        format_layout.addStretch(1)
        main_layout.addLayout(format_layout)

        # 创建输入IP地址的布局
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.domain_input)
        domain_layout.addWidget(self.generate_button)
        main_layout.addLayout(domain_layout)

        # 创建结果展示框
        result_group_box = QGroupBox("结果")
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(10, 30, 10, 10)  # 设置内边距
        result_layout.addWidget(self.create_result_widget())
        result_group_box.setLayout(result_layout)
        main_layout.addWidget(result_group_box)

        # 设置布局
        self.setLayout(main_layout)

    def create_result_widget(self):
        result_widget = QWidget()
        result_main_layout = QHBoxLayout()

        # 创建左侧滚动区域
        left_scroll_area = QScrollArea()
        left_scroll_area.setWidgetResizable(True)
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        search_label = QLabel("IP:")
        self.search_input = QLineEdit()
        left_layout.addWidget(search_label)
        left_layout.addWidget(self.search_input)
        self.ip_list_widget = QListWidget()
        left_layout.addWidget(self.ip_list_widget)
        left_widget.setLayout(left_layout)
        left_scroll_area.setWidget(left_widget)

        # 创建右侧滚动区域
        right_scroll_area = QScrollArea()
        right_scroll_area.setWidgetResizable(True)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Key", "Value"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("QTableView { alternate-background-color: #1c3b7a;border:none;}")
        self.table_widget.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #353fbb; color: white}")
        right_layout.addWidget(self.table_widget)
        right_widget.setLayout(right_layout)
        right_scroll_area.setWidget(right_widget)

        # 将左右部分添加到结果展示布局中
        result_main_layout.addWidget(left_scroll_area,1)
        result_main_layout.addWidget(right_scroll_area,3)

        # 设置结果展示布局
        result_widget.setLayout(result_main_layout)

        return result_widget


    def toggle_input_options(self, index):
        if index == 0:  # 输入
            self.domain_label.setText('domain:')
            self.domain_input.clear()
            self.domain_input.setPlaceholderText('')
            self.domain_input.setEchoMode(QLineEdit.Normal)  # 恢复为正常输入模式
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

    def toggle_output_options(self, index):
        if index == 0:  # 输出到界面
            # 清空 QListWidget
            self.ip_list_widget.clear()

            # 清空 QTableWidget
            self.table_widget.clearContents()
            self.table_widget.setRowCount(0)
        elif index == 1:  # 保存到文件
            # 清空 QListWidget
            self.ip_list_widget.clear()

            # 清空 QTableWidget
            self.table_widget.clearContents()
            self.table_widget.setRowCount(0)
    
    # 定义函数用于更新表格内容
    def update_table(self,ip):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)  # 清除现有行数
        data = self.result_list[0][ip]  # 根据 IP 获取对应的数据
        for key, value in data.items():
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(str(key)))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(str(value)))

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
            config.read('shodan/config.ini')
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
        self.ip_list_widget.clear()

        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
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
            # print("输入域名为",self.input )
            model="input"
        else:
            model="file"
            # print("输入文件为",self.input )
        self.thread1 = PostShodanThread(model,self.input,api_key,proxy)
        self.thread1.finished.connect(self.post_thread_finished)
        self.thread1.start()
        
    def post_thread_finished(self,result_list):
        self.result_list = result_list
        save_type = self.save_format_combo.currentIndex()
        if save_type == 1:   #保存到文件
            now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            url_result_file_path = now_time + "_ShodanHost.json"
            # 将 data_list 写入到 JSON 文件
            with open(url_result_file_path, 'w') as json_file:
                json.dump(result_list, json_file, indent=4)
            QMessageBox.information(self, "查询完成","结果已经保存到当前运行路径下："+ url_result_file_path)
        else:
            if result_list:
                for data in result_list:
                    for ip in data.keys():
                        self.ip_set.add(ip)  # 添加到 IP 集合
                        self.ip_list_widget.addItem(ip)
                # 初始化右侧部分内容
                self.ip_list_widget.setCurrentRow(0)  # 默认选中第一行
                self.update_right_widget()
                # 连接信号和槽，确保切换 IP 时右侧内容更新
                self.ip_list_widget.currentItemChanged.connect(self.update_right_widget)        
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShodanHost()
    window.show()
    sys.exit(app.exec_())
