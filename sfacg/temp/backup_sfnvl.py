#!/usr/bin/env python


import os, re, sys, string, time
import urllib, urllib2
from BeautifulSoup import BeautifulSoup as bs


PREFIX_CHP = "http://book.sfacg.com/"

class nvlchp:
    title = ''
    url = ''
    text = ''
    def __init__(self, url='', title=''):
        self.title = title
        self.url   = url
        try:
            soup = bs(urllib2.urlopen(url).read()) 
        except e:
            print e
            sys.exit(0)
        soup.findAll('div',{'class':'m_text6 Blue_link3'})[0].contents[1]



class nvlvol:
    url = ''
    chp = []
    def __init__(self, url,vols=[0]):
        self.url = url
        try:
            soup = bs(urllib2.urlopen(url).read()) 
            #print soup.findAll('div',{'class':'m_text6 Blue_link3'})
        except Exception, e:
            print e
            sys.exit(0)
        for vol in vols:
            for chps in soup.findAll('div', {'class':'m_text6 Blue_link3'})[vol]('a'):
                chp_url = PREFIX_CHP + chps['href']
                title = chps.string
                self.chp.append(nvlchp(chp_url, title))

def main():
    x = nvlvol('http://book.sfacg.com/Novel/2729/MainIndex/')
    sys.exit(0)

if __name__ == '__main__':
    main()
