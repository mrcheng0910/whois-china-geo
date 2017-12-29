# encoding:utf-8
"""
使用Levenshtein距离初始化字符，利用k-means算法来进行聚类分析
"""

import Levenshtein
import json
import re


def read_raw_data():
    """
    读取待处理的省份与对应的城市，这是未分类和验证的数据，有大量异常和错误
    """
    fp = open('./data/province_city.txt', 'r')
    data = []
    for i in fp:
        data.append(i)
    return data


def read_province():
    """
    读取省份名称和其别名，以及省份下的城市以及城市名称
    :return:
    """
    with open('province_city.json','r') as f:
        data = json.load(f)
    return data




class ProvinceCityObj(object):
    """
    省份和城市名称类
    """
    region_data = read_province()

    def __init__(self,unconfirmed_province,unconfirmed_city):
        self.unconfirmed_province = unconfirmed_province
        self.unconfirmed_city = unconfirmed_city
        self.confirmed_province = ""
        self.province_alias = ""
        self.confirmed_city = ""
        self.city_alias = ""

    def process_province_city(self):
        self.unconfirmed_province = remove_punctuation(self.unconfirmed_province).strip().lower()
        self.unconfirmed_city = remove_punctuation(self.unconfirmed_city).strip().lower()

    def is_chinese(self,uchar):
        """
        是否为中文
        :param uchar:
        :return:
        """
        if u'\u4e00' <= uchar <= u'\u9fff':
            return True
        else:
            return False

    def remove_punctuation(self,line):
        """
        提取出数字、字母和汉字，字符去除
        :param line:
        :return:
        """
        rule = re.compile(ur"[^a-zA-Z0-9\u4e00-\u9fa5]")
        line = rule.sub('', unicode(line, "utf-8"))
        # print type(line.encode("utf-8"))
        return line.encode("utf-8")


def compute_similarity(s1, s2):
    """
    计算相似性
    :param s1:
    :param s2:
    :return:
    """
    # todo 需要对这三种方法的优劣进行分析，选择最有效的一种计算方法

    if len(s1) == 1:  # 若只有1个字母，则使用相似性进行计算
        return Levenshtein.jaro_winkler(s1, s2,0.1)
    try:
        s1.index(s2)   # 标准名称是否在待验证的名称中出现，若无则会出现异常
    except ValueError:
        # return Levenshtein.jaro(s1, s2)   # 相似度
        return Levenshtein.jaro_winkler(s1, s2,0.1)
        # return Levenshtein.distance(s1,s2)  # 距离
        # return Levenshtein.ratio(s1,s2)   # 相似性
    else:
        return 1.0  # 完全匹配则返回1.0





def process_data(raw_data):
    """
    处理原始的省份城市数据，处理方法如下：
    1. 省份，城市都是数字
    2. 省份是数字，城市是字母
    3. 省份是字母，城市是数字
    4. 省份和城市都是字母
    """
    province_available = []
    province_unavailable = []
    for i in raw_data:
        # 提取出省份和城市
        province_city = i.split('\t')
        if len(province_city) == 1:
            province = province_city[0].strip()
            city = ""
        else:
            province = province_city[0].strip()
            city = province_city[1].strip()

        # 删除除数字、字母和汉字等其他内容,可能删除后，剩余为空字符串
        province = remove_punctuation(province).strip().lower()
        city = remove_punctuation(city).strip().lower()
        if province.isalpha() or is_chinese(province.decode('utf-8')):
            province_available.append((province,city))
        else:
            province_unavailable.append((province,city))

    return province_available,province_unavailable


def is_chinese(uchar):
    """
    是否为中文
    :param uchar:
    :return:
    """
    if u'\u4e00' <= uchar<=u'\u9fff':
        return True
    else:
        return False


def remove_punctuation(line):
    """
    提取出数字、字母和汉字，字符去除
    :param line:
    :return:
    """
    rule = re.compile(ur"[^a-zA-Z0-9\u4e00-\u9fa5]")
    line = rule.sub('',unicode(line,"utf-8"))
    # print type(line.encode("utf-8"))
    return line.encode("utf-8")





