from PyQt5.QtWidgets import ( QMainWindow, QLabel,
                             QHBoxLayout, QVBoxLayout, QApplication,  QSplitter, 
                             QListWidget,QWidget, 
                             QVBoxLayout, QHBoxLayout,
                             QVBoxLayout, 
                             QLabel,  QHBoxLayout, QWidget,
                             QListWidgetItem,  QApplication, QWidget, QSplitter,
                             QPushButton)
from PyQt5.QtGui import QFont, QIcon,QPixmap
from PyQt5.QtCore import Qt, QSize
import os
import FunctionPage.common
import urllib3
import sys

urllib3.disable_warnings()

def get_main_path():
    """
    Returns the absolute path of the last directory in the path of the main executable or script.
    If the program is frozen (i.e., packaged with PyInstaller), it returns the directory containing the .exe file.
    Otherwise, it returns the directory containing the main .py script.
    """
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        path = os.path.dirname(os.path.abspath(__file__))
    
    last_directory = os.path.basename(path)
    last_directory_absolute_path = os.path.join(os.path.dirname(path), last_directory)
    
    return last_directory_absolute_path

this_dir = get_main_path()
basic_style="""
    QMainWindow, QPushButton,QLineEdit, QTextEdit,QCheckBox,QGroupBox,QListWidget,QTableWidget {color: black; font-family: '微软雅黑'; font-size: 12pt; }
    QLineEdit, QTextEdit {background-color: white; color: black; border:1px solid #5f68c3; border-radius: 10px; padding-left:10px;}
    QLabel, QCheckBox { font-family: '微软雅黑'; font-size: 12pt; color: #34499a; border: none; background: none;}
    QPushButton {
        background: #868e95;
        border: 2px solid #5f68c3;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        padding: 10px 20px;
        text-align: center;
        margin: 5px;
    }
    QPushButton:hover {
        background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0, stop: 0 #bd4ade, stop: 1 #ededed);
        border: 2px solid #65b5e9;
    }
    QPushButton:pressed {
        background-color: #ededed;
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
""" % (this_dir.replace("\\","/"))

FunctionPage.common.this_dir = this_dir
FunctionPage.common.combo_box_style = combo_box_style

import FunctionPage.BasicInfo
import FunctionPage.EmailAllPage
import FunctionPage.get_Exchange_version
import FunctionPage.get_Zimbra_version
import FunctionPage.EmailURLGenerator
import FunctionPage.get_external_links
import FunctionPage.JSFinder
import FunctionPage.tools
# import FunctionPage.OneForAllPage
import FunctionPage.HostScan
import FunctionPage.shodanPage

