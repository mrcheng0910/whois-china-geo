#!/usr/bin/env python
# encoding:utf8

"""
    静态配置及操作对象
=======================

version   :   1.0
author    :   @`13
time      :   2016.11.5
"""

import json
import logging
import logging.config
import datetime
import os
import sys


# 请检查系统文件命名是否正确,请勿随意更改任何文件的名称
SYS_NAME = "get_whois"  # 系统文件名
DIRECTORY_NAME = "Setting"      # 当前文件名
JSON_NAME = "setting.json"      # JSON配置文件名
LOGGER_NAME = "logger.conf"     # 日志系统配置文件名
WHOIS_Data_MOUDLE_NAME = "WhoisData"    # WHOIS　DATA模块名

class Static:
    """静态配置及操作对象初始化"""
    def __init__(self):
        pass
        # print id(self)

    # 配置文件路径
    PATH_LOGGER_CONF = None  # 日志系统配置文件
    PATH_JSON = None         # 配置文件路径
    # 静态变量
    PROCESS_NUM = None  # 处理线程数
    COMMIT_NUM = None   # 事务提交数
    # 对象
    LOGGER = None       # 系统主日志对象
    # Database
    HOST = None     # 数据库地址
    PORT = None     # 端口
    USER = None     # 用户名
    PASSWD = None   # 密码
    CHARSET = None  # 字符编码
    # Whois
    DATABASE_NAME = None    # 系统数据库名
    WHOIS_TABLE = None      # whois数据表
    WHOWAS_TABLE = None     # whowas数据表
    DOMAIN_TABLE = None     # 域名表
    FQDN_TABLE = None       # 全域名表
    SRVIP_TABLE = None      # whois服务器ip表
    WHOIS_TLD_TABLE = None      # whois服务器与tld映射表
    WHOIS_FUNC_FILE = None      # whois服务器提取函数映射表
    PROXY_SOCKS_FLAG = None     # 是否使用代理
    PROXY_SOCKS_TABLE = None    # 代理socks表
    PROXY_SOCKS_REFRESH = None  # 代理socks刷新频率
    SOCKS_TIMEOUT = None        # socks连接超时
    SOCKS_RECONNECT = None      # socks失败重连数
    _shared_state = {}

    @staticmethod
    def init():
        """初始化"""
        Static.static_value_init()
        Static.log_init()

    @staticmethod
    def static_value_init():
        """静态值初始化"""
        # 获取当前绝对路径
        sys.path.append('..')
        now_path = os.path.abspath('./')
        root_path = now_path.split(SYS_NAME)[0]
        root_path += SYS_NAME

        Static.PATH_JSON = root_path + '/' + DIRECTORY_NAME + '/' + JSON_NAME
        Static.PATH_LOGGER_CONF = root_path + '/' + DIRECTORY_NAME + '/' + LOGGER_NAME
        try:
            # 读取JSON文件获取配置
            jsonFile = file(Static.PATH_JSON)
            setting = json.load(jsonFile)
            jsonFile.close()
            # 流程
            Static.PROCESS_NUM = setting['System']['processNum']
            Static.COMMIT_NUM = setting['System']['commitNum']
            Static.PROXY_SOCKS_FLAG = setting['System']['proxySocks']
            # 数据库
            Static.PORT = setting['database']['port']
            Static.USER = setting['database']['user']
            Static.HOST = setting['database']['host']
            Static.PASSWD = setting['database']['passwd']
            Static.CHARSET = setting['database']['charset']
            # 核心数据
            Static.DATABASE_NAME = setting['whoisData']['DatabaseName']
            Static.WHOIS_TABLE = setting['whoisData']['whoisTable']
            Static.WHOWAS_TABLE = setting['whoisData']['whowasTable']
            Static.DOMAIN_TABLE = setting['whoisData']['domainTable']
            Static.FQDN_TABLE = setting['whoisData']['FQDN_Table']
            # 辅助数据
            Static.SRVIP_TABLE = setting['whoisData']['svripTable']
            Static.WHOIS_FUNC_FILE = str(root_path + '/' + WHOIS_Data_MOUDLE_NAME + '/')
            Static.WHOIS_FUNC_FILE += str(setting['whoisData']['whoisFuncFile'])
            Static.WHOIS_TLD_TABLE = setting['whoisData']['whoisTldTable']
            # socket链接
            Static.SOCKS_TIMEOUT = setting['whoisData']['socksTimeout']
            Static.SOCKS_RECONNECT = setting['whoisData']['socksReconnect']
            Static.PROXY_SOCKS_TABLE = setting['whoisData']['proxySocksTable']
            Static.PROXY_SOCKS_REFRESH = setting['whoisData']['proxyipRefresh']
        except Exception as e:
            print '配置文件读取出错: ' + str(e)
            exit(0)

    @staticmethod
    def log_init():
        """对象出初始化"""
        logging.config.fileConfig(Static.PATH_LOGGER_CONF)
        Static.LOGGER = logging.getLogger('main')  # 日志

    @staticmethod
    def get_now_time():
        """获取本地时间"""
        return str(datetime.datetime.now()).split('.')[0]

if __name__ == '__main__':
    # Demo
    print Static.get_now_time()   # 获取当前事件
    Static.init()                 # 全部初始化
    # Static.init()
    # print Static.PATH_CONF
    # print Static.get_now_time()






