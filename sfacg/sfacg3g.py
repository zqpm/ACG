#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, urllib2
from BeautifulSoup import BeautifulSoup as bs

sys.path.append('jianfan')
from jianfan import jtof

#debugp = True
debugp = False
SRC_URL = 'http://3g.sfacg.com'
SF_N_LST = {}  
SF_N_LST['index']      = '2729'
SF_N_LST['baga']       = '3029'
SF_N_LST['spicenwolf'] = '2662'
SF_N_LST['fmp']        = '2339'
SF_N_LST['is']         = '7678'


def debug_print(str):
    global debugp
    if debugp == True: 
        print str
    else:
        return

class sfacg:
    """sfacg light novel"""
    # sfacg light novel website prefix
    SFACG3G_URL = SRC_URL
    # use UA of mobile browswer 
    OPERA_X_UA  = 'Opera/9.80 (Windows Mobile; WCE; Opera Mobi/WMD-50286; U; \
                   en) Presto/2.4.13 Version/10.00'
    OPERA_X_H   = {'Accept-Charset': 'utf-8', 'User-Agent' : OPERA_X_UA, \
                   'Referer': SFACG3G_URL}
    # light novel list
    LNV_LIST = SF_N_LST

    def __init__(self, lnv, fec):
        self.lnv      = sfacg.SFACG3G_URL + '/Novel/' + sfacg.LNV_LIST[lnv] \
                        + '/MainIndex/'
        self.fec      = fec
        self.req      = urllib2.Request(self.lnv,"", sfacg.OPERA_X_H)
        self.response = urllib2.urlopen(self.req)
        # use BeautifulSoup
        self.soup     = bs(self.response)

        # chapter/volume counter
        ctr_chp = 0
        ctr_vol = -1
        self.chps = list()

        fl = open('list' + '_' + self.fec + '.txt','w')
        for ali in self.soup.ul.findAll('li'):
            # check <strong> tag, it's not content
            if ali.strong == None:
                ctr_vol += 1
            else:
                if ctr_vol != 0:
                    ctr_chp += 1
                ctr_vol = 0
            sn = str(ctr_chp).rjust(3,'0') + '-' \
                 + str(ctr_vol).rjust(3,'0')
            lk = ali.a['href'].encode('utf-8')
            title = ali.text.encode('utf-8')
            self.chps.append((sn,lk,title))
        fl.close()
        self.soup.close()
        return 

    def download(self):
        if len(unit) == 0:
            unit = self.chps
        else:
            nunit = list()
            for idd in unit:
                nunit.append(self.chps[idd])
        unit = nunit
        for idx in unit:
            fname = idx[0] + '_' + self.fec + '.txt'

            if os.path.exists(fname):
                continue
            f = open(fname,'w')
            chplink = sfacg.SFACG3G_URL + idx[1]
            print 'Downloading', idx[2], '>>> ', fname
            self.response = urllib2.urlopen(chplink)
            hj = self.rm_spchar(self.response.read())
            chpsp = bs(hj)
            # format output by sfacg
            f.write(jtof(chpsp.body.text).encode(self.fec,"ignore"))
            f.close()
        return
    def rm_spchar(self,str):
        str = str.replace('<BR>','')
        str = str.replace('<br>','')
        str = str.replace('<br />','')
        str = str.replace('&amp;','&')
        str = str.replace('&nbsp;',' ')
        str = str.replace('&quot;','"')
        str = str.replace('&hellip;','…')
        str = str.replace('&middot;','·')
        str = str.replace('&lt;','<')
        str = str.replace('&gt;','>')
        str = str.replace('&ldquo;','“')
        str = str.replace('&rdquo;','”')
        str = str.replace('&lsquo;','‘')
        str = str.replace('&rsquo;','’')
        if self.fec == 'utf-8':
            str = str.replace('\r','')
            str = str.replace('\n\n','\n')
        elif self.fec == 'big5':
            str = str.replace('\r\n\r\n','\r\n')
            
        return str
    def rm_spam(self,sp):
        for jsp in sp.findAll('script'):
            jsp.extract()
        return sp

