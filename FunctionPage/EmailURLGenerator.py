import itertools
import random
import re
import string
from itertools import chain
import sys
import threading
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QPushButton, QComboBox, \
    QTextEdit, QHBoxLayout, QCheckBox, QLineEdit,QFileDialog,QGroupBox,QMessageBox,QVBoxLayout, QGridLayout, QGroupBox,\
        QTableWidget,QTableWidgetItem,QAbstractItemView,QScrollArea

from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import QThread, pyqtSignal

from PyQt5.QtCore import Qt
from datetime import datetime
import re

class WorkerThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, domain, number, random_length,http_isChecked,https_isChecked,number_isChecked,str_isChecked,UpperStr_isChecked):
        super().__init__()
        self.domain = domain
        self.number = number
        self.random_length = random_length
        self.http_isChecked = http_isChecked
        self.https_isChecked = https_isChecked
        self.number_isChecked = number_isChecked
        self.str_isChecked = str_isChecked
        self.UpperStr_isChecked = UpperStr_isChecked


    def run(self):
        result_urls = self.generate_email_urls(self.domain, self.number, self.random_length)
        self.finished.emit(result_urls)
    
    def generate_email_urls(self, domain, number=None, random_length=None):
        b = ["webmail", "mailserver", "mail", "ews", "owa", "email", "outlook", "exchange", "popmail", "imap",
             "imapmail", "mx", "smtp", ]
        result_urls = []

        def mail_number(url_count):


            for i in range(url_count):
                if self.http_isChecked:
                    urls_domain = (f"http://{prefix}{i}.{domain}" for prefix in b)
                    urls_path = (f"http://{domain}/{prefix}{i}" for prefix in b)
                
                if self.https_isChecked and self.http_isChecked:
                    urls_domain = chain(urls_domain, (f"https://{prefix}{i}.{domain}" for prefix in b))
                    urls_path = chain(urls_path, (f"https://{prefix}{i}.{domain}" for prefix in b))

                elif self.https_isChecked and not self.http_isChecked:
                    urls_domain = (f"https://{prefix}{i}.{domain}" for prefix in b)
                    urls_path = (f"https://{prefix}{i}.{domain}" for prefix in b)

                result_urls.extend(chain(urls_domain, urls_path))

        def default_domain():
            if self.http_isChecked:
                domain_urls = (f"http://{prefix}.{domain}" for prefix in b)
                path_urls = (f"http://{domain}/{prefix}" for prefix in b)
                other_urls = [f"http://webmail.{domain}/webmail"]
            if self.https_isChecked and self.http_isChecked:
                domain_urls = chain(domain_urls, (f"https://{prefix}.{domain}" for prefix in b))  #用chain把多个可迭代对象中的元素串联起来
                path_urls = chain(path_urls, (f"https://{domain}/{prefix}" for prefix in b))
                other_urls = [
                        f"http://webmail.{domain}/webmail",
                        f"https://webmail.{domain}/webmail",
                    ]
            elif self.https_isChecked and not self.http_isChecked:
                domain_urls = (f"https://{prefix}.{domain}" for prefix in b)
                path_urls = (f"https://{domain}/{prefix}" for prefix in b)
                other_urls = [f"https://webmail.{domain}/webmail",]
            
            result_urls.extend(chain(domain_urls, path_urls, other_urls))  #使用extend() 方法来将多个列表合并成一个列表

        default_domain()
        if number:
            mail_number(number)
        if random_length > 0:
            # 根据选项生成字符集合
            characters = ''
            if self.number_isChecked:
                characters += string.digits
            if self.str_isChecked:
                characters += string.ascii_lowercase
            if self.UpperStr_isChecked:
                characters += string.ascii_uppercase
           
            # 生成所有排列组合
            permutations = [''.join(p) for p in itertools.product(characters, repeat=random_length)]

            for perm in permutations:
                if self.http_isChecked:
                    domain_urls = (f"http://{prefix}{perm}.{domain}" for prefix in b)
                if self.https_isChecked and self.http_isChecked:
                    domain_urls = chain(domain_urls, (f"https://{prefix}{perm}.{domain}" for prefix in b))
                elif  self.https_isChecked and not self.http_isChecked:
                    domain_urls = (f"https://{prefix}{perm}.{domain}" for prefix in b)
                result_urls.extend(domain_urls)

        return result_urls

