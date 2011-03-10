#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, urllib2
sys.path.append('jianfan')
from BeautifulSoup import BeautifulSoup as bs
from jianfan import jtof

#debugp = True
debugp = False

#SFACG3G_INDEX = SFACG3G_URL + '/Novel/2729/MainIndex/'
def debug_print(str):
    global debugp
    if debugp == True: 
        print str
    else:
        return

class sfacg:
    """sfacg light novel"""
    # sfacg light novel website prefix
    SFACG3G_URL = 'http://3g.sfacg.com'
    # use UA of mobile browswer 
    OPERA_X_UA  = 'Opera/9.80 (Windows Mobile; WCE; Opera Mobi/WMD-50286; U; en) Presto/2.4.13 Version/10.00'
    OPERA_X_H   = {'Accept-Charset': 'utf-8', 'User-Agent' : OPERA_X_UA, 'Referer': SFACG3G_URL}
    # light novel list
    LNV_LIST    = {'index': '2729'}

    def __init__(self, lnv):
        self.lnv      = sfacg.SFACG3G_URL + '/Novel/' + sfacg.LNV_LIST[lnv] + '/MainIndex/'
        self.req      = urllib2.Request(self.lnv,"", sfacg.OPERA_X_H)
        self.response = urllib2.urlopen(self.req)
        # use BeautifulSoup
        self.soup     = bs(self.response)

        # chapter/volume counter
        ctr_chp = 0
        ctr_vol = -1
        self.chps = list()

        # print sub-chapters
        for ali in self.soup.ul.findAll('li'):
            if ali.strong == None:
                ctr_vol += 1
                self.chps.append((str(ctr_chp) + '-' + str(ctr_vol), ali.a['href'].encode('utf-8'), ali.text.encode('utf-8')))
                debug_print(str(ctr_chp) + '-' + str(ctr_vol) + ' ' + ali.text.encode('utf-8') + ' ' + ali.a['href'].encode('utf-8'))
            else:
                if ctr_vol != 0:
                    ctr_chp += 1
                ctr_vol = 0
                debug_print(str(ctr_chp) + ' ' + ali.text.encode('utf-8'))
        self.soup.close()
        return 

    def download(self):
        """single test"""
        tmpct = 0
        for idx in self.chps:
            f = open(idx[0]+".txt","w")
            chplink       = sfacg.SFACG3G_URL + idx[1]
            print "Downloading ... ", idx[0], idx[2]
            self.response = urllib2.urlopen(chplink)
            hj            = self.response.read().replace('<BR>','\n').replace('&nbsp;',' ')
            chpsp         = bs(hj)
            debug_print(chpsp.body.text.encode('utf-8'))
            f.write(jtof(chpsp.body.text).encode('utf-8'))
            f.close()
            tmpct += 1
            if tmpct == 1:
                break
