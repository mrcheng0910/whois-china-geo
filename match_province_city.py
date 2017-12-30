# encoding:utf-8
"""
使用Levenshtein距离初始化字符，利用k-means算法来进行聚类分析
"""

import Levenshtein
import json
import re
from collections import Counter
from get_whois.data_base import MySQL
from get_whois.config import SOURCE_CONFIG
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class ProvinceCityObj(object):
    """
    省份和城市名称类
    """

    def __init__(self, original_province, original_city,region_data):
        self.original_province = original_province.strip().lower()  # 原始的省份名称
        self.original_city = original_city.strip().lower()  # 原始的城市名称
        self.region_data = region_data  # 区域数据

        # 省份相关变量
        self.unconfirmed_province = ""   # 格式化后的未确认省份名称
        self.candidate_provinces = []
        self.confirmed_province = ""   # 匹配的省份名称
        self.province_alias = ""   # 与之匹配的省份名称
        self.province_alias_ratio = 0.0

        # 城市相关变量
        self.unconfirmed_city = ""  # 格式化后的未确认城市名称
        self.candidate_citys = []
        self.confirmed_city = ""  # 匹配的城市名称
        self.city_alias = ""  # 与之匹配的城市名称
        self.city_alias_ratio = 0.0

        # 特殊情况
        self.multiple_province = False
        self.multiple_city = False


    def _process_province_city(self):
        """
        格式化省份和城市名称，去除除数字、字母和汉字的其他内容
        """
        # 删除除数字、字母和汉字等其他内容,可能删除后，剩余为空字符串
        self.unconfirmed_province = self._remove_punctuation(self.original_province).lower()
        self.unconfirmed_city = self._remove_punctuation(self.original_city).lower()


    def _remove_punctuation(self, line):
        """
        提取出数字、字母和汉字，去除其他字符
        :param line: 待处理的字符串
        """
        rule = re.compile(ur"[^a-zA-Z0-9\u4e00-\u9fa5]")
        # line = rule.sub('', unicode(line, "utf-8"))
        line = rule.sub('',line)
        return line


    def _compute_similarity(self,s1, s2):
        """
        s1为要匹配的，s2为标准的格式
        计算相似性两个字符串的相似性
        相似性分为三个等级：
        等级1：完全相同
        等级2：相似度
        等级3：s2存在在s1中
        todo 等级2和等级3的分配是否合理
        """
        # todo 需要对这三种方法的优劣进行分析， 选择最有效的一种计算方法

        # 两个字符串完全相同
        if s1 == s2:
            similarity_level = 1
            return 1.0, similarity_level

        # 若只有2个字母，则使用相似性进行计算,不能使用index
        if len(s2) <= 2:  # 2或者3 todo 验证
            similarity_level = 2
            return Levenshtein.jaro_winkler(s1, s2, 0.1), similarity_level
        else:
            try:
                s1.index(s2)  # 标准名称是否在待验证的名称中出现，若无则会出现异常
            except ValueError:
                # return Levenshtein.jaro(s1, s2)   # 相似度
                similarity_level = 2
                return Levenshtein.jaro_winkler(s1, s2, 0.1), similarity_level
                # return Levenshtein.distance(s1,s2)  # 距离
                # return Levenshtein.ratio(s1,s2)   # 相似性
            else:
                similarity_level = 3
                return 1.0, similarity_level  # 完全匹配则返回1.0

    def match_candidate_province(self, name):
        """
        与省份/直辖市/自治区/行政区等数据进行比较，根据相似度，匹配出相似的候选项
        :param name string: 待比较的选项
        :return: candidate_provinces dict : 包含匹配的省份名称，所匹配的省份别名，相似度和匹配等级

        """
        candidate_provinces = []
        for prov_name in self.region_data:
            prov_alias = self.region_data[prov_name]['alias']
            for alias in prov_alias:
                province_ratio = {}
                ratio, level = self._compute_similarity(name, alias)  # 相似度和等级
                if ratio >= 0.90:
                    province_ratio["province"] = prov_name
                    province_ratio["alias"] = alias
                    province_ratio["ratio"] = ratio
                    province_ratio["level"] = level
                    candidate_provinces.append(province_ratio)
        candidate_provinces = sorted(candidate_provinces, key=lambda ratio: ratio["ratio"], reverse=True)  # 降序排序
        return candidate_provinces

    def choose_province_city(self):
        """
        得到匹配的省份和对应城市的名称
        """

        self._process_province_city()  # 省份和城市名称格式化处理
        self.candidate_provinces = self.match_candidate_province(self.unconfirmed_province)  # 获取与省份相似的名称和相似度集合
        self.choose_province()  # 获取省份名称和其他情况

        self.match_candidate_city()  # 获取对应省份的相似名称的城市和概率集合
        self.choose_city()

    def choose_province(self):
        """
        选择最准确的省份，以及匹配的省份内容和等级情况
        todo 等级暂时未使用上
        """
        province_counter = Counter() # 统计匹配出的各个省份出现的次数
        if not self.candidate_provinces:  # 如果为空，则结束
            return
        for p in self.candidate_provinces:
            province_counter[p['province']] += 1

        self.confirmed_province,self.multiple_province = self.vote_poll(province_counter)

    def vote_poll(self, counter):
        """
        选择票数最多的候选项
        :param counter: dict 选项和票数分布
        :return:
            most_votes_item: string 得票最多的选项，可能是票数相同多个候选项
            is_same:  bool 是否有相同票数的选项
        """
        items = []  # 候选项
        initial_vote = 0  # 初始票数为0
        # 若只有1个候选项，则直接输出唯一候选项，无相同票数
        if len(counter) == 1:
            most_votes_item = counter.keys()[0]
            is_same = False
        else:  # 多于1个候选项时获取票数最多的选项
            for item, votes in counter.most_common():  # 注意根据票数已对候选项进行了排序
                if votes >= initial_vote:
                    items.append(item)
                    initial_vote = votes
                else:    # 若无，则退出
                    break

            if len(items) >= 2:
                is_same = True
            else:
                is_same = False
            most_votes_item = ','.join(items)

        return most_votes_item, is_same

    def match_candidate_city(self):
        """
        得到候选的城市和概率集合
        :param province_region:
        :return:
        """
        # 未匹配到省份，省份为空
        if not self.confirmed_province:
            return

        # 匹配到两个省份
        if self.multiple_province:
            # print "匹配出多个省份",self.confirmed_province.split(',')
            confirmed_province_citys = []

            for p in self.confirmed_province.split(','):
                province_region = self.region_data[p]['city']
                citys = self.match_city(province_region,self.unconfirmed_city)
                confirmed_province_citys.append(citys)
                if citys:
                    self.confirmed_province = p
                    self.candidate_citys = citys
                    break
            return

        province_region = self.region_data[self.confirmed_province]['city']
        self.candidate_citys = self.match_city(province_region,self.unconfirmed_city)

    def match_city(self,province_region,unconfirmed_city):
        candidate_citys = []
        for c in province_region:
            city_alias = province_region[c]
            for i in city_alias:
                city_ratio = {}
                ratio, level = self._compute_similarity(unconfirmed_city, i)
                if ratio >= 0.9:
                    city_ratio["city"] = c
                    city_ratio["alias"] = i
                    city_ratio["ratio"] = ratio
                    city_ratio["level"] = level
                    candidate_citys.append(city_ratio)
        candidate_citys = sorted(candidate_citys, key=lambda ratio: ratio["ratio"], reverse=True)  # 降序排序
        return candidate_citys

    def choose_city(self):
        """
        选择最准确的省份，以及匹配的省份内容和等级情况
        todo 等级暂时未使用上
        """
        city_counter = Counter()  # 统计匹配出的各个省份出现的次数
        if not self.candidate_citys:  # 如果候选城市集合为空，则结束
            return
        for p in self.candidate_citys:
            city_counter[p['city']] += 1

        self.confirmed_city, self.multiple_city = self.vote_poll(city_counter)

    def get_all_feature(self):
        """
        获取所有信息
        """
        return {
            "candidate_provinces": self.candidate_provinces,
            "confirmed_province": self.confirmed_province,
            "candidate_citys": self.candidate_citys,
            "confirmed_city": self.confirmed_city,
            "multiple_province": self.multiple_province,
            "multiple_city": self.multiple_city
        }

    def analyze_feature(self):

        # if self.confirmed_province != "beijing":
        #     return
        print "待匹配的省份和城市为：",self.original_province+","+self.original_city
        if not self.confirmed_province:
            print "没有找到匹配的省份，其待候选的省份列表为："
            print self.candidate_provinces
            return
        else:
            print '匹配的省份为：', self.confirmed_province
        if not self.confirmed_city:
            print "没有找到匹配的城市，原因为："
            if self.multiple_province:
                print "发现匹配出多个省份，无法确认城市"
                return
            else:
                print "其待候选的城市列表为："
                print self.candidate_citys
                return
        else:
            print '匹配的城市为：', self.confirmed_city


