#!/usr/bin/python
# encoding:utf-8
"""
多线程获取域名的MX记录
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from get_whois_new.data_base import MySQL
import time
import threading
from Queue import Queue
from threading import Thread
from datetime import datetime
import DNS
from get_whois_new.config import SOURCE_CONFIG

num_thread = 20  # 线程数量
queue = Queue()  # 任务队列，存储sql
lock = threading.Lock()


def resolve_domain_record(domain):
    """
    获取域名的mx记录，若无则返回空
    """
    mxs = []
    req_obj = DNS.Request()

    try:
        answer_obj = req_obj.req(name=domain, qtype=DNS.Type.MX,server="223.5.5.5")
        for i in answer_obj.answers:
            if i['typename'] == 'MX':
                mxs.append(i['data'][1])
    except DNS.Base.DNSError:
        mxs = []

    return mxs


def create_queue():
    """创建任务队列，队列中为域名"""
    domains = get_domain_from_db()  # 得到要查询的列表
    for d in domains:
        queue.put(d[0])


def get_domain_mx():
    """
    获取域名mx记录，并更新数据库
    """
    global domains_mx   # 全局变量，批量更新数据库
    while 1:
        print queue.qsize()
        domain = queue.get()
        mxs = resolve_domain_record(domain)
        lock.acquire()  # 上锁
        domains_mx.append((domain, mxs))
        if len(domains_mx) == 200:   # 当获取500个域名的记录后，更新数据库
            update_data()
            domains_mx = []
        lock.release()  # 解锁

        queue.task_done()
        time.sleep(1)  # 去掉偶尔会出现错误



def update_data():
    """
    更新数据库
    """
    db = MySQL(SOURCE_CONFIG)
    sql = 'UPDATE domain_ip_mx SET mx="%s" WHERE domain="%s"'

    for i, j in domains_mx:
        print i, j
        try:
            db.update_no_commit(sql % (';'.join(sorted(j)),i))  # 只更新不提交
        except BaseException, e :
            print "出错！！！", e
            continue
    db.commit()
    db.close()


def get_domain_from_db():
    """
    从数据库中得到待获取mx记录的域名集合
    """
    db = MySQL(SOURCE_CONFIG)
    # sql = 'SELECT domain  FROM domain_ip_mx WHERE mx IS NULL '
    sql = 'SELECT domain  FROM domain_ip_mx WHERE mx = "" '
    db.query(sql)
    domains = db.fetch_all_rows()
    db.close()
    return domains


def main():
    """主函数"""
    print str(datetime.now()), '开始解析域名的mx'
    global domains_mx
    domains_mx = []
    create_queue()
    for q in range(num_thread):  # 开始任务
        worker = Thread(target=get_domain_mx)
        worker.setDaemon(True)
        worker.start()
    queue.join()
    update_data()  # 注意添加该操作，否则会丢失部分数据
    print str(datetime.now()), '结束解析域名的mx'


if __name__ == '__main__':
    main()
