#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, urllib2
from BeautifulSoup import BeautifulSoup as bs

sys.path.append('jianfan')
from jianfan import jtof

#debugp = True
debugp = False

#SFACG3G_INDEX = WENKU8_PREFIX + '/Novel/2729/MainIndex/'
def debug_print(str):
    global debugp
    if debugp == True: 
        print str
    else:
        return

class wenku8:
    """wenku8 light novel"""
    # wenku8 light novel website prefix
    WENKU8_PREFIX = 'http://www.wenku8.cn/modules/article/reader.php?'
    # use UA of mobile browswer 
    OPERA_X_UA  = 'Opera/9.80 (Windows Mobile; WCE; Opera Mobi/WMD-50286; U; en) Presto/2.4.13 Version/10.00'
    OPERA_X_H   = {'Accept-Charset': 'utf-8', 'User-Agent' : OPERA_X_UA, 'Referer': WENKU8_PREFIX}
    # light novel list
    LNV_LIST = {}
    LNV_LIST['spicenwolf']  = 'aid=5'
    LNV_LIST['index']  = 'aid=3'

    def __init__(self, lnv, fec):
        self.lnv      = wenku8.WENKU8_PREFIX + wenku8.LNV_LIST[lnv]
        self.fec      = fec
        self.req      = urllib2.Request(self.lnv,'', wenku8.OPERA_X_H)
        self.response = urllib2.urlopen(self.req)
        # use BeautifulSoup
        self.soup     = bs(self.response)

        # chapter/volume counter
        ctr_chp = 0
        #ctr_vol = -1
        self.chps = list()
        self.tsp = bs()

        fl = open('list' + '_' + self.fec + '.txt','w')
        for atr in self.soup.body.findAll('tr'):
            tsp = bs(atr.text)
            if tsp.a != None:
                ctr_chp += 1
                sn = unicode(ctr_chp).rjust(3,'0')
                lk = tsp.a['href']
                title = unicode(tsp.contents[0])[:-1]
                self.chps.append((sn,lk,title))
                fl.write( sn.encode(fec, 'ignore') + '.txt' + ' ' + title.encode(fec, 'ignore') + '\n')
        tsp.close()
        fl.close()
        self.soup.close()
        return 
    def download(self, unit=[]):
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
            chplink = idx[1]
            print 'Downloading', idx[2], '>>> ', fname
            self.response = urllib2.urlopen(chplink)
            hj = self.rm_spchar(self.response.read())
            chpsp = bs(hj)
            chpsp = self.rm_spam(chpsp)
            # get title/content
            chttl = chpsp.findAll('div',{'class':'chaptertitle'})
            chcnt = chpsp.findAll('div',{'class':'chaptercontent'})
            for vol in range(len(chttl) -1):
                f.write(jtof(chttl[vol].text).encode(self.fec,'ignore').lstrip())
                f.write('\n==========\n')
                f.write(jtof(chcnt[vol].text).encode(self.fec,'ignore'))
                f.write('\n\n\n\n')
            chpsp.close()
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