class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gathery")
        self.setGeometry(300, 100, 2000, 1200)

        self.select_style = "QPushButton { color: #f78018;  border: none; padding: 10px; border-radius: 5px;  font-weight: bold; text-align: left;}"
        self.dedault_style = "QPushButton { color: #fff;  border:none;  padding: 10px; border-radius: 5px;  font-weight: bold; text-align: left;}"
        self.button_font = QFont()
        self.button_font.setPointSize(12)
        self.button_font.setFamily("Microsoft YaHei")

        self.font_style = "QListWidget::item { color: #fff;border:none }"
        self.selection_style = """
                                QListWidget::item:selected { background-color: #868e95; border-radius: 20px; border:none;outline: none;}
                                """
        self.item_font = QFont()  
        self.item_font.setPointSize(10)
        self.item_font.setFamily("Microsoft YaHei")
        self.item_font.setBold(True)
        self.basic_style = basic_style
        self.combo_box_style = combo_box_style
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_widget.setStyleSheet("background-color: white;")

        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)
        left_widget.setLayout(left_layout)

        logo_layout = QHBoxLayout()

        circular_button = QPushButton()
        circular_button.setFixedSize(200, 100)
        pixmap = QPixmap(this_dir+'/icon/logo.jpg')
        icon = pixmap.scaled(circular_button.size(), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)

        circular_button.setIcon(QIcon(icon))
        circular_button.setIconSize(circular_button.size()) 
        circular_button.setStyleSheet("""
            QPushButton {
                border-radius: 90px; 
                background-color: #313131;
                background-repeat: no-repeat;
            }
        """)

        logo_layout.addWidget(circular_button)

        self.info_button = QPushButton("信息收集")
        self.info_button.setFont(self.button_font)
        self.info_button.setIcon(QIcon(this_dir+"/icon/down.png"))
        self.info_button.setIconSize(QSize(13, 13))
        self.info_button.setLayoutDirection(Qt.RightToLeft) 
        self.info_button.setStyleSheet(self.dedault_style)

        self.info_submenu = QListWidget()
        self.info_submenu.setFixedHeight(350)
        self.info_submenu.setFrameStyle(QListWidget.NoFrame)
        self.info_submenu.hide()
        self.info_submenu.itemClicked.connect(self.handle_submenu_click)
        self.info_submenu.setStyleSheet(self.font_style + self.selection_style)
        self.info_submenu.setFocusPolicy(Qt.NoFocus)
        
        self.add_submenu_item(self.info_submenu, "域名/IP 信息查询")
        self.add_submenu_item(self.info_submenu, "HOST碰撞")
        self.add_submenu_item(self.info_submenu, "网站JS爬取")
        self.add_submenu_item(self.info_submenu, "网站外链爬取")
        self.add_submenu_item(self.info_submenu, "emailall邮箱收集")
        self.add_submenu_item(self.info_submenu, "shodan信息收集")

        # -------------------------------------------------------------------------
        self.products_button = QPushButton("版本获取")
        self.products_button.setFont(self.button_font)
        self.products_button.setIcon(QIcon(this_dir+"/icon/down.png"))
        self.products_button.setIconSize(QSize(13, 13)) 
        self.products_button.setLayoutDirection(Qt.RightToLeft)
        self.products_button.setStyleSheet(self.dedault_style)

        self.GetVersion_submenu = QListWidget()
        self.GetVersion_submenu.setFixedHeight(150)
        self.GetVersion_submenu.setFrameStyle(QListWidget.NoFrame)
        self.GetVersion_submenu.hide()
        self.GetVersion_submenu.itemClicked.connect(self.handle_submenu_click)
        self.GetVersion_submenu.setStyleSheet(self.font_style + self.selection_style)
        self.GetVersion_submenu.setFocusPolicy(Qt.NoFocus) 
        self.add_submenu_item(self.GetVersion_submenu, "Exchange版本获取")
        self.add_submenu_item(self.GetVersion_submenu, "Zimbra版本获取")
        # ---------------------------------------------------------------------------
        self.get_mail_url_button = QPushButton("油服url生成")
        self.get_mail_url_button.setFont(self.button_font)
        self.get_mail_url_button.setStyleSheet(self.dedault_style)
        self.get_mail_url_button.clicked.connect(self.handle_mail_url_click)
        # ---------------------------------------------------------------------------
        self.tools_button = QPushButton("小工具合集")
        self.tools_button.setFont(self.button_font)
        self.tools_button.setStyleSheet(self.dedault_style)
        self.tools_button.clicked.connect(self.handle_mail_url_click)

        self.info_button.clicked.connect(lambda: self.toggle_submenu(self.info_submenu))
        self.products_button.clicked.connect(lambda: self.toggle_submenu(self.GetVersion_submenu))
        
        left_layout.addLayout(logo_layout)
        left_layout.addSpacing(20) 
        left_layout.addWidget(self.info_button)
        left_layout.addWidget(self.info_submenu)
        left_layout.addSpacing(20)  
        left_layout.addWidget(self.products_button)
        left_layout.addWidget(self.GetVersion_submenu)
        left_layout.addSpacing(20)  # 添加空白间距，数值可以调整
        left_layout.addWidget(self.get_mail_url_button)
        left_layout.addWidget(self.tools_button)
        # ---------------------------------------------------右侧
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        # content_widget.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0, stop: 0 #1c154a, stop: 1 #4654a7);")  #设置渐变背景色
        content_widget.setStyleSheet("background-color: white")  #设置背景色

        self.content_label = QLabel("欢迎使用Gathery")
        self.content_label.setFont(QFont("Arial", 20))
        
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setStyleSheet("color: #bac5cf; font-weight: bold;")
        
        content_layout.addWidget(self.content_label)
        
        # 域名/IP 信息查询
        self.BasicInfo_widget = FunctionPage.BasicInfo.MainWindow(self.basic_style,self.combo_box_style)
        self.BasicInfo_widget.setVisible(False)

        # host碰撞
        self.host_scan_widget = FunctionPage.HostScan.HostScanWidget(self.basic_style)
        self.host_scan_widget.setVisible(False)

        # 外链提取工具页面
        self.external_links_widget = FunctionPage.get_external_links.get_external_links(self.basic_style,self.combo_box_style)
        self.external_links_widget.setVisible(False)

        # 创建 JsCrawlerWidget 页面
        self.js_crawler_widget = FunctionPage.JSFinder.JSFinder(self.basic_style,)
        self.js_crawler_widget.setVisible(False)

        # EmaillAll 页面
        self.EmaillAll_widget = FunctionPage.EmailAllPage.MainWindow(self.basic_style,self.combo_box_style)
        self.EmaillAll_widget.setVisible(False)

        # OneForAllPage 页面
        # self.OneForAll_widget = FunctionPage.OneForAllPage.MainWindow(self.basic_style,self.combo_box_style)
        # self.OneForAll_widget.setVisible(False)

        # shodanAPI 页面
        self.shodanApi_widget = FunctionPage.shodanPage.MainWindow(self.basic_style,self.combo_box_style)
        self.shodanApi_widget.setVisible(False)

        # 创建邮件服务器url获取的页面
        self.get_mail_url_widget = FunctionPage.EmailURLGenerator.EmailURLGenerator(self.basic_style,self.combo_box_style)
        self.get_mail_url_widget.setVisible(False)

        # 创建Zimbra版本获取页面
        self.get_Zimbra_version_widght = FunctionPage.get_Zimbra_version.get_Zimbra_version(self.basic_style,self.combo_box_style)
        self.get_Zimbra_version_widght.setVisible(False)

        # 创建Exchange版本获取页面
        self.get_Exchange_version_widght = FunctionPage.get_Exchange_version.get_Exchange_version(self.basic_style,self.combo_box_style)
        self.get_Exchange_version_widght.setVisible(False)

        # 小工具合集页面
        self.tools_widget = FunctionPage.tools.MainWindow(self.basic_style,self.combo_box_style)
        self.tools_widget.setVisible(False)

        # 将外链提取工具QWidget添加到右侧布局中
        content_layout.addWidget(self.BasicInfo_widget)
        content_layout.addWidget(self.host_scan_widget)
        content_layout.addWidget(self.external_links_widget)
        content_layout.addWidget(self.js_crawler_widget)
        content_layout.addWidget(self.EmaillAll_widget)
        # content_layout.addWidget(self.OneForAll_widget)
        content_layout.addWidget(self.shodanApi_widget)

        content_layout.addWidget(self.get_Zimbra_version_widght)
        content_layout.addWidget(self.get_Exchange_version_widght)

        content_layout.addWidget(self.get_mail_url_widget)

        content_layout.addWidget(self.tools_widget)
        # ---------------------------------------------------左侧
        splitter = QSplitter()
        
        splitter.addWidget(left_widget)
        splitter.addWidget(content_widget)
        # 设置左侧背景颜色
        left_widget.setStyleSheet("background-color: #313131; border-radius: 30px;")
        # left_widget.setStyleSheet("background-color: #304156; border-radius: 30px;")

        # 设置右侧背景颜色
        content_widget.setStyleSheet("background-color: white")  #设置渐变背景色

        # 设置左右比例
        splitter.setSizes([self.width() // 7, self.width() // 1])

        main_layout.addWidget(splitter)
        main_layout.setContentsMargins(10, 40, 0, 40)  # 设置主布局的外边距为零(左、上、右、下)
       
        self.buttons = {
            '信息收集': self.info_button,
            '版本获取': self.products_button,
            '油服url生成': self.get_mail_url_button,
            '小工具合集': self.tools_button
        }

        for button in self.buttons.values():
            button.clicked.connect(self.handle_button_click)

    def add_submenu_item(self, submenu, text, width=None):
        item = QListWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        item.setSizeHint(QSize(150, 50))  # 设置每个选项的宽度和高度
        item.setFont(self.item_font)  # 将字体对象应用于QListWidgetItem
        
        submenu.addItem(item)

    def toggle_submenu(self, submenu):
        if submenu.isHidden():
            submenu.show()
        else:
            submenu.hide()
    
    def handle_submenu_click(self, item):
        # 取消先前选择的项目
        buttons = [self.tools_button, self.get_mail_url_button, self.info_button, 
                   self.products_button
                ]
        for button in buttons:
            button.setStyleSheet(self.dedault_style)

        submenus = [self.info_submenu, self.GetVersion_submenu]
        for submenu in submenus:
            for i in range(submenu.count()):
                submenu.item(i).setSelected(submenu.item(i) == item)

        if item.listWidget() == self.info_submenu:
            self.info_button.setStyleSheet(self.select_style)
        elif item.listWidget() == self.GetVersion_submenu:
            self.products_button.setStyleSheet(self.select_style)

        font = QFont("Arial", 16)  # 创建一个字体对象，设置字体为Arial，大小为12
        self.content_label.setFont(font)  # 将字体对象设置给 QLabel
        self.content_label.setText(f"{item.text()}")
        self.content_label.setStyleSheet("border: none; background: none; color: #bac5cf; font-weight: bold; ")

        # 映射菜单项到相应的小部件
        widget_mapping = {
            "域名/IP 信息查询":self.BasicInfo_widget,
            "HOST碰撞":self.host_scan_widget,
            "网站外链爬取": self.external_links_widget,
            "网站JS爬取": self.js_crawler_widget,
            "emailall邮箱收集": self.EmaillAll_widget,
            "shodan信息收集": self.shodanApi_widget,

            "Zimbra版本获取": self.get_Zimbra_version_widght,
            "Exchange版本获取": self.get_Exchange_version_widght,

        }
        # 设置小部件的可见性 self.OneForAll_widget,
        for widget in [self.BasicInfo_widget,self.host_scan_widget,self.external_links_widget, self.js_crawler_widget, self.EmaillAll_widget,
                        self.get_Zimbra_version_widght,self.get_Exchange_version_widght,
                       self.shodanApi_widget,
                       ]:
            widget.setVisible(widget_mapping.get(item.text()) == widget)

        self.get_mail_url_widget.setVisible(False)
        self.tools_widget.setVisible(False) 
           
    def handle_mail_url_click(self):
        # 取消先前选择的项目
        for i in range(self.info_submenu.count()):
            self.info_submenu.item(i).setSelected(False)
        for i in range(self.GetVersion_submenu.count()):
            self.GetVersion_submenu.item(i).setSelected(False)
            
        font = QFont("Arial", 16)
        self.content_label.setFont(font)
        sender_button = self.sender()  # 获取发送信号的对象，即被点击的按钮
        button_text = sender_button.text()  # 获取按钮的文本内容
        if button_text == "小工具合集":
            self.get_mail_url_widget.setVisible(False)
            self.tools_widget.setVisible(True)
        else:
            self.get_mail_url_widget.setVisible(True)
            self.tools_widget.setVisible(False)

        self.content_label.setText(f"{button_text}")

        # 隐藏子菜单的所有部件
        self.BasicInfo_widget.setVisible(False)
        self.host_scan_widget.setVisible(False)
        self.external_links_widget.setVisible(False)
        self.js_crawler_widget.setVisible(False)
        self.get_Zimbra_version_widght.setVisible(False)
        self.get_Exchange_version_widght.setVisible(False)
        self.EmaillAll_widget.setVisible(False)
        # self.OneForAll_widget.setVisible(False)
        self.shodanApi_widget.setVisible(False)
    def handle_button_click(self):
        sender_button = self.sender()  # 获取发送信号的按钮
        button_text = sender_button.text()  # 获取按钮的文本内容
        self.set_styles(button_text)

    def set_styles(self, selected_button_text):
        for button_text, button in self.buttons.items():
            if button_text == selected_button_text:
                button.setStyleSheet(self.select_style)
            else:
                button.setStyleSheet(self.dedault_style)

def main():
    app = QApplication(sys.argv)
    window = AdminPanel()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
