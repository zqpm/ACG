#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from BeautifulSoup import BeautifulSoup as bs
SFACG3G_URL = 'http://3g.sfacg.com'
OPERA_X_UA = 'Opera/9.80 (Windows Mobile; WCE; Opera Mobi/WMD-50286; U; en) Presto/2.4.13 Version/10.00'
OPERA_X_H = {'Accept-Charset': 'Big5', 'User-Agent' : OPERA_X_UA}

SFACG3G_INDEX = SFACG3G_URL + '/Novel/2729/MainIndex/'

def main():
    TARGET_URL = SFACG3G_INDEX
    req        = urllib2.Request(TARGET_URL,"", OPERA_X_H)
    response   = urllib2.urlopen(req)
    #content    = response.read().split("\n")
    #for line in content:
    #    print line

    soup       = bs(response)

    for ali in soup.ul.findAll('li'):
        if ali.strong == None:
            print ali.text, ali.a['href']
        else:
            print ali.text



if __name__ == '__main__':
    main()