def verify_province_city(province_name,city_name,region_data):
    """
    验证输入的省份和城市
    :param province_name:
    :param city_name:
    :return:
    """
    # region_data = read_province()  # 标准区域数据
    province_city_obj = ProvinceCityObj(province_name, city_name, region_data)  # 创建对象
    province_city_obj.choose_province_city()  # 选择省份和城市

    verify_results = province_city_obj.get_all_feature()
    # province_city_obj.analyze_feature()

    return verify_results


def read_province():
    """
    读取省份名称和其别名，以及省份下的城市以及城市名称
    :return:
    """
    with open('province_city.json','r') as f:
        data = json.load(f)
    return data

def fetch_resource_data():
    """获得源数据
    :param tb_name: string 表名
    :return: results: 查询结果
    """
    db = MySQL(SOURCE_CONFIG)
    db.query('SELECT reg_province,reg_city FROM domain_info WHERE (reg_country="cn" OR reg_country = "china") AND province IS NULL GROUP BY reg_city')
    results = db.fetch_all_rows()
    db.close()
    return results

def update_db(db,province,city,reg_province,reg_city):
    # db = MySQL(SOURCE_CONFIG)
    sql = 'UPDATE domain_info SET province="%s",city="%s" WHERE reg_province = "%s" AND reg_city="%s" ' %(province,city,reg_province,reg_city)
    db.update_no_commit(sql)
    # db.close()


def main():
    region_data = read_province()  # 标准区域数据
    db = MySQL(SOURCE_CONFIG)
    data = fetch_resource_data()
    for p, c in data:
        result = verify_province_city(p, c,region_data)
        print result
        update_db(db,result['confirmed_province'],result['confirmed_city'], p, c)

    db.commit()
    db.close()

if __name__ == "__main__":
    main()   # todo 优化增加内存字典