class EmailURLGenerator(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style
        self.setStyleSheet(self.basic_style)

        self._font = QFont()  
        self._font.setPointSize(12)
        # self._font.setBold(True)  #加粗
        self._font.setFamily("Microsoft YaHei")
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('邮箱URL生成器')
        self.resize(1400, 900)

        # 保存形式选择下拉框和文件保存位置
        self.save_format_label = QLabel('结果保存形式:')
        self.save_format_label.setFont(self._font)
        self.save_format_combo = QComboBox()
        self.save_format_combo.setStyleSheet(self.combo_box_style)
        self.save_format_combo.addItem('输出到界面')
        # self.save_format_combo.addItem('保存到文件')
        # self.save_format_combo.currentIndexChanged.connect(self.toggle_output_options)
        self.save_format_combo.setFixedWidth(180)
        self.save_format_combo.setFixedHeight(40)
        
        # 输入域名和可选项
        self.domain_label = QLabel('域名:')
        self.domain_label.setFont(self._font)
        self.domain_input = QLineEdit()
        self.domain_input.setFixedHeight(45)
        self.domain_input.returnPressed.connect(self.generate_urls)  # 绑定回车事件

        # 生成按钮
        self.generate_button = QPushButton('生成')
        self.generate_button.setFont(self._font)
        self.generate_button.setFixedWidth(100)
        self.generate_button.setFixedHeight(62)
        self.generate_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.generate_button.clicked.connect(self.generate_urls)

        # ----------------------------------------------------
        self.protocol_tips_label = QLabel('协议类型:')
        self.protocol_tips_label.setStyleSheet("border:none;")
        self.protocol_tips_label.setFont(self._font)    

        protocol_group_box = QGroupBox()
        # group_box.setFixedWidth(400)  # 设置宽度为 300
        protocol_layout = QHBoxLayout(protocol_group_box)

        self.http_checkbox = QCheckBox('http')
        self.http_checkbox.setStyleSheet("border:none;")
        self.http_checkbox.setFont(self._font)
        self.http_checkbox.setChecked(True)
        self.http_checkbox.stateChanged.connect(self.check_checkbox_status)

        self.https_checkbox = QCheckBox('https')
        self.https_checkbox.setStyleSheet("border:none;")
        self.https_checkbox.setFont(self._font)
        self.https_checkbox.setChecked(True)
        self.https_checkbox.stateChanged.connect(self.check_checkbox_status)

        protocol_layout.addWidget(self.http_checkbox)
        protocol_layout.addWidget(self.https_checkbox)    
        # ----------------------------------------------------

        self.number_label = QLabel('邮件标识后拼接的数字:')
        self.number_label.setFont(self._font)
        self.mail_number_input = QLineEdit()
        self.mail_number_input.setPlaceholderText('可选,默认不设置')
        self.mail_number_input.setFixedHeight(40)

        self.random_label = QLabel('随机位数:')
        self.random_label.setFont(self._font)
        self.random_input = QLineEdit()
        self.random_input.setPlaceholderText('可选,默认不设置')
        self.random_input.setFixedHeight(40)

        self.tips_label = QLabel('随机类型:')
        self.tips_label.setStyleSheet("border:none;")
        self.tips_label.setFont(self._font)

        random_type_group_box = QGroupBox()
        random_type_layout = QHBoxLayout(random_type_group_box)

        self.number_checkbox = QCheckBox('数字')
        self.number_checkbox.setStyleSheet("border:none;")
        self.number_checkbox.setFont(self._font)
        self.number_checkbox.setChecked(True)

        self.str_checkbox = QCheckBox('小写字母')
        self.str_checkbox.setStyleSheet("border:none;")
        self.str_checkbox.setFont(self._font)
        self.str_checkbox.setChecked(False)

        self.UpperStr_checkbox = QCheckBox('大写字母')
        self.UpperStr_checkbox.setStyleSheet("border:none;")
        self.UpperStr_checkbox.setFont(self._font)
        self.UpperStr_checkbox.setChecked(False)

        random_type_layout.addWidget(self.number_checkbox)
        random_type_layout.addWidget(self.str_checkbox)
        random_type_layout.addWidget(self.UpperStr_checkbox)

        # 显示结果
        self.result_display_label = QLabel('结果:')
        self.result_display_label.setFont(self._font)
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setFont(QFont("微软雅黑", 12))

        self.total_number_label = QLabel('共获取0条url')

        # 设置布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout_format = QHBoxLayout()
        layout_format.addWidget(self.save_format_label)
        layout_format.addWidget(self.save_format_combo)
        layout.addLayout(layout_format)
        layout_format.addStretch(1)

        layout_file = QHBoxLayout()
        layout.addLayout(layout_file)

        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.domain_input)
        domain_layout.addWidget(self.generate_button)

        layout.addLayout(domain_layout)

        optional_layout = QHBoxLayout()
        optional_layout.addWidget(self.protocol_tips_label)
        optional_layout.addWidget(protocol_group_box)
        optional_layout.addWidget(self.number_label)
        optional_layout.addWidget(self.mail_number_input)
        optional_layout.addWidget(self.random_label)
        optional_layout.addWidget(self.random_input)
        optional_layout.addWidget(self.tips_label)
        optional_layout.addWidget(random_type_group_box)


        layout.addLayout(optional_layout)
        layout.addWidget(self.result_display_label)
        layout.addWidget(self.result_display)
        layout.addWidget(self.total_number_label)
        
        self.setLayout(layout)

    def check_checkbox_status(self):
        if not self.http_checkbox.isChecked() and not self.https_checkbox.isChecked():
            # 如果两个复选框都未选中，则重新选中其中一个
            self.http_checkbox.setChecked(True)

    def toggle_output_options(self, index):
        if index == 0:  # 输出到界面
            self.result_display.setVisible(True)
            self.result_display.clear()
        elif index == 1:  # 保存到文件
            self.result_display.clear()
            self.result_display.setVisible(True)

    def generate_urls(self, event=None):
        self.generate_button.setEnabled(False)  # 将按钮设置为不可点击

        self.result_display.clear()
        self.total_number_label.setText(f"共获取0条url")
        
        self.result_display.append("生成中...")

        if not self.http_checkbox.isChecked() and not self.https_checkbox.isChecked():
            # 如果两个复选框都未选中，则重新选中其中一个
            self.http_checkbox.setChecked(True)

        self.domain = self.domain_input.text()
        self.number = int(self.mail_number_input.text()) if self.mail_number_input.text() else None
        self.random_length = int(self.random_input.text()) if self.random_input.text() else 0

        if not self.domain:
            QMessageBox.warning(self, '错误', '请提供域名。')
            return
        
        http_isChecked = self.http_checkbox.isChecked()
        https_isChecked = self.https_checkbox.isChecked()   

        number_isChecked = self.number_checkbox.isChecked()
        str_isChecked = self.str_checkbox.isChecked()
        UpperStr_isChecked = self.UpperStr_checkbox.isChecked()

        # 在主函数中创建WorkerThread并启动它
        self.thread1 = WorkerThread(self.domain, self.number, self.random_length,http_isChecked,https_isChecked,number_isChecked,str_isChecked,UpperStr_isChecked)
        self.thread1.finished.connect(self.handle_thread_finished)
        self.thread1.start()

    # 定义一个处理线程完成的槽函数，用于接收线程结果并更新GUI
    def handle_thread_finished(self, result_urls):
        if self.save_format_combo.currentIndex() == 0:  # 输出到界面
            self.result_display.setPlainText('\n'.join(result_urls))
            self.total_number_label.setText(f"共获取{len(result_urls)}条url")
        elif self.save_format_combo.currentIndex() == 1:  # 保存到文件
            now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.result_file_path = now_time + "_email_urls.txt"
            with open(self.result_file_path, 'w') as file:
                file.write('\n'.join(result_urls))
            self.result_display.setPlainText("结果已经保存到文件：" + self.result_file_path)
        
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmailURLGenerator()
    window.show()
    sys.exit(app.exec_())