def match_candidate_province(unconfirmed_province, region_data):
    """
    获取候选的省份列表。根据输入的未确认的省份名称，经过匹配，得到可匹配上的省份名称和相似比率
    :param unconfirmed_province: 待确认的省份名称
    :param region_data: 正确的省份名称数据库
    :return:
        candidate_provinces: 匹配上的省份和其相似性的列表
    """
    candidate_provinces = []
    for prov_name in region_data:
        prov_alias = region_data[prov_name]['alias']
        for a in prov_alias:
            province_ratio = {}
            ratio = compute_similarity(a.encode("utf-8"), unconfirmed_province)  # 相似性
            if ratio >= 0.6:
                province_ratio["province"] = prov_name
                province_ratio["alias"] = a.encode("utf-8")
                province_ratio["ratio"] = ratio
                candidate_provinces.append(province_ratio)
    candidate_provinces = sorted(candidate_provinces, key=lambda ratio: ratio["ratio"], reverse=True)  # 降序排序

    return candidate_provinces


def match_candidate_city(unconfirmed_city, province_region):

    candidate_citys = []
    for c in province_region:
        city_alias = province_region[c]
        for i in city_alias:
            city_ratio = {}
            ratio = compute_similarity(unconfirmed_city, i.encode("utf-8"))
            if ratio >= 0.6:
                city_ratio["city"] = c
                city_ratio["alias"] = i.encode("utf-8")
                city_ratio["ratio"] = ratio
                candidate_citys.append(city_ratio)
    candidate_citys = sorted(candidate_citys, key=lambda ratio: ratio["ratio"], reverse=True)  # 降序排序

    return candidate_citys


def choose_province_city(candidate_provinces, unconfirmed_city, region_data):
    """
    得到域名的准确省份和城市地址
    :param candidate_provinces: 所有待匹配的候选省份
    :return:
    """
    confirmed_province = ""
    confirmed_city = ""
    candidate_citys = []
    for p in candidate_provinces:
        p_ratio = p['ratio']   # 与该省份名称的相似性
        if p_ratio == 1.0:   # 省份完全匹配
            confirmed_province = p['province']
            province_region = region_data[confirmed_province]['city']
            candidate_citys = match_candidate_city(unconfirmed_city,province_region)

            if confirmed_province == 'beijing':
                choose_city(unconfirmed_city,candidate_citys,region_data,confirmed_province)


def choose_city(unconfirmed_city, candidate_citys, region_data,confirmed_province):
    """
    选择最终的城市
    :param unconfirmed_city:  未确认的城市
    :param candidate_citys:  候选的城市列表
    :param region_data: 省份和城市地理信息
    :return:
    """
    print "待确认", unconfirmed_city
    confirmed_city = ""

    for c in candidate_citys:
        c_ratio = c['ratio']
        if c_ratio >= 0.9:  # 超过0.9相似度，表示基本匹配成功，但是0.9阈值需要确认todo
            confirmed_city = c['city']
            break
    if not confirmed_city:
        temp_candidate_citys = match_candidate_province(unconfirmed_city, region_data)
        if temp_candidate_citys:
            temp_province = temp_candidate_citys[0]['province']
            if confirmed_province == temp_province:
                confirmed_city = temp_province

    print confirmed_city
    # return confirmed_city


def main():

    data = read_raw_data()  # 获得要识别的省份和城市名称
    province_available, _,= process_data(data)  # 处理原始数据
    region_data = read_province()  # 获取正确的省份和城市的名称
    for unconfirmed_province,unconfirmed_city in province_available[1000:1500]:
        # print unconfirmed_province
        candidate_provinces = match_candidate_province(unconfirmed_province, region_data)
        # print province_alias
        choose_province_city(candidate_provinces, unconfirmed_city, region_data)


if __name__ == "__main__":

    main()

