# encoding:utf-8

from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
from collections import Counter
from sql import china_sql
from collections import defaultdict


def email_type(percent_flag = False,top=50):
    """
    获取注册中国域名的邮箱类型分布情况
    """
    total_domains = 0  # 域名总数
    db = MySQL(SOURCE_CONFIG)

    sql = 'SELECT SUBSTRING_INDEX(reg_email,"@",-1) as email, count(*) FROM `domain_info` WHERE reg_email != ""  \
          AND (%s) GROUP BY email' % china_sql

    db.query(sql)
    results = db.fetch_all_rows()
    email_counter = Counter()
    for email, count in results:
        email_counter[email] = count
        total_domains += count
    db.close()

    if percent_flag:
        for i, j in email_counter.most_common(top):
            print i + '\t'+ str(float(j)/total_domains)
    else:
        for i, j in email_counter.most_common(top):
            print i +'\t' + str(j)


def email_domains():
    """
        获取注册中国域名的邮箱类型分布情况
        """
    total_domains = 0
    db = MySQL(SOURCE_CONFIG)

    sql = 'SELECT reg_email, count(*) FROM `domain_info` WHERE reg_email != "" AND (reg_country = "cn" OR reg_country = "china" OR reg_country="hk" OR  reg_country="hong kong") GROUP BY reg_email '

    db.query(sql)
    results = db.fetch_all_rows()
    email_counter = Counter()
    for email, count in results:
        email_counter[email] = count
        total_domains += count

    db.close()
    for i, j in email_counter.most_common(50):
        print i + '\t' + str(j)

    print total_domains


def email_domains1():
    """
        获取注册中国域名的邮箱类型分布情况
    """
    total_domains = 0
    db = MySQL(SOURCE_CONFIG)

    sql = 'SELECT LOWER (reg_email), count(*) FROM `domain_info` WHERE reg_email != "" AND (%s) GROUP BY reg_email ' % china_sql  # 注意让所有邮箱为小写字母

    db.query(sql)
    results = db.fetch_all_rows()

    email_counter = Counter()   # email注册域名的统计
    email_type_count = Counter()  # 不同类型email注册域名的统计
    for email, count in results:
        try:
            # email类型统计
            email_type = email.split('@')[1]
            email_type_count[email_type] += count
            # email统计
            email_counter[email] = count
            total_domains += count
        except IndexError, e:
            # print e, email
            continue

    db.close()

    for i, j in email_type_count.most_common(40):
        print i, j
    print "--------------------------------------------------"
    for i, j in email_counter.most_common(50):
        print i + '\t' + str(j)

    print total_domains


if __name__ == '__main__':

    # email_type()
    email_domains1()