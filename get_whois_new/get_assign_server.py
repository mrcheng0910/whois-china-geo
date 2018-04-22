#!/usr/bin/env python
# encoding:utf-8

"""
"""
import random
from Setting.global_resource import *  # 全局资源
from Setting.static import Static  # 静态变量,设置
from WhoisConnect import whois_connect  # Whois通信
from WhoisConnect import whois_connect_by_socks as whois_connect  # Whois通信
from WhoisData.info_deal import get_result  # Whois处理函数
from whois_code.extract_whois_position import extract_geo
from whois_code.match_province_city import verify_province_city

from data_base import MySQL
from config import SOURCE_CONFIG

from phone2geo.phone_locate import get_phone_locate
from postal2geo.analysis_postal2 import get_postal_locate

Static.init()
Resource.global_object_init()
log_get_whois = Static.LOGGER


def get_domain_whois(raw_domain, whois_srv):
    """
    获取whois信息
    :param raw_domain: 输入域名
    :return: whois信息字典 / 获取失败返回None
    """
    # log_get_whois.info(raw_domain + ' - start')

    # 处理域名信息
    Domain = Resource.Domain(raw_domain)
    domain_punycode = Domain.get_punycode_domain()  # punycode编码域名
    try:
        tld = Domain.get_tld()  # 域名后缀
    except:
        log_get_whois.error(str(raw_domain) + '域名TLD提取出现错误')
        return None

    WhoisFunc = Resource.WhoisFunc.get_whois_func(whois_srv)  # 获取TLD对应的提取函数名称

    data_flag = 1  # whois通信标记
    raw_whois_data = whois_connect.GetWhoisInfo(domain_punycode, whois_srv).get()
    if raw_whois_data.startswith('Socket Error'):
        data_flag = -1
    if raw_whois_data == '':
        data_flag = -5  # 获取到空数据，flag = -5

    # 处理原始whois数据
    whois_dict = get_result(domain_punycode,
                            tld,
                            whois_srv,
                            WhoisFunc,
                            raw_whois_data,
                            data_flag)

    # WHOIS信息的地理位置
    whois_geo = {}
    reg_country, reg_province, reg_city, reg_postal, reg_street = extract_geo(whois_dict['details'])
    whois_geo['reg_country'] = reg_country
    whois_geo['reg_province'] = reg_province
    whois_geo['reg_city'] = reg_city
    whois_geo['reg_postal'] = reg_postal
    whois_geo['reg_street'] = reg_street
    print whois_dict['details']
    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    # print whois_geo
    return whois_dict, whois_geo


