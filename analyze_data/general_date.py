# encoding: utf-8
"""
格式化处理不同时区的时间，统一为+08：00时间，即北京时间
1. 无时间（00:00:00）和timezone信息的时间格式，默认为东八区标记
2. 其他含有时区的信息，转换为东八区

"""
try:
    import pytz
except:
    print 'sudo easy_install pytz'

from dateutil.parser import parse

cn = pytz.timezone('Asia/Shanghai')   # 设置中国时区+8

# 已知的支持的时间格式
timezone_format = [
    '2016-07-16 23:06:34',
    '2015-01-05T13:27:16Z',
    '11-sep-2015',
    'Wed Aug 03 15:17:28 GMT 2016',
    '1997-09-15T00:00:00-0700',
    '1998-05-06 04:00:00+10',
    '23-Dec-2016 06:02:34 UTC',
    '2016/08/24',
    '2013-08-01',
    '24-12-2010',
    '2013-11-09T16:57:55.0z',
    '2005-04-27T16:50:52+0000Z'
]


def extract_date(str_time):
    """
    格式化时间
    """
    if str_time.find('.') != -1:  # 针对'2013-11-09T16:57:55.0z'的情况
        str_time = str_time.split('.')[0]
    elif str_time.find('+0000') != -1:
        str_time = str_time.split('+0000')[0]  # 针对'2005-04-27T16:50:52+0000Z'的情况

    try:
        time_parse = parse(str_time)    # 解析日期为datetime型
    except ValueError, e:
        return str_time

    try:
        time_parse = time_parse.astimezone(tz=cn)   # 有时区转换为北京时间
    except ValueError, e:
        time_parse = cn.localize(time_parse)   # 无时区转换为localtime，即北京时间
    return time_parse.year


# print extract_date('2002-09-14T09:11:41+0000Z')