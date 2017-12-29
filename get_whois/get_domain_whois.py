#!/usr/bin/env python
# encoding:utf-8

"""
    获取域名whois数据
=======================

version   :   1.0
author    :   @`13
time      :   2017.1.18
"""

from Setting.global_resource import *  # 全局资源
from Setting.static import Static  # 静态变量,设置
from WhoisConnect import whois_connect  # Whois通信
from WhoisData.info_deal import get_result  # Whois处理函数
from data_base import MySQL
from config import SOURCE_CONFIG

Static.init()
Resource.global_object_init()
log_get_whois = Static.LOGGER

def get_domain_whois(raw_domain=""):
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
    """获得源数据
    :param tb_name: string 表名
    :return: results: 查询结果
    """
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT domain FROM base_domain')
    results = db.fetch_all_rows()
    db.close()
    return results


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

    sql = 'INSERT INTO domain_info(org_name, update_date,domain,reg_phone,reg_email,exp_date,reg_name,top_srv,ns,reg_date,flag,status,details,registrar_name,tld,sec_srv) VALUES("%s", "%s","%s", "%s","%s", "%s","%s", "%s","%s", "%s","%s", "%s","%s", "%s","%s", "%s")'
    db.insert(sql % (org_name, update_date,domain,reg_phone,reg_email,exp_date,reg_name,top_srv,ns,reg_date,flag,status,details,registrar_name,tld,sec_srv))


    db.close()

if __name__ == '__main__':
    query_domains = fetch_resource_data()
    for d in query_domains:
        print d
        try:
            data = get_domain_whois(d[0])
            print data
            insert_db(data)
        except:
            print "异常"
            pass
    # for i in data:
    #     print i,data[i]
