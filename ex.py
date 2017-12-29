#encoding:utf-8

import tldextract
from collections import Counter

fp = open('2.txt','r')
domains = []

# fw = open("test1.txt",'w')
tld_counter = Counter()
for i in fp:
    d = i.strip().split(',')
    # if d[1]:
        # fw.write(d[0]+'\t'+d[1]+'\n')
        # print
        # print i
    domains.append(d[0])

# fw.close()



# print len(domains)
for i in domains:
    suffix = tldextract.extract(i).suffix
    tld_counter[suffix] += 1


# print tld_counter
for i,j in tld_counter.most_common(20):
    print i+'\t'+str(j)
#
fp.close()





# import json
# with open('1.txt', 'r') as f:
#     data = json.load(f)
#
# for i in data:
#     print i, data[i]