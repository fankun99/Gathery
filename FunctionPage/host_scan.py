#!/usr/bin/env python
# -*- conding:utf-8 -*-
import threading
import re,queue,requests,time
import traceback

queues = queue.Queue()
info_queue = queue.Queue()
threadLock = threading.Lock()
requests.packages.urllib3.disable_warnings() #屏蔽ssl报错
threads_complete = True
queues_size = 0 #存放总的数量
now_size = 0 #现在进度
switch = 1 #开关

class get_therad(threading.Thread):   #网络请求线程
    def __init__(self,url_ip,name,result_display,log_display):
        threading.Thread.__init__(self)
        self.url_ip = url_ip
        self.name = name
        self.result_display = result_display
        self.log_display = log_display

    def run(self):
        threadLock.acquire()
        # print("线程" + self.name+'启动')
        threadLock.release()
        while not self.url_ip.empty():
            url_ips = self.url_ip.get()
            for i in ['http://','https://']:
                url = i + url_ips[1] +":"+ str(url_ips[2])
                host = url_ips[0]+":"+str(url_ips[2])
                port = url_ips[2]
                headers = {
                    'host': '%s'%(host),
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
                    'Connection': 'close'
                }
                try:
                    response = requests.get(url=url, headers=headers,timeout=3,verify=False,allow_redirects=False)#忽略ssl问题和禁止302、301跳转
                    response.encoding = 'utf-8'
                    threadLock.acquire()
                    data = re_handle(url,host,response.text,response.headers,response.status_code)#url、host、响应体、响应头、响应码
                    threadLock.release()
                except Exception as e:
                    traceback.print_exc()
                    threadLock.acquire()
                    threadLock.release()
            
        threadLock.acquire()
        print("退出线程：" + self.name)
        threadLock.release()

class handle_therad(threading.Thread):  #独立线程 处理数据线程
    def __init__(self,result_display):
        threading.Thread.__init__(self)
        self.result_display = result_display
        self.info_list=[] #

    def run(self):
        while threads_complete:
            info_complete =True
            try:
                if len(self.info_list) == 0:
                    info = info_queue.get(timeout=3)
                    self.info_list.append(info)
                    for key, values in info.items():
                        self.result_display.append(str(key))
                        for _key,val in values.items():
                            formatted_text = f"   --><font color='blue'>[{_key}]</font> {val}"
                            self.result_display.append(formatted_text)
                else:
                    info = info_queue.get(timeout=3)

                    for i in self.info_list:
                        if info[0] == i[0] and info[2] == i[2] and info[3] == i[3]:
                            info_complete = False
                            break
                    if info_complete:
                        self.info_list.append(info)
                        for key, values in info.items():
                            for _key,val in values.items():
                                formatted_text = f"   --><font color='blue'>[{_key}]</font> {val}"
                                self.result_display.append(formatted_text)
                                # self.result_display.append( "   -->[" + str(_key) + "] " + val)
            except Exception as e:
                print(e)
    
    def get_info_list(self,):
        return self.info_list

class read_file_data(threading.Thread):  #独立线程 加载数据，防止内存爆炸
    def __init__(self,ip_addresses_list,hostnames_list,thread_num,result_display,log_display,port_list):
        threading.Thread.__init__(self)
        self.num = int(thread_num)
        self.ip_addresses_list = ip_addresses_list
        self.hostnames_list = hostnames_list
        self.result_display = result_display
        self.log_display = log_display
        self.port_list = port_list

    def run(self):#读取host.txt和ip.txt
        ip_list=self.ip_addresses_list
        host_list=self.hostnames_list

        global queues_size
        queues_size = (len(ip_list) * len(host_list)) * 2 * len(self.port_list)
        self.log_display.append('一共需要碰撞' + str(queues_size) + '次！')

        for host in host_list:
            for ip in ip_list:
                for i in self.port_list:
                    queues.put((host, ip,i))
                    global now_size
                    now_size += 1
            while True:
                if queues.qsize() > self.num*4:
                    global switch
                    switch = 0
                else:
                    break
        switch = 0

def re_handle(url,host,data,head,code):    #网页返回内容处理
    info = {}
    try:
        title = "title: " + str(re.search('<title>(.*)</title>',data).group(1))  # 获取标题
    except:
        title = u"获取标题失败"
    info[url] = {}
    #只要响应码200、301、302的，其他的都不要
    if code == 302 or code == 301:
        if 'Location' in head:
            info[url]["host"] = host
            info[url]["data_len"] = str(len(data))
            info[url]["code"] = str(code)
            info[url]["head_Location"] = head['Location']
            if '//cas.baidu.com' not in head['location'] and '//www.baidu.com' not in head['location'] and '//m.baidu.com' not in head['location']:
                info_queue.put(info)
    
    elif '百度一下' in title:
        info[url]["host"] = host
        info[url]["data_len"] = str(len(data))
        info[url]["title"] = str(title)
        print('无效数据' + str(info),code)

    elif code == 200:
        info[url]["host"] = host
        info[url]["data_len"] = str(len(data))
        info[url]["title"] = str(title)
        if len(data) > 20:  # 去除掉一些无用数据
            info_queue.put(info)
    else:
        info[url]["host"] = host
        info[url]["data_len"] = str(len(data))
        info[url]["title"] = str(title)
        print(info,code)

def run_therad(ip_addresses_list,hostnames_list,port_text,thread_num,result_display,log_display):# 创建新线程
    if port_text:
        port_list = [port.strip() for port in port_text.split(',')]
    else:
        port_list = [80,443]
    read_file_data_therads = read_file_data(ip_addresses_list,hostnames_list,thread_num,result_display,log_display,port_list)
    read_file_data_therads.start()

    while switch:
        continue

    threads = []
    for i in range(thread_num):
        thread = get_therad(queues,i,result_display,log_display)
        thread.start()
        threads.append(thread)

    handle_therads = handle_therad(result_display)
    handle_therads.start()

    read_file_data_therads.join()
    for t in threads:
        t.join()
    
    log_display.append('=====结 束 匹 配=====')
    global threads_complete
    threads_complete = False
    handle_therads.join()

    info_list = handle_therads.get_info_list()
    return info_list

