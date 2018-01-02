# encoding:utf-8

from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG


def total_china_domains():
    """
    统计中国域名的总数量
    """
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT count(*) FROM domain_info WHERE reg_country="cn" OR reg_country = "china"')
    results = db.fetch_all_rows()
    print '中国的域名数量为：',results[0][0]
    db.close()
    return results[0][0]


def tld_china():
    """
    中国域名各个顶级域名的分布情况，不包括cn
    """
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT tld, count(*) AS c FROM domain_info WHERE reg_country="cn" OR reg_country = "china" GROUP BY tld ORDER BY c DESC ')
    results = db.fetch_all_rows()
    print '中国的域名数量为：', results
    db.close()
    return results


def province_china():
    """
    各个省份的域名数量分布情况
    """
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT province,count(*) AS c FROM domain_info WHERE reg_country="cn" OR reg_country = "china" GROUP BY province ORDER BY c DESC ')
    results = db.fetch_all_rows()
    print '中国的域名数量为：', results
    db.close()
    return results


def city_china():
    """"""
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT domain,reg_province,reg_city,province,city FROM domain_info WHERE (reg_country="cn" OR reg_country = "china") AND (reg_city IS NOT NULL AND city ="") limit 100')
    results = db.fetch_all_rows()
    # print '中国的域名数量为：', results
    for i in results:
        print i
    db.close()
    return results


def unconfirmed_province():
    """
    统计可解析和不可解析的省份所占的百分比
    """
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT domain,reg_province,reg_city FROM domain_info WHERE (reg_country="cn" OR reg_country = "china") AND reg_province ="" OR (reg_province IS NOT NULL AND province="") ')
    results = db.fetch_all_rows()
    print len(results)
    for i in results:
        print i
    db.close()
    return results



# total_china_domains()
# tld_china()

# province_china()
# city_china()
unconfirmed_province()