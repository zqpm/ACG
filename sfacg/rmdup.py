#!/usr/bin/env python
# -*- coding: utf8 -*-
import os

rmlist = list()
rmlist.append(u'轉載信息\n'.encode('big5'))
rmlist.append(u'彩圖\n'.encode('big5'))
rmlist.append(u'彩頁\n'.encode('big5'))
rmlist.append(u'插圖\n'.encode('big5'))
rmlist.append(u'插頁\n'.encode('big5'))
rmlist.append(u'插畫\n'.encode('big5'))

fn = open('./nlist.txt','w')
def main():
    f = open('./list.txt','rw')
    for line in f:
        if [True for x in line.split(' ') if x in rmlist]:
            fff = './'+line.split(' ')[0]+"_big5.txt"
            #print fff
            #print line.decode('big5').encode('utf-8')
            if os.path.exists(fff):
                os.remove(fff)
            continue
        fn.write(line)
    f.close()
    fn.close()

if __name__ == '__main__':
    main()
