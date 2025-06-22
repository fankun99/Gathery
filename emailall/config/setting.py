#!/usr/bin/python3
# coding=utf-8

import configparser
import pathlib

"""
配置文件
"""
# 路径设置
relative_directory = pathlib.Path(__file__).parent.parent  # EmailAll代码相对路径
modules_storage_dir = relative_directory.joinpath('modules')  # modules存放目录
result_save_dir = relative_directory.joinpath('result')

rule_func = list()

emails = list()

config = configparser.ConfigParser()
config.read('emailall/config.ini')

is_use_proxy = config.get('credentials', 'is_use_proxy')
if is_use_proxy == "1":
    proxy_type = config.get('credentials', 'proxy_type')
    proxy_server_ip = config.get('credentials', 'proxy_server_ip')
    proxy_port = config.get('credentials', 'proxy_port')
    proxy = {proxy_type: f"{proxy_server_ip}:{proxy_port}", 'https': f"{proxy_server_ip}:{proxy_port}"}
else:
    proxy = {}
