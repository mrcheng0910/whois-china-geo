#!/usr/bin/env python
# encoding:utf-8

"""
获取域名whois数据和更新域名的地理位置信息（whois地理、电话、邮编）
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')


from Setting.global_resource import *  # 全局资源
from Setting.static import Static  # 静态变量,设置

from whois_code.match_province_city import verify_province_city

import time
import threading
from threading import Thread
from Queue import Queue
from datetime import datetime

num_thread = 10      # 线程数量
queue = Queue()     # 任务队列，存储sql
lock = threading.Lock()  # 变量锁

from data_base import MySQL
from config import SOURCE_CONFIG

from phone2geo.phone_locate import get_phone_locate
from postal2geo.analysis_postal2 import get_postal_locate

Static.init()
Resource.global_object_init()
log_get_whois = Static.LOGGER


def update_domain_whois_locate(db, domain, country_code, province, city, postal_code, reg_phone):
    """
    更新数据库中域名的WHOIS信息和locate信息
    :param db: 数据库
    """

    reg_whois_country, reg_whois_province, reg_whois_city = format_whois_geo(country_code, province, city)
    reg_phone_country, reg_phone_province, reg_phone_city,reg_phone_type = format_phone_geo(reg_phone)
    reg_postal_country, reg_postal_province, reg_postal_city,reg_postal_type = format_postal_geo(postal_code)

    cmp_flag = cmp_geo(reg_whois_province,reg_phone_province,reg_postal_province)

    sql_locate = (
        'UPDATE domain_locate set reg_whois_country="%s",reg_whois_province="%s",reg_whois_city="%s",reg_postal_country="%s",'
        'reg_postal_province="%s",reg_postal_city="%s",reg_phone_country="%s",reg_phone_province="%s",'
        'reg_phone_city="%s",cmp_res="%s",reg_phone_type="%s",reg_postal_type="%s"'
        'WHERE domain="%s" '

    )
    db.update(sql_locate % (reg_whois_country,reg_whois_province, reg_whois_city, \
                     reg_postal_country,reg_postal_province,reg_postal_city,reg_phone_country,reg_phone_province, \
                     reg_phone_city, cmp_flag, reg_phone_type, reg_postal_type,domain))


def cmp_geo(reg_whois_province,reg_phone_province,reg_postal_province):
    """
    比较WHOIS地理的一致性,得到结果
    :param reg_whois_province:
    :param reg_phone_province:
    :param reg_postal_province:
    """
    provinces = []
    null_count = 0
    if reg_whois_province:
        provinces.append(str(reg_whois_province.strip()))
    else:
        null_count += 1
    if reg_phone_province:
        provinces.append(str(reg_phone_province.strip()))
    else:
        null_count += 1
    if reg_postal_province:
        provinces.append(str(reg_postal_province.strip()))
    else:
        null_count += 1

    if null_count == 3:
        return 1  # 完全不同，都是无法解析的

    provinces_len = len(provinces)
    provinces_set_len = len(set(provinces))

    flag = provinces_len - provinces_set_len + 1

    return flag


def format_whois_geo(country_code, province, city):
    reg_whois_country = reg_whois_province = reg_whois_city = ""
    # 更新whois地理信息到基础库中
    # print country_code
    if not country_code:
        return reg_whois_country, reg_whois_province, reg_whois_city
    if country_code.lower() == 'cn' or country_code.lower() == 'china':
        result = verify_province_city(province, city)
        reg_whois_country = '中国'
        if result:
            reg_whois_province, reg_whois_city = result['confirmed_province'], result['confirmed_city']
    else:
        reg_whois_country, reg_whois_province, reg_whois_city = country_code, province, city

    return reg_whois_country, reg_whois_province, reg_whois_city


def format_phone_geo(phone):
    """
    转移电话的地理信息
    :param phone: 电话
    :return:
        reg_phone_country: 国家
        reg_phone_province: 省份
        reg_phone_city: 城市
    """
    phone_locate = get_phone_locate(phone)
    reg_phone_country = reg_phone_province = reg_phone_city = ""
    reg_phone_type = 0

    if phone_locate['province']:  # 存在省份
        reg_phone_country = '中国'
        reg_phone_province = phone_locate['province']
        reg_phone_city = phone_locate['city']
        reg_phone_type = phone_locate['type']

    return reg_phone_country, reg_phone_province, reg_phone_city,reg_phone_type


def format_postal_geo(postal):
    """
    转译邮编的地理信息
    :param postal: 邮编
    :return:
        reg_postal_country：注册国家
        reg_postal_province: 注册省份
        reg_postal_city: 注册城市
    """
    if not postal:
        return "", "", "", 4
    postal_locate,reg_postal_type = get_postal_locate(postal)  # 得到邮编的中国地理位置
    reg_postal_country = reg_postal_province = reg_postal_city = ""

    if postal_locate[0]:  # 不为None
        reg_postal_country = postal_locate[0]
        reg_postal_province = postal_locate[1]
        reg_postal_city = postal_locate[2]

    return reg_postal_country, reg_postal_province, reg_postal_city, reg_postal_type


def update_domain_info(domain, country_code, province, city, postal_code, reg_phone):
    """
    依据更新规则，更新信息到数据库表中
    """
    db = MySQL(SOURCE_CONFIG)
    update_domain_whois_locate(db, domain, country_code, province, city, postal_code, reg_phone)
    db.close()


def update_domain_whois():
    """
    更新域名的WHOIS信息
    """
    while 1:

        domain, country_code, province, city, postal_code, reg_phone = queue.get()  # 从队列中读出域名信息
        print domain
        print queue.qsize()   # 剩余的域名数量

        try:
            update_domain_info(domain, country_code, province, city, postal_code, reg_phone)
        except BaseException, e:
            # print domain,'数据库异常'
            # queue.task_done()  # 任务完成
            print e
            pass
        # lock.release()  # 解锁
        queue.task_done()
        time.sleep(1)  # 去掉偶尔会出现错误




def fetch_resource_data():
    """
    获得待查询whois信息的域名，包括域名名称、更新时间、到期时间和详细信息,顶级域名

    注意：
    domain_whois表中的域名是由domain_index中根据触发器更新的
    """
    db = MySQL(SOURCE_CONFIG)
    sql = 'SELECT domain, country_code,province,city,postal_code,reg_phone FROM domain_locate  WHERE  reg_whois_country IS NULL LIMIT 1,240535'
    db.query(sql)
    query_domains = db.fetch_all_rows()  # 得到总共的数量
    db.close()
    return query_domains


def create_queue():
    """
    创建任务队列
    """
    query_domains = fetch_resource_data()
    for d in query_domains:
        queue.put(d)  # num 加入队列


def create_thread():
    """创建任务线程"""
    for q in range(num_thread):  # 开始任务
        worker = Thread(target=update_domain_whois)
        worker.setDaemon(True)
        worker.start()
    queue.join()


def domain_whois():
    """主操作"""
    print str(datetime.now()), '开始获取域名的WHOIS信息'
    create_queue()
    create_thread()
    print str(datetime.now()), '结束获取域名的WHOIS信息'


if __name__ == '__main__':
    domain_whois()