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
    获取中国域名使用NS服务器的数据
    """
    db = MySQL(SOURCE_CONFIG)

    sql = 'select lower(ns) from domain_info WHERE (reg_country = "cn" OR reg_country = "china" OR reg_country="hk" OR \
            reg_country="hong kong") AND ns != "" '
    db.query(sql)
    results = db.fetch_all_rows()
    db.close()
    return results


def analyze_ns(results):
    """
    分析域名使用ns服务器的情况
    :param results: 待分析数据
    """
    total_domains = len(results)
    ns_counter = Counter()
    for ns in results:
        ns_list = sorted(ns[0].split(';'))  # 注意排序，因为多个ns服务器，名称相同，但顺序可能不一致
        ns = ';'.join(ns_list)   # 组成字符串形式，以;分割
        ns_counter[ns] += 1

    ns_domain = defaultdict(set)  # ns服务器的主域名对应的次级域名列表
    ns_domain_count = Counter()    # ns服务器的主域名对应的域名数量

    for i, j in ns_counter.most_common():
        domain_list = []
        for d in i.split(';'):
            domain = tldextract.extract(d).domain + '.'+tldextract.extract(d).suffix
            domain_list.append(domain)

        if len(set(domain_list)) == 1:
            ns_domain[domain_list[0]].add(i)
            ns_domain_count[domain_list[0]] += j
        else:
            # print i
            ns_domain[';'.join(list(set(domain_list)))].add(i)
            ns_domain_count[';'.join(list(set(domain_list)))] += j

    top_ns = []
    top_ns_domain_count = 0
    for i, j in ns_domain_count.most_common(15):
        print i, j
        top_ns.append(i)
        top_ns_domain_count += j

    for i in top_ns:
        tmp_ns = []
        print i
        for j in ns_domain[i]:
            tmp_ns.extend(j.split(';'))
        for m in  set(tmp_ns):
            print m

    # for i in ns_domain:
    #     print i,ns_domain[i]
    # print ns_domain['dnspod.com']
    print top_ns_domain_count
    print total_domains


if __name__ == '__main__':
    results = get_ns()
    analyze_ns(results)