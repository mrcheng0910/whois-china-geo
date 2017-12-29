#!/usr/bin/env python
# encoding:utf-8

"""
    数据库更新操作
======================

version   :   1.0
author    :   @`13
time      :   2017.1.17
"""

from db_opreation import DataBase
from Setting.static import Static

Static.static_value_init()
Static.log_init()
update_log = Static.LOGGER


class WhoisRecord(object):
    """whois数据更新类"""
    # Singleton-单例模式
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(WhoisRecord, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self, DataBaseObject, commitCount=Static.COMMIT_NUM):
        """
        构造函数
        :param DataBaseObject: 数据库操作对象,之前次对象应该先链接到数据库
        :param commitCount: 数据库事务提交频率
        未在数据库更新则会返回 None
        """
        self.DB = DataBaseObject
        self.DB.execute("""USE {database}""".format(
            database=str(Static.DATABASE_NAME)))  # 选择数据库
        self.commit_count = 0
        self.commit_limit = commitCount

    def Update(self, whois_dict):
        """
        将 whois数据字典 更新至 数据库 中
        :param whois_dict:whois信息字典
        >>Note:系统对于效率要求不高,做了<多次>查询校验,提高鲁棒性
        """
        # todo : check this func and do the test for this sys and start to write doc.  2017.2.12 AM
        self.commit_count += 1
        origin_flag = -100

        # commit 设置
        if self.commit_count >= self.commit_limit:
            self.DB.db_commit()
            self.commit_count = 0
        # ------------------------------------
        # 1,查询flag判断是否需要更新
        # ------------------------------------

        # ------------------------------------
        # 1,1 获取 domain 表中原始flag
        # ------------------------------------
        SQL = """SELECT whois_flag FROM {domainTable} WHERE `domain` = '{domain}';""".format(
            domainTable=Static.DOMAIN_TABLE, domain=whois_dict['domain'])  # 查询whois
        try:
            origin_flag = int(self.DB.execute(SQL)[0][0])
        except TypeError as e:
            update_log.error(str(whois_dict['domain']) + '不存在于域名表中 error:' + str(e))
        # ------------------------------------
        # 1,2 根据原始flag 和 本次flag进行判断
        # ------------------------------------

        # 如果 ([1]之前成功获取而本次获取失败 或者 [2]两次获取都失败 将不执行更新whois
        if origin_flag > 0 > whois_dict['flag']:
            return  # 1,2-[1]
        elif origin_flag < 0 and whois_dict['flag'] < 0:
            return  # 1,2-[2]
        # 如果 ([3]本次获取成功/之前没有获取过whois 将更新whois
        elif whois_dict['flag'] > 0 or origin_flag == 0:  # 1,2-[3]
            # ------------------------------------
            # 1,3 更新domain表
            # ------------------------------------
            if origin_flag != whois_dict['flag']:  # 如果上次flag与本次不相同,则更新flag为最新
                SQL = """UPDATE `{domainTable}` SET `whois_flag`={flag} WHERE (`domain`='{Domain}');""".format(
                    domainTable=Static.DOMAIN_TABLE, flag=whois_dict['flag'], Domain=whois_dict['domain'])
                self.DB.execute(SQL)

            # ------------------------------------
            # 2,更新whois表并检查whois是否过期
            # 2,1 whois数据更新语句
            # ------------------------------------
            SQL = """REPLACE INTO `{whoisTable}` set """.format(whoisTable=Static.WHOIS_TABLE)
            SQL += """`domain` = '{Value}', """.format(Value=whois_dict['domain'])
            SQL += """`tld` = '{Value}', """.format(Value=whois_dict['tld'])
            SQL += """`flag` = {Value}, """.format(Value=whois_dict['flag'])
            SQL += """`domain_status` = '{Value}', """.format(Value=whois_dict['domain_status'])
            SQL += """`sponsoring_registrar` = '{Value}', """.format(Value=whois_dict['sponsoring_registrar'])
            SQL += """`top_whois_server` = '{Value}', """.format(Value=whois_dict['top_whois_server'])
            SQL += """`sec_whois_server` = '{Value}', """.format(Value=whois_dict['sec_whois_server'])
            SQL += """`reg_name` = '{Value}', """.format(Value=whois_dict['reg_name'])
            SQL += """`reg_phone` = '{Value}', """.format(Value=whois_dict['reg_phone'])
            SQL += """`reg_email` = '{Value}', """.format(Value=whois_dict['reg_email'])
            SQL += """`org_name` = '{Value}', """.format(Value=whois_dict['org_name'])
            SQL += """`name_server` = '{Value}', """.format(Value=whois_dict['name_server'])
            SQL += """`creation_date` = '{Value}', """.format(Value=whois_dict['creation_date'])
            SQL += """`expiration_date` = '{Value}', """.format(Value=whois_dict['expiration_date'])
            SQL += """`updated_date` = '{Value}', """.format(Value=whois_dict['updated_date'])
            SQL += '''`details` = ("{Value}")'''.format(Value=whois_dict['details'])
            whois_update_SQL = SQL
            # ------------------------------------
            # 2,2-检查上次更新是否失败
            # ------------------------------------
            if whois_dict['flag'] > 0 >= origin_flag:
                self.DB.execute(whois_update_SQL)  # 若上次获取失败而这次成功则直接更新
                return
            # -----------------------------------------
            # 2,3-若上次和本次数据获取均成功:获取上次更新时间
            # -----------------------------------------
            SQL = """SELECT `updated_date` FROM `{whoisTable}` WHERE (`domain`='{Domain}');""".format(
                whoisTable=Static.WHOIS_TABLE, Domain=whois_dict['domain'])
            origin_update_date = self.DB.execute(SQL)
            if origin_update_date is None:  # 之间不存在的记录 : 单独插入更新whois
                self.DB.execute(whois_update_SQL)
                return
            elif whois_dict['flag'] > 0:  # 本次正确的记录才会更新whois/whowas
                # -----------------------------------------
                # 2,3:提取上次更新时间
                # -----------------------------------------
                try:
                    origin_update_date = origin_update_date[0][0]
                except Exception as error:
                    update_log.error(
                        '提取whois更新时间->' + str(whois_dict['domain']) + 'unexpected error occur!' + str(error))
                # -----------------------------------------
                # 3,判断是否需要更新whowas
                # 3,1 两次更新时间不同 && 上次数据正常 && 两次更新时间均不为空 -> 更新whowas
                # -----------------------------------------
                if origin_update_date != whois_dict['updated_date'] \
                        and origin_flag > 0\
                        and whois_dict['updated_date']\
                        and origin_update_date:
                    update_log.error('whowas更新 : ' + str(whois_dict['domain']))
                    # -----------------------------------------
                    # 3,2-whowas数据 SQL插入语句
                    # -----------------------------------------
                    whowas_update_SQL = """INSERT INTO {whowasTable}""".format(whowasTable=Static.WHOWAS_TABLE)
                    whowas_update_SQL += """(domain, tld, flag, domain_status, sponsoring_registrar, top_whois_server, sec_whois_server, reg_name, reg_phone, reg_email, org_name, name_server, creation_date, expiration_date, updated_date, details) """
                    whowas_update_SQL += """SELECT domain, tld, flag, domain_status, sponsoring_registrar, top_whois_server, sec_whois_server, reg_name, reg_phone, reg_email, org_name, name_server, creation_date, expiration_date, updated_date, details  """

                    # 更新whowas
                    self.DB.execute(whowas_update_SQL)
                # 最后更新whois记录
                self.DB.execute(whois_update_SQL)



