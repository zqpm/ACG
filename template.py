#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, urllib2
from BeautifulSoup import BeautifulSoup as bs
sys.path.append('jianfan')
from jianfan import jtof


LNV_LIST = {}           # novel list

# debug print
def dbpt(str):
    global debugp
    if debugp == True: 
        print str
    else:
        return

def sfacg_getlist(bs, fec):
    nlist = []
    # chapter/volume counter
    ctr_chp = 0
    ctr_vol = -1
    fl = open('list' + '_' + fec + '.txt','w')
    for ali in bs.ul.findAll('li'):
        # check <strong> tag, it's not content
        if ali.strong == None:
            ctr_vol += 1
        else:
            if ctr_vol != 0:
                ctr_chp += 1
            ctr_chp = 0
        sn    = str(ctr_chp).rjust(3,'0') + '-' + str(ctr_vol).rjust(3,'0')
        lk    = ali.a['href'].encode('utf-8')
        title = ali.text.encode('utf-8')
        nlist.append((sn,lk,title))
    fl.close()
    return nlist



# novel class
class novel:
    """novel website module"""
    OPERA_X_UA  = 'Opera/9.80 (Windows Mobile; WCE; Opera Mobi/WMD-50286; U; \
                   en) Presto/2.4.13 Version/10.00'

    def __init__(self, lnv, fec, url):
        self.SRC_URL  = url
        OPERA_X_H     = {'Accept-Charset': 'utf-8', 'User-Agent' : OPERA_X_UA,\
                         'Referer': SRC_URL}
        self.lnv      = self.SRC_URL + '/Novel/' \
                        + novel.LNV_LIST[lnv] + '/MainIndex/'
        self.fec      = fec
        self.req      = urllib2.Request(self.lnv,"", novel.OPERA_X_H)
        self.response = urllib2.urlopen(self.req)
        self.soup     = bs(self.response)               
        self.chps     = getlist(self.soup, fec)
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
            print 'Downloading', idx[2], '>>> ', fname
            f             = open(fname,'w')
            chplink       = self.SRC_URL + idx[1]
            self.response = urllib2.urlopen(chplink)
            processed     = self.dosomething(self.response.read())
            chpsp         = bs(processed)
            # format output by sfacg
            f.write(jtof(chpsp.body.text).encode(self.fec,"ignore"))
            f.close()
        return
    # do some processing
    def dosomething(self,str):
        str = self.rm_spchar(str)
        return str
    # replace HTML special character
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
    # remove javascript ad
    def rm_spam(self,sp):
        for jsp in sp.findAll('script'):
            jsp.extract()
        return sp

