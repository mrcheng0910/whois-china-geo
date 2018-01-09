#!/usr/bin/python
# encoding:utf-8
"""
多线程获取域名的MX记录
"""
from get_whois.data_base import MySQL
import time
import threading
from Queue import Queue
from threading import Thread
from datetime import datetime
import DNS
from get_whois.config import SOURCE_CONFIG

num_thread = 30  # 线程数量
queue = Queue()  # 任务队列，存储sql
lock = threading.Lock()
# current_ip_port = []


def get_domain_from_db():
    """
    从数据库中获取已有whois服务器地址和已有的IP地址
    :return:
    """
    db1 = MySQL(SOURCE_CONFIG)
    # sql = 'SELECT domain  FROM domain_info WHERE mx_record IS NULL limit 100'
    sql = 'SELECT domain FROM `domain_info` WHERE ID BETWEEN 199656 AND 210000'
    db1.query(sql)
    domains = db1.fetch_all_rows()
    db1.close()
    return domains


def resolve_domain_record(domain):
    """
    获取解析到的域名ip和cname列表
    """
    mxs = []
    req_obj = DNS.Request()

    try:
        answer_obj = req_obj.req(name=domain, qtype=DNS.Type.MX,server="1.2.4.8")
        for i in answer_obj.answers:
            if i['typename'] == 'MX':
                mxs.append(i['data'][1])
    except DNS.Base.DNSError:
        mxs = []

    return mxs


def create_queue():
    """创建队列"""
    domains = get_domain_from_db()  # 得到要查询的列表
    for d in domains:
        queue.put(d[0])


def get_domain_mx():
    """
    获取服务器的IP地址，并与已有ip比对,最后更新数据库
    """
    global current_ip_port
    while 1:
        domain = queue.get()
        ips = resolve_domain_record(domain)
        print domain, ips
        lock.acquire()
        current_ip_port.append((domain, ips))
        if len(current_ip_port) == 500:
            update_data()
            current_ip_port = []
        lock.release()  # 解锁

        queue.task_done()
        time.sleep(1)  # 去掉偶尔会出现错误



def update_data():
    """
    更新数据库
    :param ip:
    :param port:
    :param srv:
    :return:
    """
    db = MySQL(SOURCE_CONFIG)

    sql = 'UPDATE domain_info SET mx_record="%s" WHERE domain="%s"'
    for i,j in current_ip_port:
        db.update_no_commit(sql % (';'.join(sorted(j)),i))
    db.commit()
    db.close()



def main():
    print str(datetime.now()), '开始解析域名的IP地址'
    global current_ip_port
    current_ip_port = []
    create_queue()
    for q in range(num_thread):  # 开始任务
        worker = Thread(target=get_domain_mx)
        worker.setDaemon(True)
        worker.start()
    queue.join()
    update_data()
    print str(datetime.now()), '结束解析whois服务器域名'


if __name__ == '__main__':
    main()
