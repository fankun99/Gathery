import json
import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QLineEdit, QPushButton, QFileDialog,
    QErrorMessage
)
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtCore import Qt, QUrl ,QSize, QThread, pyqtSignal

import FunctionPage.host_scan as host_scan

class WorkerThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, ip_addresses_list,hostnames_list,port_text,thread_num,result_display,log_display):
        super().__init__()
        self.ip_addresses_list = ip_addresses_list
        self.hostnames_list = hostnames_list
        self.port_text = port_text
        self.thread_num = thread_num
        self.result_display = result_display
        self.log_display = log_display
        self.result = []

    def run(self):
        result = host_scan.run_therad(self.ip_addresses_list,self.hostnames_list,self.port_text,self.thread_num,self.result_display,self.log_display)
        if result:
            self.result = result
        self.finished.emit(self.result)
       
class HostScanWidget(QWidget):
    def __init__(self,basic_style):
        super().__init__()
        self.result = None
        self.basic_style = basic_style
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('HostScan')
        # self.resize(1200, 600)
        self.setStyleSheet(self.basic_style)
        layout = QVBoxLayout()

        # 第一排输入框和按钮
        options_layout = QHBoxLayout()
        self.port_input_label = QLabel("Ports:")
        options_layout.addWidget(self.port_input_label)
        self.port_input = QLineEdit()
        self.port_input.setFixedHeight(62)
        self.port_input.setPlaceholderText("可选, 默认80, 443")
        options_layout.addWidget(self.port_input)

        self.threads_input_label = QLabel("Threads:")
        options_layout.addWidget(self.threads_input_label)
        self.threads_input = QLineEdit()
        self.threads_input.setFixedHeight(62)
        self.threads_input.setPlaceholderText("可选, 默认10")
        options_layout.addWidget(self.threads_input)

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

        # 第二排输入框
        input_layout = QHBoxLayout()
        self.ip_input_label = QLabel("IP:")
        input_layout.addWidget(self.ip_input_label)
        self.ip_input = QTextEdit()
        self.ip_input.setPlaceholderText("一行一个（IP或CIDR格式，如192.168.1.1或8.8.8.8/24）")
        input_layout.addWidget(self.ip_input)

        self.host_input_label = QLabel("Hosts:")
        input_layout.addWidget(self.host_input_label)
        self.host_input = QTextEdit()
        self.host_input.setPlaceholderText("一行一个")
        input_layout.addWidget(self.host_input)

        layout.addSpacing(25)
        layout.addLayout(input_layout)

        # 显示结果和日志
        result_log_scroll_area = QScrollArea()
        # 设置无边框样式
        result_log_scroll_area.setStyleSheet("border: none;")
        
        result_log_layout = QHBoxLayout()
        result_log_scroll_area.setWidgetResizable(True)

        result_display_layout = QVBoxLayout()
        self.result_display_label = QLabel("Results:")
        result_display_layout.addWidget(self.result_display_label)
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        # self.result_display.setStyleSheet("background-color: #32337e; color: white; border: 1px solid #5f68c3; border-radius: 30px; padding-left: 15px;")
        self.result_display.setStyleSheet("background-color: white; color: black; border: 1px solid #5f68c3; border-radius: 30px; padding-left: 15px;")
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
    
        ip_text = self.ip_input.toPlainText()
        host_text = self.host_input.toPlainText()
        port_text = self.port_input.text()
        if not self.threads_input.text():
            thread_num = 10
        else:
            thread_num = int(self.threads_input.text())
        
        ip_addresses_list = ip_text.splitlines()
        final_ip_list = []
        for ip_input in ip_addresses_list:
            if ip_input.endswith("/24"):
                ip_pre = ip_input.split('/24')[0]
                for num in range(1,255):
                    final_ip_list.append(ip_pre+'.'+str(num))
            else:
                final_ip_list.append(ip_input)
        hostnames_list = host_text.splitlines()
        final_ip_list = list(set(final_ip_list)) #去重
        if final_ip_list and hostnames_list:
            self.thread1 = WorkerThread(final_ip_list,hostnames_list,port_text,thread_num,self.result_display,self.log_display)
            self.thread1.finished.connect(self.handle_thread_finished)
            self.thread1.start()

        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("所有IP字段和host字段不能为空.")
            return
        
    def handle_thread_finished(self,result):
        self.result = result
        self.start_button.setEnabled(True)  # 将按钮设置为可点击

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
            QErrorMessage.showMessage("没有数据可以导出....")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HostScanWidget()
    window.show()
    sys.exit(app.exec_())


