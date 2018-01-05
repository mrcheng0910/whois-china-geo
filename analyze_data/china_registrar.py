# encoding:utf-8

from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
from collections import Counter


def get_registrars(sql_type):
    """
    根据输入的sql条件，从数据库中获取对应类型的域名
    :param sql_type: 查询条件
    :return: registrar_counter ，注册商计数
    """
    registrar_counter = Counter()
    sql_china = '(reg_country="cn" OR reg_country="china" OR reg_country="hk" OR reg_country ="hong kong")'
    full_sql = 'SELECT registrar_name,COUNT(*) FROM domain_info WHERE %s %s GROUP BY registrar_name' % (sql_china, sql_type)
    db = MySQL(SOURCE_CONFIG)
    db.query(full_sql)
    results = db.fetch_all_rows()
    for r, c in results:
        registrar_counter[r] = c

    db.close()
    print registrar_counter
    return registrar_counter


def no_missing_data():
    """
    不缺失省份和城市数据的域名类型
    """
    sql_both_province_city = 'AND (province!="" AND city!="")'  # 省份与城市都有数据，且解析都正确的域名
    sql_province_not_city = 'AND (province!="" AND reg_city !="" AND city="")'  # 省份与城市都有数据，省份可以正确解析，但是城市无法解析
    sql_both_not_province_city = 'AND (reg_province !="" AND province = "" AND reg_city != "")'  # 省份与城市都有数据，省份无法解析

    both_province_city = get_registrars(sql_both_province_city)
    province_not_city = get_registrars(sql_province_not_city)
    both_not_province_city = get_registrars(sql_both_not_province_city)

    return both_province_city, province_not_city, both_not_province_city


def missing_province():
    """
    缺失省份
    """
    sql_no_province_not_city = 'AND (reg_province = "" AND reg_city !="" )'  # 省份无数据，城市有数据
    no_province = get_registrars(sql_no_province_not_city)
    return no_province


def missing_city():
    # 省份有数据，城市无数据类型
    sql_confirmed_province_no_city = 'AND (reg_province !="" AND reg_city = "" AND province !="" )'  # 省份有数据，城市无数据，省份可以正确解析
    sql_unconfirmed_province_no_city = 'AND (reg_province !="" AND reg_city = "" AND province ="" )'  # 省份有数据，城市无数据，省份不可以正确解析

    province = get_registrars(sql_confirmed_province_no_city)
    un_province = get_registrars(sql_unconfirmed_province_no_city)

    return province, un_province


def missing_province_city():
    """
    省份城市都缺失
    """
    sql_no_province_city = 'AND (reg_province = "" AND reg_city = "")'
    no_province_city = get_registrars(sql_no_province_city)
    return no_province_city


if __name__ == '__main__':
    # no_missing_data()
    # missing_province()
    # missing_city()
    missing_province_city()


