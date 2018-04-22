# encoding:utf8

"""
"""

import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from whois_connect import GetWhoisInfo
from database import DataBase

PATH = 'Data/domain/'
DOMAIN_EXAMPLE = 'example.com'


def main(Table,domain,srv):
    """主流程"""
    DB = DataBase()
    DB.db_connect()
    DB.execute_no_return("USE cyn_test")
    T, D = TestWhoisSrv(domain, srv)
    if D is None:
        D = ''
    if len(D) > 5:
        # print D
        D = D.replace("\\", "")
        D = D.replace("'", "\\'")
        D = D.replace('"', '\\"')
    SQL = """INSERT INTO {table} SET `srv` = '{w}' ,`domain` = '{dn}' ,`long_time` = {t} ,`details` = '{d}',`size` = '{s}' """.format(
        table=Table+'baidu', w=srv, t=T, d=str(D), dn=domain,s=len(D))
    DB.execute_no_return(SQL)
    DB.db_commit()
    DB.db_close()



def TestWhoisSrv(domain, whois_srv):
    """
    测试whois服务器性能
    :param domain: 域名
    :param whois_srv: whois服务器地址 ip/whois
    :return: T - 获取此条记录的时间
             D - 获取的结果
    """
    start = time.time()
    try:
        D = GetWhoisInfo(domain, whois_srv).get()  # 获取
    except Exception as e:
        D = str(e)
    end = time.time()
    T = end - start
    print len(D)
    print T
    return T, D


if __name__ == '__main__':

    fp = open('srv_test.txt','r')
    srv = []
    for i in fp.readlines():
        srv.append(i.strip())
    fp.close()
    table_name = 'cyn_test.'

    for s in srv:
        print s
        main(table_name,'google.nl', s)