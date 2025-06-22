from datetime import datetime
import json
import os
import sys
import threading
import traceback
from urllib.parse import quote, unquote
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QPushButton, QComboBox, \
    QTextEdit, QHBoxLayout, QCheckBox, QLineEdit,QFileDialog,QGroupBox,QScrollArea,QTextBrowser,QMessageBox,QLayout
from PyQt5.QtGui import QFont, QCursor,QColor,QIcon
import string
from PyQt5.QtCore import Qt, QUrl ,QSize, QThread, pyqtSignal
import configparser
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from emailall import emailall

import random
import smtplib
import logging
import time
import dns.resolver
import FunctionPage.common as common


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
    QScrollArea { border: 1px solid #34397f; }
"""

class WorkerThread(QThread):
    finished = pyqtSignal(dict,dict)

    def __init__(self, model,input,verifyEmail):
        super().__init__()
        self.model = model
        self.input = input
        self.verifyEmail = verifyEmail

        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: %(message)s')

        self.logger = logging.getLogger()

    def run(self):
        if self.model == "input":
            email_all = emailall.EmailAll(domain=self.input, domains=None)
        else:
            email_all = emailall.EmailAll(domain=None, domains=self.input)
        result = email_all.run()


        if self.verifyEmail:
            email_list = result.get("email")
            mail_list = []
            if email_list:
                for item in email_list:
                    email = item[1]
                    mail_list.append(email)
            final_verify_dict = self.verify_istrue(mail_list)  #{'190758586@qq.com': True, 'qwer111111111111995@163.com': False}
        else:
            final_verify_dict = {}   
             
        self.finished.emit(result,final_verify_dict)
    
    def verify_istrue(self,email):
        try:
            email_list = []
            email_obj = {}
            final_res = {}
            if isinstance(email, str) or isinstance(email, bytes):
                email_list.append(email)
            else:
                email_list = email

            for em in email_list:
                name, host = em.split('@')
                if email_obj.get(host):
                    email_obj[host].append(em)
                else:
                    email_obj[host] = [em]

            for key in email_obj.keys():
                host = random.choice(self.fetch_mx(key))
                self.logger.info('正在连接服务器...：%s' % host)
                s = smtplib.SMTP(host, timeout=10)
                for need_verify in email_obj[key]:
                    helo = s.docmd('HELO chacuo.net')
                    self.logger.debug(helo)

                    send_from = s.docmd('MAIL FROM:<3121113@sds.net.ddas.cc>') #声明自己的邮箱，自己改
                    self.logger.debug(send_from)
                    send_from = s.docmd('RCPT TO:<%s>' % need_verify)
                    self.logger.debug(send_from)
                    if send_from[0] == 250 or send_from[0] == 451:
                        final_res[need_verify] = True  # 存在
                    elif send_from[0] == 550:
                        final_res[need_verify] = False  # 不存在
                    else:
                        final_res[need_verify] = None  # 未知
                s.close()

            return final_res
        except Exception as e:
            traceback.print_exc()
            return final_res
    
    def fetch_mx(self,host):
        '''
        解析服务邮箱
        :param host:
        :return:
        '''
        self.logger.info('正在查找邮箱服务器')
        answers = dns.resolver.query(host, 'MX')
        res = [str(rdata.exchange)[:-1] for rdata in answers]
        self.logger.info('查找结果为：%s' % res)
        return res
class TaskPage(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()
        self.combo_box_style =combo_box_style
        self.basic_style = basic_style
        self.setStyleSheet(self.basic_style)

        self.result = {}  #保存结果
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('EmailAll')
        self.resize(1400, 900)

        self.input_format_label = QLabel('输入形式:')
        self.input_format_combo = QComboBox()
        self.input_format_combo.setStyleSheet(self.combo_box_style)
        self.input_format_combo.addItem('用户输入')
        self.input_format_combo.addItem('文件')
        self.input_format_combo.currentIndexChanged.connect(self.toggle_input_options)
        self.input_format_combo.setFixedWidth(180)
        self.input_format_combo.setFixedHeight(40) 

        self.save_format_label = QLabel('结果形式:')
        self.save_format_combo = QComboBox()
        self.save_format_combo.setStyleSheet(self.combo_box_style)
        self.save_format_combo.addItem('输出到界面')
        # self.save_format_combo.addItem('保存到文件')
        self.save_format_combo.setFixedWidth(180)
        self.save_format_combo.setFixedHeight(40)

        self.VerifyEmail = QCheckBox('验证邮箱有效性')
        self.VerifyEmail.setChecked(True)  #设置选中
        self.VerifyEmail.setFixedHeight(130)  # 设置复选框的高度为30像素

        self.export_button = QPushButton("导出")
        self.export_button.setFixedWidth(100)
        self.export_button.setFixedHeight(58)
        self.export_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.export_button.clicked.connect(self.export_data)

        # 输入url和可选项
        self.domain_label = QLabel('domain:')
        self.domain_input = QLineEdit()
        self.domain_input.setFixedHeight(50)
        self.domain_input.returnPressed.connect(self.get_set)  # 绑定回车事件

        self.generate_button = QPushButton('查询')
        self.generate_button.setFixedWidth(100)
        self.generate_button.setFixedHeight(58)
        self.generate_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.generate_button.clicked.connect(self.get_set)

         # 显示结果的布局
        self.result_layout = QHBoxLayout()

        # 左侧显示区域-url
        self.url_layout = QVBoxLayout()
        self.result_display_label = QLabel('结果:')
        self.result_url_display = QTextEdit()
        self.result_url_display.verticalScrollBar().setStyleSheet(scroll_style)
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
        layout_format.addWidget(self.VerifyEmail)
        layout_format.addWidget(self.export_button)
        layout_format.addStretch(1)
        
        layout.addLayout(layout_format)

        layout_file = QHBoxLayout()
        layout.addLayout(layout_file)

        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.domain_input)
        domain_layout.addWidget(self.generate_button)

        layout.addLayout(domain_layout)

        layout.addLayout(self.result_layout)
        
        self.setLayout(layout)

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
            self.result_url_display.setVisible(True)
            self.result_url_display.clear()
        elif index == 1:  # 保存到文件
            self.result_url_display.clear()
            self.result_url_display.setVisible(True)

    def get_set(self, event=None):
        self.result_url_display.clear()
        self.generate_button.setEnabled(False)  # 将按钮设置为不可点击

        self.result_url_display.setTextColor(QColor("green"))
        self.result_url_display.append("开始查询...")

        current_type = self.input_format_combo.currentText()
        self.input = self.domain_input.text()
        # 检查复选框是否被选中
        if current_type == "用户输入" and not self.input:
            QMessageBox.warning(self, '错误', '请提供域名。')
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
        verifyEmail = self.VerifyEmail.isChecked()
        self.thread1 = WorkerThread(model,self.input,verifyEmail)
        self.thread1.finished.connect(self.handle_thread_finished)
        self.thread1.start()
        
    def handle_thread_finished(self,result,final_verify_dict):
        save_type = self.save_format_combo.currentIndex()
        if result:
            self.result = result
            if save_type == 1:   #保存到文件
                now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                url_result_file_path = now_time + "_EmaillAll.json"
                json_data = json.dumps(self.result, indent=4)
                with open(url_result_file_path, "a+", encoding='utf-8') as f:
                    f.write(json_data)
                self.result_url_display.append("查询完成")
                self.result_url_display.append("结果已经保存到当前运行路径下："+ url_result_file_path)
            else:
                email_list = result.get("email")
                if email_list:
                    self.result_url_display.append(f"当前获取了 {len(email_list)} 条数据")
                    for item in email_list:
                        self.result_url_display.append(item[1])  # 只显示邮箱地址
                other_info = result.get("other")
                if other_info:
                    self.result_url_display.append(other_info)
                if final_verify_dict:
                    self.result_url_display.append(f"验证情况")
                    for key,value in final_verify_dict:
                        self.result_url_display.append(key + "->" + str(value))  # 只显示邮箱地址
        self.result_url_display.append("查询完成")
        self.generate_button.setEnabled(True)  # 将按钮设置为可点击
    
    def export_data(self, event=None):
        if self.result:
            now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            url_result_file_path = now_time + "_EmaillAll.json"
            json_data = json.dumps(self.result, indent=4)
            with open(url_result_file_path, "a+", encoding='utf-8') as f:
                f.write(json_data)
            QMessageBox.information(self, "导出提示",f"导出成功,文件：{url_result_file_path}")
        else:
            QMessageBox.warning(None, "警告", "没有数据可以导出", QMessageBox.Ok)

class ConfigPage(QWidget):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()
        self.combo_box_style =combo_box_style
        self.basic_style = basic_style

        self.setStyleSheet(self.basic_style)
        self.init_ui()
        self.set_style()
        self.set_value()
        self.set_conn()  #绑定按钮点击事件

    def set_style(self):
        self.protocol_combobox.setStyleSheet(self.combo_box_style)

    def init_ui(self):
        layout = QHBoxLayout()  # 创建左右布局，QHBoxLayout 表示左右布局
        layout.setContentsMargins(10, 20, 0, 0)  # 设置该页面整体的左边距，上边距，右边距，底部边距
        # ----------------------------------------------------------------------开始设置左侧布局
        left_layout = QVBoxLayout()  # 设置左侧界面整体使用上下布局 ; QVBoxLayout表示：上下布局
        fofa_group = QGroupBox("veryvp配置")

        veryvp_layout = QHBoxLayout()  # 创建一个左右布局
        veryvp_layout.setContentsMargins(10, 30, 10, 30)  # 设置内边距
        veryvp_left_layout = QHBoxLayout()
        veryvp_username_label = QLabel("username:")
        self.veryvp_username_input = QLineEdit()
        veryvp_left_layout.addWidget(veryvp_username_label)
        veryvp_left_layout.addWidget(self.veryvp_username_input)

        veryvp_api_layout = QHBoxLayout()
        veryvpn_password_label = QLabel("password:")
        self.veryvp_passwd_input = QLineEdit()
        veryvp_api_layout.addWidget(veryvpn_password_label)
        veryvp_api_layout.addWidget(self.veryvp_passwd_input)

        # 将两个水平布局添加到垂直布局中
        veryvp_left_layout.addLayout(veryvp_api_layout)

        # 创建右侧布局用于放置修改按钮
        veryvp_right_layout = QVBoxLayout()

        # 将左侧布局和右侧布局添加到FOFA配置框中
        veryvp_layout.addLayout(veryvp_left_layout)
        veryvp_layout.addLayout(veryvp_right_layout)

        # 将FOFA配置框添加到主布局中
        fofa_group.setLayout(veryvp_layout)
        left_layout.addWidget(fofa_group)

        # =========================================github配置
        github_group = QGroupBox("github配置")
        github_layout = QHBoxLayout()  # 左右布局QHBoxLayout  上下布局：QVBoxLayout
        github_layout.setContentsMargins(10, 30, 10, 30)  # 设置内边距
        github_token_label = QLabel("github_token :")
        self.github_token_input = QLineEdit()

        github_layout.addWidget(github_token_label)
        github_layout.addWidget(self.github_token_input)

        github_group.setLayout(github_layout)
        left_layout.addWidget(github_group)

        # =====================================phonebook配置
        phonebook_group = QGroupBox("phonebook配置")
        phonebook_layout = QHBoxLayout()
        phonebook_layout.setContentsMargins(10, 30, 10, 30)  # 设置内边距
        phonebook_key_label = QLabel("pb_key:")
        self.pb_key_input = QLineEdit()

        phonebook_layout.addWidget(phonebook_key_label)
        phonebook_layout.addWidget(self.pb_key_input)

        phonebook_group.setLayout(phonebook_layout)
        left_layout.addWidget(phonebook_group)

        # =========================================snov配置
        snov_group = QGroupBox("snov配置")
        snov_layout = QHBoxLayout()
        snov_layout.setContentsMargins(10, 30, 10, 30)  # 设置内边距
        snov_username_label = QLabel("username:")
        self.snov_username_input = QLineEdit()
        snov_passwd_label = QLabel("password:")
        self.snov_password_input = QLineEdit()

        snov_layout.addWidget(snov_username_label)
        snov_layout.addWidget(self.snov_username_input)

        snov_layout.addWidget(snov_passwd_label)
        snov_layout.addWidget(self.snov_password_input)

        snov_group.setLayout(snov_layout)
        left_layout.addWidget(snov_group)

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
        self.protocol_combobox.setStyleSheet(self.combo_box_style)

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

    def set_value(self):
        config = configparser.ConfigParser()
        try:
            config.read('emailall/config.ini')
            veryvp_username = config.get('credentials', 'veryvp_username')
            veryvp_password = config.get('credentials', 'veryvp_password')
            github_token = config.get('credentials', 'github_token')
            snov_username = config.get('credentials', 'snov_username')
            snov_password = config.get('credentials', 'snov_password')
            pb_key = config.get('credentials', 'pb_key')
            is_use_proxy = config.get('credentials', 'is_use_proxy')
            proxy_type = config.get('credentials', 'proxy_type')
            proxy_server_ip = config.get('credentials', 'proxy_server_ip')
            proxy_port = config.get('credentials', 'proxy_port')
            self.veryvp_username_input.setText(veryvp_username)
            self.veryvp_passwd_input.setText(veryvp_password)
            self.github_token_input.setText(github_token)
            self.snov_username_input.setText(snov_username)
            self.snov_password_input.setText(snov_password)
            self.pb_key_input.setText(pb_key)
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
    # 使用示例
    def write_config_file(self):
        filename = "emailall/config.ini"
        if not os.path.exists(filename):
            config = configparser.ConfigParser()
            config['credentials'] = {}
            with open(filename, 'w') as configfile:
                config.write(configfile)

        # 要写入的新配置值
        new_values = {
            "veryvp_username": self.veryvp_username_input.text(),
            "veryvp_password":self.veryvp_passwd_input.text(),
            "github_token":self.github_token_input.text(),
            "snov_username":self.snov_username_input.text(),
            "snov_password":self.snov_password_input.text(),
            "pb_key":self.pb_key_input.text(),
            'is_use_proxy': '1' if self.is_use_proxy_checkbox.isChecked() else '0',
            'proxy_type': self.protocol_combobox.currentText(),
            'proxy_server_ip': self.proxy_ip_input.text(),
            'proxy_port': self.proxy_port_input.text()
        }
        # 将新配置值写入 config.ini 文件中
        for key, value in new_values.items():
            section = "credentials"
            config = configparser.ConfigParser()
            config.read(filename)
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, key, value)
            with open(filename, 'w') as configfile:
                config.write(configfile)  

    def save_config(self, event=None):
        choice = QMessageBox.question(
            self,
            '确认','是否保存？')
        if choice == QMessageBox.Yes:
            # print(api_data)
            self.write_config_file()
            QMessageBox.information(self, "保存成功",
                                    "如果你修改了代理配置并希望立刻应用到shodan查询，需要重启程序，其他的修改可以保存后点击\"重新加载\"即可")

class ExplanationPage(QWidget):
    def __init__(self,basic_style):
        super().__init__()
        self.basic_style = basic_style

        self.setStyleSheet(self.basic_style)
        
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()  
        layout.setContentsMargins(10, 20, 0, 0)  # 设置该页面整体的左边距，上边距，右边距，底部边距

        text = QTextBrowser()
        text.setOpenExternalLinks(True)  # 设置打开外部链接的方式为在默认浏览器中打开

        # 创建滚动区域并设置文本编辑框为其子部件
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 设置滚动区域自适应大小
        scroll_area.setWidget(text)  # 设置文本编辑框为滚动区域的子部件
        scroll_area.setStyleSheet(scroll_style)

        text.setHtml("""
    <p> 1.注册地址 </p>
    <p> - veryvp: <a href='http://www.veryvp.com/'> http://www.veryvp.com/ </a> </p>
    <p> - github : <a href='https://www.github.com'> https://www.github.com  </a>   </p>
    <p> - snov: <a href='https://app.snov.io/'> https://app.snov.io/   </a> </p>
    <p> - phonebook: <a href='https://phonebook.cz/'> https://phonebook.cz/ </a>   </p>
    
    <p>2.其他    </p>
    <p> - veryvp和snov去网站免费注册    </p>
    <p> - GitHub的token去设置里创建一个即可    </p>
    <p> - phonebook的key访问<a href='https://phonebook.cz/'> https://phonebook.cz/ </a>然后查看源代码，将`API_KEY`的值填入即可  </p>
    
    <p> 3.邮箱信息收集主要来源    </p>
    <p>    - Search    </p>
    <p>    - Ask    </p>
    <p>    - Baidu    </p>
    <p>    - Bing    </p>
    <p>    - Google    </p>
    <p>    - QWant    </p>
    <p>    - SO    </p>
    <p>    - Sougou    </p>
    <p>    - GithubApi    </p>
    <p>    - DataSets    </p>
    <p>    - Email-Format    </p>
    <p>    - Skymem    </p>
    <p>    - Veryvp    </p>
    <p>    - PhoneBook    </p>
    <p>    - Snov    </p>
        """)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self,basic_style,combo_box_style):
        super().__init__()

        self.basic_style = basic_style
        self.combo_box_style = combo_box_style
        
        self.setWindowTitle("tools")
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

        self.TextProcessor = TaskPage(self.basic_style,self.combo_box_style)
        self.password_generator_page = ConfigPage(self.basic_style,self.combo_box_style)
        self.explanation_page = ExplanationPage(self.basic_style)

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
        # self.setStyleSheet("background-color: #ffffff;")

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
        self.function_tabs.addTab(self.TextProcessor, QIcon(this_dir+"/icon/text.png"), "查询")
        self.function_tabs.addTab(self.password_generator_page, QIcon(this_dir+"/icon/config.png"), "config")
        self.function_tabs.addTab(self.explanation_page, QIcon(this_dir+"/icon/config.png"), "说明")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
