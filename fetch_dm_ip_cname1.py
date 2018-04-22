# encoding:utf-8

"""
1. 获取域名的IP地址以及地理位置，同时更新数据库，更新数据库规则如下：
    1）若数据库中无该域名记录，则插入；
    2）若数据库中有该域名记录，则与该域名最近一次的更新记录进行比较，若相同则不更新，不同则更新。
2. 获取域名的CNAME，同时更新数据库，规则与上相同

程亚楠
创建：2017.9.8
"""

import schedule
import time
import DNS


def resolve_domain_record(domain):
    """
    获取解析到的域名ip和cname列表
    """
    cnames = []
    ips = []
    req_obj = DNS.Request()
    try:
        answer_obj = req_obj.req(name=domain, qtype=DNS.Type.MX, server="223.5.5.5")
        for i in answer_obj.answers:
            print i
            if i['typename'] == 'CNAME':
                cnames.append(i['data'])
            elif i['typename'] == 'A':
                ips.append(i['data'])
    except DNS.Base.DNSError:
        cnames = []
        ips =[]

    return ips, cnames


if __name__ == '__main__':
    # main()
    # schedule.every(2).hours.do(main)  # 12小时循环探测一遍
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    print resolve_domain_record('baidu.com')