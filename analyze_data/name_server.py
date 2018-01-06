# encoding:utf-8
"""
分析中国注册域名使用NS服务器的情况
"""

from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
from collections import Counter
import tldextract
from collections import defaultdict

def get_ns():
    """
    获取注册中国域名的邮箱类型分布情况
    """
    db = MySQL(SOURCE_CONFIG)

    sql = 'select ns from domain_info WHERE (reg_country = "cn" OR reg_country = "china" OR reg_country="hk" OR \
            reg_country="hong kong") AND ns != "" '
    db.query(sql)
    results = db.fetch_all_rows()

    db.close()

    return results

def analyze_ns(results):

    total_domains = len(results)
    ns_counter = Counter()
    for ns in results:
        ns_list = sorted(ns[0].split(';'))
        ns = ';'.join(ns_list)
        ns_counter[ns] += 1



    ns_domain = defaultdict(list)
    ns_domain_count = Counter()
    for i, j in ns_counter.most_common():
        domain_list = []
        for d in i.split(';'):
            domain = tldextract.extract(d).domain + '.'+tldextract.extract(d).suffix
            domain_list.append(domain)

            if len(set(domain_list)) == 1:
                ns_domain[domain_list[0]].append(i)
                ns_domain_count[domain_list[0]] += j
            else:
                ns_domain[';'.join(list(set(domain_list)))].append(i)
                ns_domain_count[';'.join(list(set(domain_list)))] += j
        # print i, j

    for i, j in ns_domain_count.most_common(50):
        print i, j

    for i in ns_domain:
        print i,ns_domain[i]


    print total_domains


if __name__ == '__main__':
    results = get_ns()
    analyze_ns(results)