#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, urllib2
from BeautifulSoup import BeautifulSoup as bs

sys.path.append('jianfan')
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
    LNV_LIST = {'index': '2729'}
    LNV_LIST['baga']  = '3029'
    LNV_LIST['spicenwolf']  = '2662'
    LNV_LIST['fmp']  = '2339'

    def __init__(self, lnv, fec):
        self.lnv      = sfacg.SFACG3G_URL + '/Novel/' + sfacg.LNV_LIST[lnv] + '/MainIndex/'
        self.fec      = fec
        self.req      = urllib2.Request(self.lnv,"", sfacg.OPERA_X_H)
        self.response = urllib2.urlopen(self.req)
        # use BeautifulSoup
        self.soup     = bs(self.response)

        # chapter/volume counter
        ctr_chp = 0
        ctr_vol = -1
        self.chps = list()

        fl = open("list.txt","w")
        # print sub-chapters
        for ali in self.soup.ul.findAll('li'):
            if ali.strong == None:
                ctr_vol += 1
                self.chps.append((str(ctr_chp).rjust(3,'0') + '-' + str(ctr_vol).rjust(3,'0'), ali.a['href'].encode('utf-8'), ali.text.encode('utf-8')))
                debug_print(str(ctr_chp).rjust(3,'0') + '-' + str(ctr_vol).rjust(3,'0') + ' ' + ali.text.encode('utf-8') + ' ' + ali.a['href'].encode('utf-8'))
            else:
                if ctr_vol != 0:
                    ctr_chp += 1
                ctr_vol = 0
                debug_print(str(ctr_chp).rjust(3,'0') + ' ' + ali.text.encode('utf-8'))
            fl.write(str(ctr_chp).rjust(3,'0') + '-' + str(ctr_vol).rjust(3,'0') +' ' + jtof(ali.text).encode(self.fec,"ignore") + '\n')
        fl.close()
        self.soup.close()
        return 

    def download(self):
        """single test"""
        # debug counter
        #tmpct = 0
        for idx in self.chps:
            fname = idx[0] + "_" + self.fec + ".txt"
            if os.path.exists(fname):
                continue
            f = open(fname,"w")
            chplink       = sfacg.SFACG3G_URL + idx[1]
            print "Downloading ... ", idx[0], idx[2]
            self.response = urllib2.urlopen(chplink)
            hj = self.response.read()
            hj = hj.replace('<BR>','\n')
            hj = hj.replace('<br />','\n')
            hj = hj.replace('&amp;','&')
            hj = hj.replace('&nbsp;',' ')
            hj = hj.replace('&quot;','"')
            hj = hj.replace('&hellip;','…')
            hj = hj.replace('&middot;','·')
            hj = hj.replace('&lt;','<')
            hj = hj.replace('&gt;','>')
            hj = hj.replace('&ldquo;','“')
            hj = hj.replace('&rdquo;','”')
            hj = hj.replace('&lsquo;','‘')
            hj = hj.replace('&rsquo;','’')
            chpsp = bs(hj)
            debug_print(chpsp.body.text.encode('utf-8'))
            f.write(jtof(chpsp.body.text).encode(self.fec,"ignore"))
            f.close()
            # debuging
            #tmpct += 1
            #if tmpct == 1:
            #    break
