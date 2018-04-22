# encoding:utf-8

from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
from collections import Counter


def registrar_china():
    """
    注册国家为中国的域名所使用的注册商的分布情况
    """
    registrar_domains = {}
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT registrar_name,count(*) AS c FROM domain_info WHERE reg_country="cn" OR reg_country = "china" OR reg_country="hk" GROUP BY registrar_name ORDER BY c DESC ')
    results = db.fetch_all_rows()
    total_count = 0
    drop_count = 0
    for r, c in results:
        total_count += c
        if r.find('DropCatch.com') != -1:
            drop_count += c
            registrar_domains['DropCatch.com LLC'] = drop_count
            continue
        registrar_domains[r] = c

    db.close()

    print total_count
    rd = Counter(registrar_domains)
    for i, j in rd.most_common():
        print i+'\t'+str(j)

# registrar_china()


def tld_china():
    """
    注册国家为中国的域名，其顶级域名后缀的分布情况
    """
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT tld,count(*) AS c FROM domain_info WHERE reg_country="cn" OR reg_country = "china" OR reg_country="hk" GROUP BY tld ORDER BY c DESC ')
    results = db.fetch_all_rows()
    total_count = 0
    for r, c in results:
        total_count += c
        print r, c
    db.close()

    print total_count


# tld_china()


def sec_srv():
    """
    二级WHOIS服务器的情况
    """
    db = MySQL(SOURCE_CONFIG)
    db.query(
        'SELECT sec_srv,count(*) AS c FROM domain_info WHERE reg_country="cn" OR reg_country = "china" OR reg_country="hk" GROUP BY sec_srv ORDER BY c DESC ')
    results = db.fetch_all_rows()
    total_count = 0
    for r, c in results:
        total_count += c
        print r, c
    db.close()

    print total_count

# sec_srv()


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


def count_registrar(domains):

    registrar_counter = Counter()
    db = MySQL(SOURCE_CONFIG)
    for d in domains:
        sql = 'SELECT registrar_name,sec_srv FROM domain_info WHERE domain = "%s" ' % (d)
        db.query(sql)
        result = db.fetch_all_rows()
        registrar_counter[result[0][0]] += 1


    for i,j in registrar_counter.most_common():
        print i,': ',j
    # return


def unconfirmed_province():
    """
    统计可解析和不可解析的省份所占的百分比
    """
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT domain,reg_province,reg_city FROM domain_info WHERE (reg_country="cn" OR reg_country = "china") AND reg_province ="" OR (reg_province IS NOT NULL AND province="") ')
    results = db.fetch_all_rows()
    print len(results)
    # for i in results:
    #     print i
    db.close()
    return results



# total_china_domains()
# tld_china()

# province_china()
# city_china()
# results = unconfirmed_province()
# domains = []
# for i in results:
#     domains.append(i[0])
#
# count_registrar(domains[:])
