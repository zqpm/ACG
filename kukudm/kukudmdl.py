#!/usr/bin/env python

import os
import re
import sys
import string
import time
import urllib
import urllib2
import tarfile
import zipfile
import tempfile
import shutil
from optparse import OptionParser, OptionGroup
from BeautifulSoup import BeautifulSoup as bs

TMPFOLDERPFX = 'kukudm_'
TMP_FOLDER = tempfile.mkdtemp(prefix=TMPFOLDERPFX) + '/'
PREFIX_LST = []
PREFIX_LST.append('http://ascrsbdtdb.kukudm.net:82/')
PREFIX_LST.append('http://ascrsbdfdb.kukudm.net:81/')
PREFIX_LST.append('http://dx.kukudm.net/')
PREFIX_LST.append('http://hzw.socomic.com/')
BROWSER_UA = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) \
             AppleWebKit/534.10 (KHTML, like Gecko) \
             Chrome/8.0.552.237 Safari/534.10'
PREFIX_WEBSITE = "http://comic.kukudm.com"
WEBSITE = 'http://kukudm.com/'
CLEAR_FLD = []


def cleanup():
    """ 
    cleanup the temp folder ever used
    """ 
    global CLEAR_FLD
    TMP_PREFIX = tempfile.gettempdir() + '/'
    for i in os.listdir(TMP_PREFIX) :
        search_pattern = '^(' + TMPFOLDERPFX + ')(.+)'
        m = re.search(search_pattern,i) 
        if m:
            CLEAR_FLD.append(m.group())
    for j in CLEAR_FLD:
        TO_BE_DELETED = TMP_PREFIX + j
        shutil.rmtree(TO_BE_DELETED)

class kkdm_img(object):
    """
    download kukudm img
    """
    url   = ''
    fname = ''
    def __init__(self, url, path, page):
        self.url   = url
        subname    = url.split('/')[-1].split('.')[-1] 
        self.fname = path + '/' + \
                     str(page).rjust(3,'0') + \
                     '.' + \
                     subname
        #if (not os.path.exists(self.fname))
        #    or(os.path.getsize(self.fname) < 500):
        if ((os.path.exists(self.fname)) 
            and (os.path.getsize(self.fname) < 500)):
            pass
        else:
            print "retrieving the comic: %s" % self.fname
            self.dl()

    def dl(self):
        img = urllib.URLopener()
        while 1: 
            try:
                img.retrieve(self.url, self.fname)
                if os.path.getsize(self.fname) < 500:
                    continue
                else:
                    break
            except IOError, e:
                if e[1] != 404:
                    print "Warning: Retrieve %s Error." % self.url
                    print "time.sleep(5) and again" 
                    time.sleep(5)
                    raise RuntimeError("404, prefix problem") 
                else:
                    print "Some Network Problem .."

class kkdm_vol(object):
    """kukudm vol"""
    global PREFIX_LST
    global BROWSER_UA
    img  = []
    hder = {'User-Agent': BROWSER_UA, 'Referer': WEBSITE}

    def __init__(self, url, path, vol):
        self.url  = url
        self.vol  = str(vol)
        self.pfx  = PREFIX_LST[0]
        self.path = path + '/' + str(vol).rjust(3,'0') 
        req= urllib2.Request(url, None, kkdm_vol.hder)
        while 1:
            try:
                response = urllib2.urlopen(req)
                break
            except urllib2.URLError, e:
                print "samuel: (error msg):",e
                continue
        sp = bs(response.read())
        jre = re.compile(r""" 
                [(document.write)]
                (.)*
                ('><span)
                """,re.VERBOSE) 
        if not os.path.exists(self.path):   # create vol folder
            os.makedirs(self.path)
        page_count = 1                      # set the prefix of the vol
        imgo = urllib.URLopener() 
        n_url = url
        while 1:
            img_link = self.get_img_link(sp,jre)
            try:
                image = kkdm_img(img_link,self.path, page_count)
            except Exception, e:
                print e,
                print ", Changing the prefix ..."
                self.pfx = self.chgpfx()
                continue
            self.img.append(image)
            n_url = self.get_np_link(sp)
            if n_url == "http://comic.kukudm.com/exit/exit.htm":
                break
            page_count += 1                                              
            req= urllib2.Request(n_url, None, kkdm_vol.hder)
            while 1:
                try:
                    response = urllib2.urlopen(req)
                    break
                except urllib2.URLError, e:
                    print "samuel: (error msg):",e
                    continue
            sp = bs(response.read())
            
    def chgpfx(self):
        for i in range(len(PREFIX_LST)):
            if self.pfx == PREFIX_LST[i]:
                break;
        return '%s' % PREFIX_LST[((i+1)%len(PREFIX_LST))]

    def get_img_link(self,esp,ere):
        jimg = esp.body('table')[1]('td')[0]('script')[0]
        jimgidx = ere.finditer(str(jimg))
        for out in jimgidx:
            haha = out.group() 
            img_sublink = haha.split('"')[3].split("'")[0]
        # get the key sub-url
        img_sublink = urllib.quote(img_sublink)                           
        img_link = self.pfx + img_sublink
        return '%s' % img_link

    def get_np_link(self,esp):
        lenofidx =  len(esp.findAll('a'))
        nextimg_sublink = esp.findAll('a')[lenofidx - 1]['href']
        n_url = PREFIX_WEBSITE + nextimg_sublink
        return '%s' % n_url

