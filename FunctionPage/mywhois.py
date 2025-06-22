import json
import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QLineEdit, QPushButton, QFileDialog,QTableWidget,QHeaderView,QTableWidgetItem,QGridLayout,QAbstractItemView,
    QErrorMessage
)
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtCore import Qt, QUrl ,QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFontMetrics

import whois

class WorkerThread(QThread):
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
    
class WhoisWidget(QWidget):
    def __init__(self,basic_style):
        super().__init__()
        self.result = None
        self.basic_style = basic_style
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

        self.result_display.clear()
    
        domain_text = self.domain_input.text()
        
        if domain_text:
            self.thread1 = WorkerThread(domain_text)
            self.thread1.finished.connect(self.handle_thread_finished)
            self.thread1.start()
        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("请提供有效的域名")
            return
        
    def handle_thread_finished(self,result):
        self.result = result
        self.start_button.setEnabled(True)  # 将按钮设置为可点击
        key_translation = {
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
                "admin_contact": "管理联系人信息",
                "tech_contact": "技术联系人信息",
                "dnssec": "DNS安全扩展",
                "state": "地区",
                "country": "国家",
                "org": "组织",
        }
        for i, (key, value) in enumerate(result.items()):
            if value:
                if key in key_translation:
                    key = key_translation[key]
                else:
                    key = key.capitalize()  # 如果没有映射，将首字母大写
                if isinstance(value, list):  # 如果值是列表
                    content = "\n".join(value)
                    self.result_display.setSectionResizeMode(QHeaderView.ResizeToContents)
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
        with open(file_path, 'w', newline='') as f:
            for data in self.result:
                for key, values in data.items():
                    f.write(str(key) + "\n" + "  -----> " + str(values) + "\n")
            
    def export_json(self, file_path):  
        with open(file_path, 'w') as jsonfile:
            for data in self.result:
                json.dump(data, jsonfile, indent=4)

    def save_to_file(self, event=None):
        if self.result:
            file_format, _ = QFileDialog.getSaveFileName(self, '保存文件', '', 'CSV Files (*.txt);;JSON Files (*.json)')
            if file_format:
                if file_format.endswith('.txt'):
                    self.export_txt( file_format)
                elif file_format.endswith('.json'):
                    self.export_json(file_format)
                self.log_display.append(f"导出完成....")
        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("没有数据可以导出....")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhoisWidget()
    window.show()
    sys.exit(app.exec_())


