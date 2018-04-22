# encoding:utf-8

from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
from collections import Counter


def get_domains(sql_china,sql_type):
    """
    根据输入的sql条件，从数据库中获取对应类型的域名
    :param sql_china:
    :param sql_type:
    :return:
    """

    full_sql = 'SELECT domain FROM domain_info WHERE %s %s' % (sql_china, sql_type)
    domains = []
    db = MySQL(SOURCE_CONFIG)
    db.query(full_sql)
    results = db.fetch_all_rows()
    for d in results:
        domains.append(d[0])
    db.close()

    return domains


def no_missing_data():
    """
    不缺失省份和城市数据的域名类型
    """
    sql_china = '(reg_country="cn" OR reg_country="china" OR reg_country="hk" OR reg_country ="hong kong")'
    sql_both_province_city = 'AND (province!="" AND city!="")'  # 省份与城市都有数据，且解析都正确的域名
    sql_province_not_city = 'AND (province!="" AND reg_city !="" AND city="")'  # 省份与城市都有数据，省份可以正确解析，但是城市无法解析
    sql_both_not_province_city = 'AND (reg_province !="" AND province = "" AND reg_city != "")'  # 省份与城市都有数据，省份无法解析

    both_province_city = get_domains(sql_china, sql_both_province_city)
    print len(both_province_city)
    province_not_city = get_domains(sql_china, sql_province_not_city)
    print len(province_not_city)
    both_not_province_city = get_domains(sql_china, sql_both_not_province_city)
    print len(both_not_province_city)

    return both_province_city, province_not_city, both_not_province_city




def diff_domain_type():
    """
    不同类型的域名
    """

    sql_china = '(reg_country="cn" OR reg_country="china" OR reg_country="hk" OR reg_country ="hong kong")'
    # 省份与城市都有数据类型
    sql_confirmed_province_city = 'AND (province!="" AND city!="")'  # 省份与城市都有数据，且解析都正确的域名
    sql_confirmed_province_not_city = 'AND (province!="" AND reg_city !="" AND city="")'  # 省份与城市都有数据，省份可以正确解析，但是城市无法解析
    sql_unconfirmed_province_city = 'AND (reg_province !="" AND province = "" AND reg_city != "")'  # 省份与城市都有数据，省份无法解析

    # 省份无数据，城市有数据类型
    sql_no_province_not_city = 'AND (reg_province = "" AND reg_city !="" )'  # 省份无数据，城市有数据

    # 省份有数据，城市无数据类型
    sql_confirmed_province_no_city = 'AND (reg_province !="" AND reg_city = "" AND province !="" )'  # 省份有数据，城市无数据，省份可以正确解析
    sql_unconfirmed_province_no_city = 'AND (reg_province !="" AND reg_city = "" AND province ="" )'  # 省份有数据，城市无数据，省份不可以正确解析

    # 省份与城市皆无数据
    sql_no_province_city = 'AND (reg_province = "" AND reg_city = "")'



    no_province_not_city = get_domains(sql_china,sql_no_province_not_city)
    print len(no_province_not_city)

    confirmed_province_no_city = get_domains(sql_china,sql_confirmed_province_no_city)
    print len(confirmed_province_no_city)

    unconfirmed_province_no_city = get_domains(sql_china,sql_unconfirmed_province_no_city)
    print len(unconfirmed_province_no_city)

    no_province_city = get_domains(sql_china,sql_no_province_city)
    print len(no_province_city)


    # return confirmed_province_city_domains,confirmed_province_not_city,unconfirmed_province_city,no_province_not_city,confirmed_province_no_city,unconfirmed_province_no_city,no_province_city

def get_registrar(domains):

    registrar_counter = Counter()
    db = MySQL(SOURCE_CONFIG)

    for d in domains:
        sql = 'SELECT registrar_name FROM domain_info WHERE domain ="%s" ' % d
        db.query(sql)
        registrar = db.fetch_all_rows()
        registrar_counter[registrar[0][0]] += 1

    db.close()

    print registrar_counter

if __name__ == '__main__':
    # diff_domain_type()

    both_province_city, province_not_city, both_not_province_city = no_missing_data()
    get_registrar(both_not_province_city)
    get_registrar(province_not_city)
    get_registrar(both_not_province_city)


