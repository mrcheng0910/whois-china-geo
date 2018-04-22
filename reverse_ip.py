# encoding:utf-8

"""
用来获取whois域名的IP地址
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
domains_ip = []
from ip2location import ip2region


def resolve_domain_record(domain):
    """
    获取解析到的域名ip和cname列表
    """
    cnames = []
    ips = []
    req_obj = DNS.Request()
    try:
        answer_obj = req_obj.req(name=domain, qtype=DNS.Type.A, server="223.5.5.5")
        for i in answer_obj.answers:
            if i['typename'] == 'CNAME':
                cnames.append(i['data'])
            elif i['typename'] == 'A':
                ips.append(i['data'])
    except DNS.Base.DNSError:
        cnames = []
        ips = []

    return ips, cnames


def get_domain_from_db():
    """
    从数据库中获取已有whois服务器地址和已有的IP地址
    :return:
    """
    db = MySQL(SOURCE_CONFIG)
    sql = 'SELECT domain  FROM domain_ip_mx WHERE ip IS NULL'
    db.query(sql)
    domains = db.fetch_all_rows()
    db.close()
    return domains


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
        print queue.qsize()
        domain = queue.get()
        ips,cnames = resolve_domain_record(domain)
        ip_geo = get_ip_geo(ips)
        print domain,ips,cnames,ip_geo
        lock.acquire()
        domains_ip.append((domain, ips,cnames,ip_geo))
        if len(domains_ip) == 200:
            update_data()
            domains_ip = []
        lock.release()  # 解锁
        queue.task_done()

        time.sleep(1)  # 去掉偶尔会出现错误


def get_ip_geo(ips):

    countries = []
    provinces = []
    cities = []
    opers = []

    for ip in ips:
        geo = ip2region(ip)
        countries.append(geo['country'])
        provinces.append(geo['region'])
        cities.append(geo['city'])
        opers.append(geo['oper'])

    ip_geo = {
        "countries": ';'.join(countries),
        "provinces": ';'.join(provinces),
        "cities": ';'.join(cities),
        "opers": ';'.join(opers)
    }
    return ip_geo


def update_data():
    """
    更新数据库
    """
    db = MySQL(SOURCE_CONFIG)
    sql = 'UPDATE domain_ip_mx SET ip="%s",cname="%s",country="%s",province="%s",city="%s",oper="%s" WHERE domain="%s" '

    for domain,ip,cname,geo in domains_ip:
        try:
            db.update_no_commit(sql % (';'.join(sorted(ip)),';'.join(cname),geo['countries'],geo['provinces'], geo['cities'], geo['opers'], domain))   # 只更新不提交
        except BaseException,e:
            print "更新数据库异常:",e
            continue
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
    print str(datetime.now()), '开始解析域名的IP地址'


if __name__ == '__main__':
    main()