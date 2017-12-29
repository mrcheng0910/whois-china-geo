import datetime

d = []
e = []
frr = open('domain_20171219.out','r')
fr = open('alexa_top1million.txt','r')
for i in frr.readlines():
    d.append(i.split('\t')[0].strip())

for i in fr.readlines():
    e.append(i.strip())

print len(d)
print len(e)

f = list(set(e)-set(d))
print len(f)

fw = open('test1.txt','w')
n = 0
for i in f:
    n += 1
    fw.write(i+'\t'+str(datetime.datetime.now())+'\n')

print n
fw.close()
frr.close()
fr.close()