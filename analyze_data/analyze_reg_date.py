# encoding:utf-8

from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
from collections import Counter
from general_date import extract_date

def get_reg_date(sql_type):
    """
    根据输入的sql条件，从数据库中获取对应类型的域名注册时间
    :param sql_type: string 查询条件
    :return
        resutls: list 符合条件的域名注册时间
    """
    sql_china = '(reg_country="cn" OR reg_country="china" OR reg_country="hk" OR reg_country ="hong kong")'
    full_sql = 'SELECT reg_date FROM domain_info WHERE %s %s' % (sql_china, sql_type)
    db = MySQL(SOURCE_CONFIG)
    db.query(full_sql)
    results = db.fetch_all_rows()
    db.close()
    return results


def manage_data(results,percent=True):
    """
    根据输入的注册时间得到各个年份分布的域名数量，结果分为数据和百分比
    :param results: list 原始数据
    :param percent: bool 结果是否为百分比
    :return:
        reg_date_counter: Counter 注册时间和对应的域名数量
    """
    reg_date_counter = Counter()
    total_domains = len(results)  # 总共的域名数量
    for r in results:
        reg_year = extract_date(r[0])  # 年份
        reg_date_counter[reg_year] += 1
    if percent:  # 结果为百分比
        for i in reg_date_counter:
            reg_date_counter[i] = reg_date_counter[i]/float(total_domains)

    return reg_date_counter


def no_missing_data():
    """
    不缺失省份和城市数据的域名类型
    """
    sql_both_province_city = 'AND (province!="" AND city!="")'  # 省份与城市都有数据，且解析都正确的域名
    sql_province_not_city = 'AND (province!="" AND reg_city !="" AND city="")'  # 省份与城市都有数据，省份可以正确解析，但是城市无法解析
    sql_both_not_province_city = 'AND (reg_province !="" AND province = "" AND reg_city != "")'  # 省份与城市都有数据，省份无法解析

    both_province_city = get_reg_date(sql_both_province_city)
    province_not_city = get_reg_date(sql_province_not_city)
    both_not_province_city = get_reg_date(sql_both_not_province_city)

    return both_province_city, province_not_city, both_not_province_city


def missing_province():
    """
    缺失省份
    """
    sql_no_province_not_city = 'AND (reg_province = "" AND reg_city !="" )'  # 省份无数据，城市有数据
    no_province = get_reg_date(sql_no_province_not_city)
    return no_province


def missing_city():
    # 省份有数据，城市无数据类型
    sql_confirmed_province_no_city = 'AND (reg_province !="" AND reg_city = "" AND province !="" )'  # 省份有数据，城市无数据，省份可以正确解析
    sql_unconfirmed_province_no_city = 'AND (reg_province !="" AND reg_city = "" AND province ="" )'  # 省份有数据，城市无数据，省份不可以正确解析

    province = get_reg_date(sql_confirmed_province_no_city)
    un_province = get_reg_date(sql_unconfirmed_province_no_city)

    return province, un_province


def missing_province_city():
    """
    省份城市都缺失
    """
    sql_no_province_city = 'AND (reg_province = "" AND reg_city = "")'
    no_province_city = get_reg_date(sql_no_province_city)
    return no_province_city


if __name__ == '__main__':
    # province_city = no_missing_data()
    missing_province_data = missing_province()
    missing_province_counter = manage_data(missing_province_data)
    for i,j in sorted(missing_province_counter.items(),reverse=True):
        print str(i)+'\t'+str(j)

    # print sorted(data2.items(), reverse=True)
    # missing_city()
    print "--------------------------------"
    missing_province_city_data = missing_province_city()
    missing_province_city_counter = manage_data(missing_province_city_data)
    for i,j in sorted(missing_province_city_counter.items(), reverse=True):
        print str(i) + '\t' + str(j)


