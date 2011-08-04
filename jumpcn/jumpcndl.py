#!/usr/bin/env python

import os,re,sys,string,time
import urllib,urllib2
import tarfile,zipfile
import tempfile
import shutil
from optparse import OptionParser, OptionGroup
from BeautifulSoup import BeautifulSoup as bs

TMPFOLDERPFX = 'jumpcn_'
TMP_FOLDER = tempfile.mkdtemp(prefix=TMPFOLDERPFX) + '/'
REAL_IMG_SRC_LIST = list()
REAL_IMG_SRC_LIST.append('http://www.daoshu.net/pcomic_com_cn/')
#REAL_IMG_SRC_LIST.append('http://ascrsbdtdb.kukudm.net:82/')
#REAL_IMG_SRC_LIST.append('http://ascrsbdfdb.kukudm.net:81/')
#REAL_IMG_SRC_LIST.append('http://dx.kukudm.net/')
BROWSER_UA = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.10 \
              (KHTML, like Gecko) Chrome/8.0.552.237 Safari/534.10'

PREFIX_WEBSITE = 'http://www.jumpcn.com.cn/comic/'
WEBSITE = 'http://www.jumpcn.com.cn/'

CLEAR_FLD = list()

def cleanup():
    '''cleanup the temp folder ever used'''
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
    """download kukudm img"""
    def __init__(self, url, path, page):
        self.url   = url
        subname    = url.split('/')[-1].split('.')[-1] 
        self.fname = path + '/' + str(page).rjust(3,'0') + '.' + subname
        if (not os.path.exists(self.fname))or(os.path.getsize(self.fname) < 600):
            print "retrieving the comic: %s" % self.fname
            self.dl()

    def dl(self):
        img = urllib.URLopener()
        while 1: 
            try:
                print "downloading ... %s" % self.url 
                img.retrieve(self.url, self.fname)
                if os.path.getsize(self.fname) < 600:
                    continue
                else:
                    break
            except IOError, e:
                if e[1] != 404:
                    print "Warning: Retrieve %s Error.\ntime.sleep(5) and again" %self.url
                    time.sleep(9)
                    continue

class kkdm_vol(object):
    """kukudm vol"""
    global REAL_IMG_SRC_LIST
    global BROWSER_UA
    img  = list()
    hder = {'User-Agent': BROWSER_UA, 'Referer': WEBSITE}
    def __init__(self, url, path, vol):
        self.url  = url
        self.vol  = str(vol)
        self.path = path + '/' + str(vol).rjust(3,'0') 

        print self.url
        # vol home page
        req = urllib2.Request(url, None, kkdm_vol.hder)
        # req2 to retrive the index.js to get the vol pages
        req2= urllib2.Request(self.url+'index.js', None, kkdm_vol.hder)

        while 1:
            try:
                response = urllib2.urlopen(req)
                response2 = urllib2.urlopen(req2)
                break
            except urllib2.URLError, e:
                print "samuel: (error msg):",e
                continue

        sp = bs(response.read())

        v_info = response2.read()
        print v_info
        self.totalpages = re.search('(total=*)(\d)*',v_info).group().split('=')[1]
        self.sublink = re.search('(volpic=)(.*\')',v_info).group().split('\'')[1].decode('gb2312').encode('utf8')
        self.sublink = urllib.quote(self.sublink) 

        # create vol folder
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        # set the prefix of the vol
        page_count = 1


        for page_count in range(int(self.totalpages)):
            img_url = REAL_IMG_SRC_LIST[0] + self.sublink + str(page_count + 1) + '.jpg'
            while True:
                try: 
                    image = kkdm_img(img_url,self.path, page_count + 1) 
                except Exception, e:
                    print e
                    print ',(samuel): something wrong here'
                    continue
                self.img.append(image) 
                break;

class kkdm_comic(object):
    """kukudm comic index"""
    global BROWSER_UA
    vol = list()
    comic_list = dict() 
    hder = {'User-Agent': BROWSER_UA, 'Referer': WEBSITE}

    # initial
    def __init__(self, comic='', vols=[]):
        if comic != '':
            self.comic = comic                           # set comic name
            self.comic_url = self.get_book_url(comic)    # set comci url
            comic_path = TMP_FOLDER + self.comic         # set download folder
            req = urllib2.Request(self.comic_url, None, kkdm_comic.hder)
            if len(vols) == 0:
                '''donwload for the lastest vol'''
                while True:
                    try:
                        response = urllib2.urlopen(req)
                        break
                    except urllib2.URLError, e:
                        print "samuel: (error msg):",e
                        continue
                sp = bs(response.read())
                #sp = bs(urllib2.urlopen(self.comic_url).read())            

                r_table = sp.find('div',{'id':'subBookList'}) ('li') 
                r_table.reverse()

                nvol = str(len(r_table))
                vols.append(nvol)
            for ci in vols:
                c_url = self.get_vol_url(self.comic_url, int(ci))
                self.vol.append(kkdm_vol(c_url, comic_path, int(ci)))
                self.zipit(int(ci))
    # get url of the comic
    def get_book_url(self, cname):
        self.comic_list['sisstrange'] = '2458'
        return '%s' % PREFIX_WEBSITE + self.comic_list[cname]

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

        r_table = sp.find('div',{'id':'subBookList'}) ('li') 
        r_table.reverse()

        #print volname of the download process
        c_url = str(url + '/' + r_table[vol-1]('a')[0]['href']) 
        opstr = r_table[vol-1]('a')[0].string
        print opstr
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

def main():
    howto = '%prog [-c comic|-u][option] arg1 arg2 ...\n\
      \n\tRange vol download:   \t %prog -c <comic> -s <start vol> -e <end vol> \
      \n\tDivided vol download: \t %prog -c <comic> -d vol1 [vol2 [vol3..] ] \
      \n\tLastest vol download: \t %prog -c <comic> -l \
      \n\tShow Lastest Update:  \t %prog -u [default counts=10]'

    aprs = OptionParser(usage=howto, version="%prog beta2.1")
    aprs.add_option("-c", "--comic", dest="comic",
                    help="indicate which comic ..")
    aprs.add_option("-s", "--start", type="int", dest="start",
                    help="vol start from ..")
    aprs.add_option("-e", "--end", type="int", dest="end",
                    help="vol end from ..")
    aprs.add_option("-d", action="store_true", dest="divided", default=False, 
                    help="devided download ..")
    aprs.add_option("-l", action="store_true", dest="latest",  default=False, 
                    help="latest vol ..")
    aprs.add_option("-u", action="store_true", dest="update",  default=False, 
                    help="list latest 100 updates ..")
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
