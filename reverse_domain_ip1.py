# encoding:utf-8

"""
用来获取whois域名的IP地址
"""

import dns.resolver
from get_whois.data_base import MySQL
import time
import threading
from Queue import Queue
from threading import Thread
from datetime import datetime

from get_whois.config import SOURCE_CONFIG
num_thread = 30  # 线程数量
queue = Queue()  # 任务队列，存储sql
lock = threading.Lock()
domains_ip = []


def get_domain_from_db():
    """
    从数据库中获取已有whois服务器地址和已有的IP地址
    :return:
    """
    db = MySQL(SOURCE_CONFIG)
    sql = 'SELECT domain  FROM domain_info WHERE a_record ="" LIMIT 1000,10000'
    # sql = 'SELECT domain FROM `domain_info` WHERE ID BETWEEN 1012782 AND 1012933'
    db.query(sql)
    domains = db.fetch_all_rows()
    db.close()
    return domains


def domain2ip(domain):
    """
    域名解析为IP列表
    参数
        domain: string 待解析的域名

    返回值
        ips: list 域名解析后的ip列表
    """
    ips = []
    res = dns.resolver.Resolver()
    # res.nameservers = ['8.8.8.8', '8.8.4.4', '114.114.114.114', '223.5.5.5', '223.6.6.6']
    res.nameservers = ['1.2.4.8','223.5.5.5']

    try:
        domain_ip = res.query('www.'+domain, 'A')
        for i in domain_ip:
            ips.append(i.address)
    except:
        ips = []
    return ips


def create_queue():
    """创建队列"""
    domains = get_domain_from_db()  # 得到要查询的列表
    for d in domains:
        queue.put(d[0])


def get_svr_ip():
    """
    获取服务器的IP地址，并与已有ip比对,最后更新数据库
    """
    global domains_ip
    while 1:
        domain = queue.get()
        ips = domain2ip(domain)
        print domain,ips
        lock.acquire()
        domains_ip.append((domain, ips))
        if len(domains_ip) == 500:
            update_data()
            domains_ip = []
        lock.release()  # 解锁
        queue.task_done()
        time.sleep(1)  # 去掉偶尔会出现错误


def update_data():
    """
    更新数据库
    """
    db = MySQL(SOURCE_CONFIG)
    sql = 'UPDATE domain_info SET a_record="%s" WHERE domain="%s"'
    for i,j in domains_ip:
        db.update_no_commit(sql % (';'.join(sorted(j)), i))   # 只更新不提交
    db.commit()
    db.close()


def main():
    print str(datetime.now()), '开始解析域名的IP地址'
    global domains_ip
    domains_ip = []
    create_queue()
    for q in range(num_thread):  # 开始任务
        worker = Thread(target=get_svr_ip)
        worker.setDaemon(True)
        worker.start()
    queue.join()
    update_data()
    print str(datetime.now()), '结束解析whois服务器域名'


if __name__ == '__main__':
    main()