# Demo
def __Demo():
    # 测试数据
    test_data = {'org_name': 'Nexperian Holding Limited', 'updated_date': '2016-11-22T04:10:03Z',
                 'domain': u'ccbanz.cc', 'reg_phone': '+86.57185022088', 'reg_email': 'YuMing@YinSiBaoHu.AliYun.com',
                 'expiration_date': '2017-11-22T04:10:03Z', 'reg_name': 'Nexperian Holding Limited',
                 'top_whois_server': 'ccwhois.verisign-grs.com', 'name_server': 'dns10.hichina.com;dns9.hichina.com',
                 'creation_date': '2016-11-22T04:10:03Z', 'flag': 1, 'domain_status': '4',
                 'details': 'Domain Name: ccbanz.cc\r\nRegistry Domain ID: 127221640_DOMAIN_CC-VRSN\r\nRegistrar WHOIS Server: grs-whois.hichina.com\r\nRegistrar URL: http://whois.aliyun.com/\r\nUpdated Date: 2016-11-22T04:10:03Z\r\nCreation Date: 2016-11-22T04:10:03Z\r\nRegistrar Registration Expiration Date: 2017-11-22T04:10:03Z\r\nRegistrar: HICHINA ZHICHENG TECHNOLOGY LTD.\r\nRegistrar IANA ID: 420\r\nReseller:\r\nDomain Status: ok http://www.icann.org/epp#OK\r\nRegistry Registrant ID: Not Available From Registry\r\nRegistrant Name: Nexperian Holding Limited\r\nRegistrant Organization: Nexperian Holding Limited\r\nRegistrant Street: Le Jia International No.999 Liang Mu Road Yuhang District\r\nRegistrant City: Hangzhou\r\nRegistrant State/Province: Zhejiang\r\nRegistrant Postal Code: 311121\r\nRegistrant Country: CN\r\nRegistrant Phone: +86.57185022088\r\nRegistrant Phone Ext: \r\nRegistrant Fax: +86.57186562951\r\nRegistrant Fax Ext: \r\nRegistrant Email: YuMing@YinSiBaoHu.AliYun.com\r\nRegistry Admin ID: Not Available From Registry\r\nAdmin Name: Nexperian Holding Limited\r\nAdmin Organization: Nexperian Holding Limited\r\nAdmin Street: Le Jia International No.999 Liang Mu Road Yuhang District\r\nAdmin City: Hangzhou\r\nAdmin State/Province: Zhejiang\r\nAdmin Postal Code: 311121\r\nAdmin Country: CN\r\nAdmin Phone: +86.57185022088\r\nAdmin Phone Ext: \r\nAdmin Fax:+86.57186562951\r\nAdmin Fax Ext: \r\nAdmin Email: YuMing@YinSiBaoHu.AliYun.com\r\nRegistry Tech ID: Not Available From Registry\r\nTech Name: Nexperian Holding Limited\r\nTech Organization: Nexperian Holding Limited\r\nTech Street: Le Jia International No.999 Liang Mu Road Yuhang District\r\nTech City: Hangzhou\r\nTech State/Province: Zhejiang\r\nTech Postal Code: 311121\r\nTech Country: CN\r\nTech Phone: +86.57185022088\r\nTech Phone Ext: \r\nTech Fax: +86.57186562951\r\nTech Fax Ext: \r\nTech Email: YuMing@YinSiBaoHu.AliYun.com\r\nName Server: dns10.hichina.com\r\nName Server: dns9.hichina.com\r\nDNSSEC: unsigned\r\nRegistrar Abuse Contact Email: abuse@list.alibaba-inc.com\r\nRegistrar Abuse Contact Phone: +86.95187\r\nURL of the ICANN WHOIS Data Problem Reporting System: http://wdprs.internic.net/\r\n>>>Last update of WHOIS database: 2016-11-22T04:10:03Z <<<\r\n\r\nFor more information on Whois status codes, please visit https://icann.org/epp\r\n\r\nRegistry Billing ID: Not Available From Registry\r\nBilling Name: Nexperian Holding Limited\r\nBilling Organization: Nexperian Holding Limited\r\nBilling Street: Le Jia International No.999 Liang Mu Road Yuhang District\r\nBilling City: Hangzhou\r\nBilling State/Province: Zhejiang\r\nBilling Postal Code: 311121\r\nBilling Country: CN\r\nBilling Phone: +86.57185022088\r\nBilling Phone Ext: \r\nBilling Fax: +86.57186562951\r\nBilling Fax Ext: \r\nBilling Email: YuMing@YinSiBaoHu.AliYun.com\r\n\r\nImportant Reminder: Per ICANN 2013RAA`s request, Hichina has modified domain names`whois format of dot com/net/cc/tv, you could refer to section 1.4 posted by ICANN on http://www.icann.org/en/resources/registrars/raa/approved-with-specs-27jun13-en.htm#whois The data in this whois database is provided to you for information purposes only, that is, to assist you in obtaining information about or related to a domain name registration record. We make this information available \\"as is,\\" and do not guarantee its accuracy. By submitting a whois query, you agree that you will use this data only for lawful purposes and that, under no circumstances will you use this data to: (1)enable high volume, automated, electronic processes that stress or load this whois database system providing you this information; or (2) allow, enable, or otherwise support the transmission of mass unsolicited, commercial advertising or solicitations via direct mail, electronic mail, or by telephone.  The compilation, repackaging, dissemination or other use of this data is expressly prohibited without prior written consent from us. We reserve the right to modify these terms at any time. By submitting this query, you agree to abide by these terms.For complete domain details go to:http://whois.aliyun.com/whois/domain/ccbanz.cc\r\n\n',
                 'sponsoring_registrar': 'HICHINA ZHICHENG TECHNOLOGY LTD.', 'tld': u'cc',
                 'sec_whois_server': 'grs-whois.hichina.com'}

    DB = DataBase()
    DB.db_connect()
    demo = WhoisRecord(DB)
    demo.Update(test_data)
    DB.db_commit()
    DB.db_close()


if __name__ == '__main__':
    import time

    start = time.time()
    __Demo()
    end = time.time()
    print end - start
