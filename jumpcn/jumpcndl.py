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
#PREFIX_LST = list()
#PREFIX_LST.append('http://ascrsbdtdb.kukudm.net:82/')
#PREFIX_LST.append('http://ascrsbdfdb.kukudm.net:81/')
#PREFIX_LST.append('http://dx.kukudm.net/')
BROWSER_UA = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.10 \
              (KHTML, like Gecko) Chrome/8.0.552.237 Safari/534.10'

PREFIX_WEBSITE = 'http://www.jumpcn.com.cn/comic/'
WEBSITE = 'http://www.jumpcn.com.cn'

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
        if (not os.path.exists(self.fname))or(os.path.getsize(self.fname) < 500):
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
                    print "Warning: Retrieve %s Error.\ntime.sleep(5) and again" %self.url
                    time.sleep(5)
                    #img.retrieve(self.url, self.fname)
                    continue
                raise RuntimeError("404, prefix problem") 

class kkdm_vol(object):
    """kukudm vol"""
    #global PREFIX_LST
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
        self.sublink = re.search('(volpic=)(.*\')',v_info).group().split('\'')[1]

        # create vol folder
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        # set the prefix of the vol
        page_count = 1
        imgo = urllib.URLopener() 
        n_url = url


        for page_count in range(int(self.totalpages)):
            img_url = self.url + self.sublink + str(page_count+1) + '.jpg'
            while True:
                try: 
                    image = kkdm_img(img_url,self.path, page_count) 
                except Exception, e:
                    print e
                    print ',(samuel): something wrong here'
                    continue
                self.img.append(image) 
                break;
            
#    def chgpfx(self):
#        for i in range(len(PREFIX_LST)):
#            if self.pfx == PREFIX_LST[i]:
#                break;
#        return '%s' % PREFIX_LST[((i+1)%len(PREFIX_LST))]
#    def get_img_link(self,esp,ere):
#        jimg = esp.body('table')[1]('td')[0]('script')[0]
#        jimgidx = ere.finditer(str(jimg))
#        for out in jimgidx:
#            haha = out.group() 
#            img_sublink = haha.split('"')[3].split("'")[0]
#        # get the key sub-url
#        img_sublink = urllib.quote(img_sublink)                           
#        img_link = self.pfx + img_sublink
#        return '%s' % img_link
#
#    def get_np_link(self,esp):
#        lenofidx =  len(esp.findAll('a'))
#        nextimg_sublink = esp.findAll('a')[lenofidx - 1]['href']
#        n_url = PREFIX_WEBSITE + nextimg_sublink
#        return '%s' % n_url

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
