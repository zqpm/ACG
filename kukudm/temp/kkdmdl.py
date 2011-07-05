#!/usr/bin/env python

import os,re,sys,string,time
import urllib,urllib2
import tarfile,zipfile
from optparse import OptionParser, OptionGroup
from BeautifulSoup import BeautifulSoup as bs

TMP_FOLDER = '/dev/shm/'
PREFIX_LST = []
PREFIX_LST.append("http://ascrsbdtdb.kukudm.net:82/")
PREFIX_LST.append("http://ascrsbdfdb.kukudm.net:81/")
PREFIX_LST.append("http://dx.kukudm.net/")
BROWSER_UA = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.10 \
              (KHTML, like Gecko) Chrome/8.0.552.237 Safari/534.10'
                
#PREFIX_LST.append("")

PREFIX_WEBSITE = "http://comic.kukudm.com"

class kkdm_img:
    """kukudm img"""
    url   = ''
    fname = ''
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
    #def __del__(self):
    #    print "remove img: %s" % self.fname
    #    if os.path.exists(self.fname):
    #        os.remove(self.fname)

class kkdm_vol:
    """kukudm vol page"""
    global PREFIX_LST
    global BROWSER_UA
    url  = ''
    path = ''
    vol  = str()
    pfx  = ''
    img  = []
    hder = {'User-Agent': BROWSER_UA, 'Referer': 'http://kukudm.com/'}
    def __init__(self, url, path, vol):
        self.url  = url
        self.vol  = str(vol)
        self.pfx  = self.chgpfx()
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
        #sp  = bs(urllib2.urlopen(url).read()) # non header version

        jre = re.compile(r""" 
                [(document.write)]
                (.)*
                ('><span)
                """,re.VERBOSE) 
        # create vol folder
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        # set the prefix of the vol
        page_count = 1
        imgo = urllib.URLopener() 

        n_url = url
        while True:
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
            #sp = bs(urllib2.urlopen(n_url).read())
            
    def chgpfx(self):
        if self.pfx == '':
            return PREFIX_LST[0]
        else :
            for i in range(len(PREFIX_LST)):
                if self.pfx == PREFIX_LST[i]:
                    break;
            return PREFIX_LST[((i+1)%len(PREFIX_LST))]
    def get_img_link(self,esp,ere):
        jimg = esp.body('table')[1]('td')[0]('script')[0]
        jimgidx = ere.finditer(str(jimg))
        for out in jimgidx:
            haha = out.group() 
            img_sublink = haha.split('"')[3].split("'")[0]
        # get the key sub-url
        img_sublink = urllib.quote(img_sublink)                           
        img_link = self.pfx + img_sublink
        return img_link
    def get_np_link(self,esp):
        lenofidx =  len(esp.findAll('a'))
        nextimg_sublink = esp.findAll('a')[lenofidx - 1]['href']
        n_url = PREFIX_WEBSITE + nextimg_sublink
        return n_url
    #def __del__(self):
    #    print "removing vol dir: %s" % self.path
    #    if os.path.exists(self.path):
    #        os.removedirs(self.path) 

class kkdm_comic:
    """kukudm comic index"""
    global BROWSER_UA
    comic = ''
    comic_url = ''
    comic_path = ''
    vol = []
    comic_list = {}  
    hder = {'User-Agent': BROWSER_UA, 'Referer': 'http://kukudm.com/'}

    # initial
    def __init__(self, comic='', vols=[]):
        if comic != '':
            self.comic = comic                           # set comic name
            self.comic_url = self.get_book_url(comic)    # set comci url
            comic_patz = TMP_FOLDER + self.comic         # set download folder
            req= urllib2.Request(self.comic_url, None, kkdm_comic.hder)
            if len(vols) == 0:
                response = urllib2.urlopen(req)
                sp = bs(response.read())
                #sp = bs(urllib2.urlopen(self.comic_url).read())            

                r_table = sp.body('table')[8]('dd')             
                nvol = str(len(r_table))
                vols.append(nvol)
            for ci in vols:
                c_url = self.get_vol_url(self.comic_url, int(ci))
                self.vol.append(kkdm_vol(c_url, comic_patz, int(ci)))
                self.zipit(int(ci))
    # get url of the comic
    def get_book_url(self, cname):
        self.comic_list['red']      = '514'
        self.comic_list['rome']     = '975'
        self.comic_list['naruto']   = '3'
        self.comic_list['onepiece'] = '4'
        self.comic_list['firephoenix'] = '277'
        self.comic_list['real'] = '168'
        self.comic_list['prison'] = '1087'
        self.comic_list['tooth'] = '1167'
        self.comic_list['godnote'] = '914'
        self.comic_list['flower'] = '1172'
        #error handle not be done.
        rtn = "http://comic.kukudm.com/comiclist/" + self.comic_list[cname] +\
               "/index.htm"
        return rtn
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
        #sp = bs(urllib2.urlopen(url).read())

        r_table = sp.body('table')[8]('dd')                 # round table
        # try all mirro site
        for mi in [1,2,3,4]:
            try:
                c_url = r_table[vol - 1]('a')[mi]['href']   # (1,2,3,4) are available
                opstr =  "Comic Vol(" + str(vol) + "):" + \
                          r_table[vol - 1]('a')[0].string
                print opstr
                break
            except:
                print "Error: vol mirror (%d/4)error" % mi
                continue
        return c_url
    def zipit(self,volname):
        volname = str(volname).rjust(3,'0') 
        zfname = volname + '.zip'
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
        #sp = bs(urllib2.urlopen(url).read())

        for i in range(0,num):
            print sp.body('dd')[i]('a')[1].string                    # name
        if comic != 0:
            print "comic not 0"
            return sp.body('table')[9]('a')  # url and bookface

    #def __del__(self):
    #    if self.comic == '':
    #        return
    #    print "remove comic folder: %s" %self.comic_path
    #    if os.path.exists(self.comic_path):
    #        os.removedirs(self.comic_path)


def main():
    howto = '%prog [-c comic|-u][option] arg1 arg2 ...\n\n\
      \nRange vol download: \n\t %prog -c <comic> -s <start vol> -e <end vol> \
      \nDivided vol download: \n\t %prog -c <comic> -d vol1 [vol2 [vol3..] ] \
      \nLastest vol download: \n\t %prog -c <comic> -l \
      \nShow Lastest Update: \n\t %prog -u [counts=10]'

    aprs = OptionParser(usage=howto, version="%prog b1.1")
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
        if opts["divided"]:
            x = kkdm_comic(opts["comic"],args)
        elif not opts["divided"]:
            if opts["latest"]:
                x = kkdm_comic(opts["comic"])
            else:
                x = kkdm_comic(opts["comic"], range(opts["start"], 
                               opts["end"] + 1))

if __name__ == '__main__':
    main()

#  vim:fdm=indent