def update_domain_whois_locate(db, whois_dict, whois_geo):
    """
    更新数据库中域名的WHOIS信息和locate信息
    :param db: 数据库
    :param whois_dict: whois信息
    :param whois_geo: 地理信息
    """
    domain, reg_phone, reg_email = whois_dict['domain'], whois_dict['reg_phone'], whois_dict['reg_email']
    org_name = whois_dict['org_name']
    reg_name = whois_dict['reg_name']
    registrar_name = whois_dict['sponsoring_registrar']
    details = whois_dict['details']
    ns, flag = whois_dict['name_server'], whois_dict['flag']
    reg_date, exp_date, update_date = whois_dict['creation_date'], whois_dict['expiration_date'], whois_dict['updated_date']
    status, tld = whois_dict['domain_status'], whois_dict['tld'].encode('utf8')
    if not reg_email and not reg_phone:
        return False
    sql_whois = (
        'UPDATE domain_whois set org_name="%s", update_date="%s",reg_phone="%s",reg_email="%s", '
        'expiration_date="%s",reg_name="%s",name_server="%s",creation_date="%s",'
        'flag="%s",domain_status="%s",details="%s",sponsoring_registrar="%s",tld="%s"'
        'WHERE domain="%s" '
    )
    try:
        db.update(sql_whois % ( org_name, update_date, reg_phone, reg_email, exp_date, reg_name, ns, reg_date, \
                            flag, status, details, registrar_name, tld, domain )
              )
    except BaseException, e:
        print "更新域名WHOIS信息出错", e
        return False

    reg_country, reg_province, reg_city, reg_postal, reg_street, country, province, city = format_whois_geo(whois_geo)
    reg_phone_country, reg_phone_province, reg_phone_city,reg_phone_type = format_phone_geo(reg_phone)
    reg_postal_country, reg_postal_province, reg_postal_city,reg_postal_type = format_postal_geo(reg_postal)

    cmp_flag = cmp_geo(province,reg_phone_province,reg_postal_province)

    sql_locate = (
        'UPDATE domain_locate set province="%s", city="%s",country_code="%s",street="%s",postal_code="%s",'
        'reg_whois_country="%s",reg_whois_province="%s",reg_whois_city="%s",reg_postal_country="%s",'
        'reg_postal_province="%s",reg_postal_city="%s",reg_phone_country="%s",reg_phone_province="%s",'
        'reg_phone_city="%s",cmp_res="%s",reg_phone_type="%s",reg_postal_type="%s",reg_phone ="%s"'
        'WHERE domain="%s" '

    )
    try:
        db.update(sql_locate % (reg_province, reg_city, reg_country, reg_street, reg_postal, country, province, city, \
                     reg_postal_country,reg_postal_province,reg_postal_city,reg_phone_country,reg_phone_province, \
                     reg_phone_city, cmp_flag, reg_phone_type, reg_postal_type,reg_phone,domain))
    except BaseException, e:
        print "更新当前地理位置信息出错", e
        return False
    return True


def format_whois_geo(whois_geo):
    country = province = city = ""
    # 更新whois地理信息到基础库中
    reg_country = whois_geo['reg_country']
    reg_province = whois_geo['reg_province']
    reg_city = whois_geo['reg_city']
    reg_postal = whois_geo['reg_postal']
    reg_street = whois_geo['reg_street']

    if reg_country.lower() == 'cn' or reg_country.lower() == 'china':
        result = verify_province_city(reg_province, reg_city)
        country = '中国'
        if result:
            province, city = result['confirmed_province'], result['confirmed_city']
    else:
        country, province, city = reg_country, reg_province, reg_city

    return reg_country, reg_province, reg_city, reg_postal,reg_street,country,province,city


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
    postal_locate,reg_postal_type = get_postal_locate(postal)  # 得到邮编的中国地理位置
    reg_postal_country = reg_postal_province = reg_postal_city = ""

    if postal_locate[0]:  # 不为None
        reg_postal_country = postal_locate[0]
        reg_postal_province = postal_locate[1]
        reg_postal_city = postal_locate[2]

    return reg_postal_country, reg_postal_province, reg_postal_city,reg_postal_type


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


def fetch_resource_data():
    """
    获得待查询whois信息的域名，包括域名名称、更新时间、到期时间和详细信息,顶级域名

    注意：
    domain_whois表中的域名是由domain_index中根据触发器更新的
    """
    db = MySQL(SOURCE_CONFIG)
    sql = 'SELECT domain FROM `domain_whois` WHERE sec_whois_server ="whois.godaddy.com" AND reg_email = "" AND reg_phone = "" LIMIT 20000'
    db.query(sql)
    query_domains = db.fetch_all_rows()  # 得到总共的数量
    db.close()
    return query_domains


def main():
    srvs = []
    fp = open('srv.txt','r')
    for i in fp.readlines():
        srvs.append(i.strip())
    fp.close()

    domains = fetch_resource_data()
    db = MySQL(SOURCE_CONFIG)
    for i in domains:
        srv = random.choice(srvs)
        print i[0], srv
        try:
            whois_dict, whois_geo = get_domain_whois(i[0], srv)
        except BaseException, e:
            continue

        update_domain_whois_locate(db, whois_dict, whois_geo)
    db.close()

if __name__ == '__main__':
    while 1:
        main()