# encoding:utf-8
import tldextract


def write_upload():
    fp = open('domain(1).txt', 'r')

    fw = open('test4.txt', 'w')
    for i in fp.readlines():
        domain = i.split(' ')[0].strip()

        tld = tldextract.extract(domain).suffix

        if tld:
            domain = tldextract.extract(domain).domain + '.' + tld
            print domain
            fw.write(domain + '\t' + 'malicious' + '\t' + 'wiseye' + '\n')

    fp.close()
    fw.close()

def to_update():
    fp = open('domain(1).txt', 'r')

    fw = open('test5.txt', 'w')
    for i in fp.readlines():
        print i.split(' ')
        domain = i.split(' ')[0].strip()
        date_time = i.split(' ')[4] +' '+i.split(' ')[5].strip()
        tld = tldextract.extract(domain).suffix

        if tld:
            domain = tldextract.extract(domain).domain + '.' + tld
            # print domain
            fw.write(domain + '\t'+date_time+ '\n')

    fp.close()
    fw.close()

to_update()