class kkdm_comic(object):
    """kukudm comic index"""
    global BROWSER_UA
    vol = []
    comic_list = {}
    hder = {'User-Agent': BROWSER_UA, 'Referer': WEBSITE}

    # initial
    def __init__(self, comic='', vols=[]):
        if comic != '':
            self.comic = comic                         # set comic name
            self.comic_url = self.get_book_url(comic)  # set comci url
            comic_path = TMP_FOLDER + self.comic       # set dl folder
            req= urllib2.Request(self.comic_url, None, kkdm_comic.hder)
            if len(vols) == 0:
                response = urllib2.urlopen(req)
                sp = bs(response.read())
                r_table = sp.body('table')[8]('dd')             
                nvol = str(len(r_table))
                vols.append(nvol)
            for ci in vols:
                c_url = self.get_vol_url(self.comic_url, int(ci))
                self.vol.append(kkdm_vol(c_url, comic_path, int(ci)))
                self.zipit(int(ci))

    def get_book_url(self, cname):
        """get url of the comic"""
        self.comic_list['red']         = '514'
        self.comic_list['rome']        = '975'
        self.comic_list['naruto']      = '3'
        self.comic_list['onepiece']    = '4'
        self.comic_list['firephoenix'] = '277'
        self.comic_list['real']        = '168'
        self.comic_list['prison']      = '1087'
        self.comic_list['tooth']       = '1167'
        self.comic_list['godnote']     = '914'
        self.comic_list['flower']      = '1172'
        self.comic_list['wrc']         = '789'
        #error handle not be done.
        rtn = "http://comic.kukudm.com/comiclist/" \
            + self.comic_list[cname] \
            + "/index.htm"
        return '%s' % rtn

    def get_vol_url(self, url, vol):
        req = urllib2.Request(url, None, kkdm_comic.hder)
        while 1:
            try:
                response = urllib2.urlopen(req)
                break
            except urllib2.URLError, e:
                print "samuel: (error msg):",e
                continue
        sp = bs(response.read())

        r_table = sp.body('table')[8]('dd')               # round table
        # try all mirro site
        for mi in [1,2,3,4]:
            try:
                c_url = r_table[vol - 1]('a')[mi]['href'] #(1-4) is ok
                opstr =  "Comic Vol(" + str(vol) + "):"\
                         + r_table[vol - 1]('a')[0].string
                print opstr
                break
            except:
                print "Error: vol mirror (%d/4)error" % mi
                continue
        return '%s' % c_url

    def zipit(self,volname):
        volname = str(volname).rjust(3,'0') 
        zfname  = self.comic + '-' + volname + '.zip'
        if os.path.exists(zfname):
            return
        oldpath = os.getcwd()
        newpath = TMP_FOLDER + self.comic + '/' + volname
        zf = zipfile.ZipFile(zfname, mode='w') 
        os.chdir(newpath)
        imgfiles = os.listdir('./')
        imgfiles.reverse()
        for i in imgfiles:
            zf.write(i)
        zf.close()
        os.chdir(oldpath)
        img = os.listdir('./')
        print "Comic ZIP File: %s saved." % zfname
        return 

    def update100(self,num=10,comic=0):
        url = 'http://comic.kukudm.com/top100.htm'
        req= urllib2.Request(url, None, kkdm_comic.hder)
        response = urllib2.urlopen(req)
        sp = bs(response.read())
        for i in range(0,num):
            print sp.body('dd')[i]('a')[1].string  # name
        if comic != 0:
            print "comic not 0"
            return '%s' % sp.body('table')[9]('a')  # url and bookface

def main():
    howto = '%prog [-c comic|-u][option] arg1 arg2 ...\n\
      \n\tRange vols download:  \t %prog -c <comic> -s <start volnum> -e <end volnum>\
      \n\tDivided vol download: \t %prog -c <comic> -d <volnum> [<volnums>]\
      \n\tLastest vol download: \t %prog -c <comic> -l \
      \n\tShow Lastest Update:  \t %prog -u [default counts=10]'

    aprs = OptionParser(usage=howto, version="%prog beta2.1")
    aprs.add_option("-c", "--comic", dest="comic", 
            help="indicate which comic ..")
    aprs.add_option("-s", "--start", type="int", dest="start", 
            help="vol start from ..")
    aprs.add_option("-e", "--end", type="int", dest="end", 
            help="vol end from ..")
    aprs.add_option("-d", action="store_true", dest="divided", 
            default=False, help="devided download ..")
    aprs.add_option("-l", action="store_true", dest="latest",  
            default=False, help="latest vol ..")
    aprs.add_option("-u", action="store_true", dest="update",  
            default=False, help="list latest 100 updates ..")
    opts, args = aprs.parse_args()
    opts = opts.__dict__

    if opts["update"]:
        if len(args) == 0: 
            kkdm_comic().update100()
        else:
            kkdm_comic().update100(int(args[0]))
    else:
        cleanup()
        if opts["divided"]:
            x = kkdm_comic(opts["comic"],args)
        elif opts["latest"]:
            x = kkdm_comic(opts["comic"])
        else:
            x = kkdm_comic(opts["comic"], range(opts["start"], 
                        opts["end"] + 1))
    shutil.rmtree(TMP_FOLDER)

if __name__ == '__main__':
    main()

#  vim:fdm=indent
