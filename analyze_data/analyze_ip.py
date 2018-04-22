# encoding:utf-8

from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
from collections import Counter


def email_china():
    """
    获取注册中国域名的邮箱类型分布情况
    """
    db = MySQL(SOURCE_CONFIG)

    sql = 'SELECT a_record FROM `domain_info` WHERE (a_record IS NOT NULL AND a_record != "") AND (reg_country="cn" OR reg_country="china" OR reg_country="hk" OR reg_country="hongkong")'
    db.query(sql)
    results = db.fetch_all_rows()
    ip_counter = Counter()
    for ip in results:
        ip = ';'.join(sorted(ip[0].split(';')))  # 注意排序，相同IP集合，排序可能不同
        ip_counter[ip] += 1
    db.close()

    for i, j in ip_counter.most_common(50):
        print i, j


if __name__ == '__main__':

    email_china()