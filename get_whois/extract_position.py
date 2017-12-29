# encoding:utf-8
"""
将四个反查源反查出的域名whois信息汇总在一起，并提取出detail中的reg_phone,reg_postal,reg_pos
"""

import sys
import re
# import MySQLdb as mdb
from data_base import MySQL
from config import SOURCE_CONFIG
reload(sys)
sys.setdefaultencoding('utf8')

def deal_ZD(src1,src2,details):
    """
    处理字段值
    :param src1: 
    :param src2: 
    :param details: 
    :return: 处理后字段值
    """
    try:
        res = re.search(src1, details).group().strip()
    except:
        try:
            res = re.search(src2, details).group().strip()
        except:
            res = None

    return res

def extract_geo(domain, details):
        """
        从details中提取注册国家省份城市邮编
        :param domain: 
        :param details: 
        :return: 
        """
        reg_country = reg_province = reg_city = reg_postal = None
        # 正则匹配语法
        c_reg_country = r'(?<=Registrant Country\:).*(?=\n)'
        c_reg_province = r'(?<=Registrant State/Province\:).*(?=\n)'
        c_reg_city = r'(?<=Registrant City\:).*(?=\n)'
        c_reg_postal = r'(?<=Registrant Postal Code\:).*(?=\n)'
        c_country = r'(?<=Country\:).*(?=\n)'
        c_province = r'(?<=State:).*(?=\n)'
        c_city = r'(?<=City\:).*(?=\n)'
        c_postal = r'(?<=Postal Code\:).*(?=\n)'
        if details is not None:
            # reg_province处理
            reg_province = deal_ZD(c_reg_province, c_province,details)
            # reg_city处理
            reg_city = deal_ZD(c_reg_city,c_city,details)
            # reg_postal处理
            reg_postal = deal_ZD(c_reg_postal,c_postal, details)
            #reg_country 处理
            reg_country = deal_ZD(c_reg_country, c_country, details)
        #
        # reg_province = mdb.escape_string(reg_province) if reg_province is not None else(reg_province)
        # reg_city = mdb.escape_string(reg_city) if reg_city is not None else(reg_city)
        # reg_postal = mdb.escape_string(reg_postal) if reg_postal is not None else(reg_postal)
        # reg_country = mdb.escape_string(reg_country) if reg_country is not None else(reg_country)

        print reg_country
        print reg_postal
        print reg_city
        print reg_province
        # return domain,details,reg_country,reg_province,reg_city,reg_postal
        if reg_country:
            update_db(reg_country,reg_postal,reg_city,reg_province,domain)

def update_db(reg_country,reg_postal,reg_city,reg_province,domain):
    db = MySQL(SOURCE_CONFIG)
    sql = 'UPDATE domain_info SET reg_country="%s",reg_postal = "%s",reg_city="%s",reg_province="%s" WHERE domain = "%s"'  % (reg_country,reg_postal,reg_city,reg_province,domain)
    db.update(sql)
    db.close()


def fetch_resource_data():
    """获得源数据
    :param tb_name: string 表名
    :return: results: 查询结果
    """
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT domain,details FROM domain_info')
    results = db.fetch_all_rows()
    db.close()
    return results

def manage_dw(dw):

    for domain, detail in dw:
        print domain
        # print domain,detail
        extract_geo(domain, detail)



if __name__ == '__main__':

    dw = fetch_resource_data()
    manage_dw(dw)
