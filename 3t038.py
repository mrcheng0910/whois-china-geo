# /user/bin/python
# encoding:utf-8

"""
用来获取whois域名的IP地址
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from get_whois_new.data_base import MySQL
from get_whois_new.config1 import SOURCE_CONFIG,DESTINATION_CONFIG



def get_domain_from_db():
    """
    从数据库中获取已有whois服务器地址和已有的IP地址
    :return:
    """
    db = MySQL(SOURCE_CONFIG)
    sql = 'SELECT * FROM domain_locate_was'
    db.query(sql)
    domains = db.fetch_all_rows()
    # print domains
    db.close()
    return domains


def insert_db():
    domains = get_domain_from_db()

    db = MySQL(DESTINATION_CONFIG)
    sql = 'insert into domain_whowas (domain,flag,insert_time,tld,domain_status,sponsoring_registrar, \
          top_whois_server,sec_whois_server,reg_name,reg_phone,reg_email,org_name,name_server,creation_date, \
          expiration_date,update_date,details) VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'
    for _,domain, flag, insert_time, tld, status, registrar, top, sec, reg_name, phone, email, org_name, ns, cd, ed, ud, detail,_ in domains:

        try:
            detail = detail.replace('\"', ' ')
            db.update(sql % (domain,flag,insert_time,tld,status,registrar,top,sec,reg_name,phone,email,org_name,ns,cd,ed,ud,detail))
        except:
            continue

    db.commit()
    db.close()

def insert_loc_db():
    domains = get_domain_from_db()

    db = MySQL(DESTINATION_CONFIG)
    sql = 'insert into domain_locate_was (domain,reg_whois_country,reg_whois_province,reg_whois_city,reg_whois_street, \
              reg_postal_country,reg_postal_province,reg_postal_city,reg_phone_country,reg_phone_province,reg_phone_city, \
              province,country_code,city,street,postal_code,reg_phone,cmp_res,insert_time,reg_postal_type, \
              reg_phone_type)  VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s") '

    for _, domain,reg_whois_country,reg_whois_province,reg_whois_city,reg_whois_street, \
              reg_postal_country,reg_postal_province,reg_postal_city,reg_phone_country,reg_phone_province,reg_phone_city, \
              province,country_code,city,street,postal_code,reg_phone,cmp_res,insert_time,reg_postal_type, \
              reg_phone_type,_, _ in domains:

        try:
            print domain
            db.update(sql % (
                domain, reg_whois_country, reg_whois_province, reg_whois_city, reg_whois_street, \
                reg_postal_country, reg_postal_province, reg_postal_city, reg_phone_country, reg_phone_province,
                reg_phone_city, province, country_code, city, street, postal_code, reg_phone, cmp_res, insert_time, reg_postal_type, \
                reg_phone_type))
        except:
            continue

    db.commit()
    db.close()



def main():
   # update_data()
   # insert_db()
   insert_loc_db()


if __name__ == '__main__':
    main()