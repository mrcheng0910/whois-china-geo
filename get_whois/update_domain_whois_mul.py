#!/usr/bin/env python
# encoding:utf-8

"""
更新第一次获取失败的域名的WHOIS信息
"""

import time
import threading
from threading import Thread
from Queue import Queue
from collections import defaultdict
from datetime import datetime


num_thread = 10      # 线程数量
queue = Queue()     # 任务队列，存储sql
lock = threading.Lock()  # 变量锁

from Setting.global_resource import *  # 全局资源
from Setting.static import Static  # 静态变量,设置
from WhoisConnect import whois_connect  # Whois通信
from WhoisData.info_deal import get_result  # Whois处理函数
from data_base import MySQL
from config import SOURCE_CONFIG


Static.init()
Resource.global_object_init()
log_get_whois = Static.LOGGER

def fetch_whois(raw_domain=""):
    """
    获取whois信息
    :param raw_domain: 输入域名
    :return: whois信息字典 / 获取失败返回None
    """
    log_get_whois.info(raw_domain + ' - start')
    # 处理域名信息
    Domain = Resource.Domain(raw_domain)
    # domain = Domain.get_utf8_domain()             # 用于返回显示的域名（utf8格式）
    domain_punycode = Domain.get_punycode_domain()  # punycode编码域名
    tld = Domain.get_tld()  # 域名后缀
    WhoisSerAddr = Resource.TLD.get_server_addr(tld)  # 获取whois地址,失败=None
    WhoisSerIP = Resource.WhoisSrv.get_server_ip(WhoisSerAddr)  # 获取whois地址的ip(随机取一个),失败=None
    WhoisFunc = Resource.WhoisFunc.get_whois_func(WhoisSerAddr)  # 获取TLD对应的提取函数名称
    log_get_whois.info('whois : ' + str(WhoisSerAddr) + '->' + str(WhoisSerIP) +
                  ' use:' + str(WhoisFunc))
    # 获取用于通信的whois服务器地址
    # 优先级 : ip > whois地址 > None (失败)
    WhoisConnectAddr = WhoisSerIP
    if WhoisConnectAddr is None:
        WhoisConnectAddr = WhoisSerAddr
    if not WhoisConnectAddr:
        log_get_whois.error(raw_domain + ' - fail : whois通信地址获取失败')
        return None
    # 获取原始whois数据
    raw_whois_data = ''     # 原始whois数据
    data_flag = 1           # whois通信标记
    try:
        raw_whois_data = whois_connect.GetWhoisInfo(domain_punycode, WhoisConnectAddr).get()
    except whois_connect.WhoisConnectException as connect_error:
        data_flag = 0 - int(str(connect_error))
    if raw_whois_data is None:
        data_flag = -5  # 获取到空数据，flag = -5
    if raw_whois_data.find("No match for") != -1:
        data_flag=-3
    # 处理原始whois数据
    log_get_whois.info('flag : ' + str(data_flag))
    whois_dict = get_result(domain_punycode,
                            tld,
                            str(WhoisSerAddr),
                            WhoisFunc,
                            raw_whois_data,
                            data_flag)
    log_get_whois.info(raw_domain + ' - finish')
    return whois_dict


def fetch_resource_data():
    """
    获取待获取whois信息的域名集合
    """
    totals = []
    exists = []
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT domain FROM domain_info WHERE flag != 1')
    total_domains = db.fetch_all_rows()  # 得到总共的数量
    for i in total_domains:
        totals.append(i[0])
    db.close()

    fp = open('sec_domain_1.txt', 'r')

    for i in fp.readlines():
        exists.append(i.strip())
    fp.close()
    return list(set(totals)-set(exists))


def insert_db(result):
    """插入到数据库中"""
    db = MySQL(SOURCE_CONFIG)
    org_name = result['org_name']
    update_date = result['updated_date']
    domain = result['domain']
    reg_phone = result['reg_phone']
    reg_email = result['reg_email']
    exp_date = result['expiration_date']
    reg_name = result['reg_name']
    top_srv = result['top_whois_server']
    ns = result['name_server']
    reg_date = result['creation_date']
    flag = result['flag']
    status = result['domain_status']
    details = result['details']
    registrar_name = result['sponsoring_registrar']
    tld = result['tld']
    sec_srv = result['sec_whois_server']
    sql = 'UPDATE domain_info set org_name="%s", update_date="%s",reg_phone="%s",reg_email="%s",exp_date="%s",reg_name="%s",top_srv="%s",ns="%s",reg_date="%s",flag="%s",status="%s",details="%s",registrar_name="%s",tld="%s",sec_srv="%s" WHERE domain="%s" '
    db.update(sql % (org_name, update_date,reg_phone,reg_email,exp_date,reg_name,top_srv,ns,reg_date,flag,status,details,registrar_name,tld,sec_srv,domain))


    db.close()


def count_domain():
    """计算域名的数量
    :param q:线程编号
    :param queue: 任务队列
    """
    while 1:
        domain = queue.get()
        try:
            data = fetch_whois(domain)
        except:
            continue
        print data
        lock.acquire()  # 锁
        try:
            insert_db(data)
            write_domain(domain)
        except:
            pass
        lock.release()  # 解锁
        queue.task_done()
        time.sleep(1)  # 去掉偶尔会出现错误


def write_domain(domain):
    """
    将已获取的域名存入文件
    :param domain: 域名
    """
    fp = open('sec_domain_1.txt','a')
    fp.write(domain+'\n')
    fp.close()


def create_queue():
    """创建任务队列，即表名称"""
    query_domains = fetch_resource_data()
    for d in query_domains:
        queue.put(d)  # num 加入队列


def create_thread():
    """创建任务线程"""
    for q in range(num_thread):  # 开始任务
        worker = Thread(target=count_domain)
        worker.setDaemon(True)
        worker.start()
    queue.join()


def get_domain_whois():
    """主操作"""
    print str(datetime.now()), '开始统计数据库中域名数量'
    create_queue()
    create_thread()
    print str(datetime.now()), '结束统计数据库中域名数量'


if __name__ == '__main__':
    get_domain_whois()