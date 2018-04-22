# encoding:utf-8
"""
统计mx记录
"""
from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
from collections import Counter
from sql import china_sql


def domain_mx():
    """
    获取注册中国域名的邮箱类型分布情况
    """
    db = MySQL(SOURCE_CONFIG)

    sql = 'SELECT LOWER (mx_record) FROM `domain_info` WHERE (mx_record != "") AND (%s)' % china_sql
    db.query(sql)
    results = db.fetch_all_rows()
    db.close()
    mx_counter = Counter()
    for mx in results:
        mx = ';'.join(sorted(mx[0].split(';')))
        mx_counter[mx] += 1

    top_count = 0
    for i, j in mx_counter.most_common(25):
        print i, j
        top_count += j

    print '域名总数：', len(results)
    print 'mx总数', len(mx_counter)
    print 'top_count', top_count


if __name__ == '__main__':
    domain_mx()