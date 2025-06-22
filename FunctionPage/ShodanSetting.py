import os
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget,  QPushButton, QComboBox, \
     QHBoxLayout, QCheckBox, QLineEdit,QGroupBox,QMessageBox
import configparser
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


class ShodanSetting(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 600)
        self.init_ui()
        self.SetStyle()
        self.ReadConfigFile()
        self.set_conn()  #绑定按钮点击事件
        self.setStyleSheet("QMainWindow, QPushButton,QLineEdit, QTextEdit,QCheckBox,QGroupBox {color: #fff; font-family: '微软雅黑'; font-size: 12pt; }"
            "QLineEdit, QTextEdit {background-color: #32337e; color: white; border:1px solid #5f68c3; border-radius: 10px;padding-left:15px;height:40px;}"
            "QLabel { font-family: '微软雅黑'; font-size: 12pt; color: #bac5cf; border: none; background: none;}"
            "QComboBox QAbstractItemView { color: white; }"
            "QWidget { background-color: #32337e; }" 
            """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0, stop: 0 #0c1dcd, stop: 1 #bd4ade);
                border: 2px solid #65b5e9;
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
            }"""
        )
    
    def SetStyle(self):
        self.setStyleSheet("background-color: #32337e;")
        self.protocol_combobox.setStyleSheet("""
            QComboBox {
                border: 1px solid #5f68c3;
                border-radius: 10px;
                padding: 1px 10px 1px 1px;
                min-width: 8em;
                background-color: #32337e;
                color: #fff;
                height: 40px;
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
        """% (this_dir))

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
        config_info_group.setFixedHeight(800)  # 设置高度为200像素
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
            config.read('shodan/config.ini')
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
        filename = "shodan/config.ini"
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShodanSetting()
    window.show()
    sys.exit(app.exec_())
