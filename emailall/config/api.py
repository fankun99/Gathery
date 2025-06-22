"""
API 配置文件
"""

import configparser

config = configparser.ConfigParser()
config.read('emailall/config.ini')

veryvp_username = config.get('credentials', 'veryvp_username')
veryvp_password = config.get('credentials', 'veryvp_password')
github_token = config.get('credentials', 'github_token')
snov_username = config.get('credentials', 'snov_username')
snov_password = config.get('credentials', 'snov_password')
pb_key = config.get('credentials', 'pb_key')





