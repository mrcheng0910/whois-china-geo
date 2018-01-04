# encoding:utf-8

from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
from collections import Counter


def email_china():
    """
    获取注册中国域名的邮箱类型分布情况
    """
    total_domains = 0
    db = MySQL(SOURCE_CONFIG)

    sql = 'SELECT SUBSTRING_INDEX(reg_email,"@",-1) as email, count(*) AS c FROM `domain_info` WHERE reg_email != "" AND (reg_country = "cn" OR reg_country = "china" OR reg_country="hk" OR  reg_country="hong kong") GROUP BY email ORDER BY c DESC'
    db.query(sql)
    results = db.fetch_all_rows()
    email_counter = Counter()
    for email, count in results:
        email_counter[email] = count
        total_domains += count

    db.close()

    for i,j in email_counter.most_common(20):
        print i+'\t'+ str(float(j)/total_domains)



if __name__ == '__main__':

    email_china()