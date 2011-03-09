#!/usr/bin/env python

import os,re,sys,string,time
import urllib,urllib2
import tarfile,zipfile
from optparse import OptionParser, OptionGroup
from BeautifulSoup import BeautifulSoup as bs

TMP_FOLDER = '/dev/shm/'
PREFIX_IMG1 = "http://ascrsbdtdb.kukudm.net:82/"
PREFIX_IMG2 = "http://ascrsbdfdb.kukudm.net:81/"

PREFIX_WEBSITE = "http://comic.kukudm.com"

class kkdm_img:
    """kukudm img"""
    url   = ''
    fname = ''
    def __init__(self, url, path, page):
        self.url   = url
        subname    = url.split('/')[-1].split('.')[-1] 
        self.fname = path + '/' + str(page).rjust(3,'0') + '.' + subname
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
                    img.retrieve(self.url, self.fname)
                raise RuntimeError("404, prefix problem") 
    def __del__(self):
        print "remove img: %s" % self.fname
        if os.path.exists(self.fname):
            os.remove(self.fname)

class kkdm_vol:
    """kukudm vol page"""
    global PREFIX_IMG1
    global PREFIX_IMG2
    url  = ''
    path = ''
    vol  = str()
    pfx  = ''
    img  = []
    def __init__(self, url, path, vol):
        self.url  = url
        self.vol  = str(vol)
        self.pfx  = self.chgpfx()
        self.path = path + '/' + str(vol).rjust(3,'0') 
        # init local variable
        sp  = bs(urllib2.urlopen(url).read())
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
            except RuntimeError, e:
                print e
                print "Changing the prefix ..."
                self.pfx = self.chgpfx()
                continue

            self.img.append(image)
            n_url = self.get_np_link(sp)
            if n_url == "http://comic.kukudm.com/exit/exit.htm":
                break

            page_count += 1                                              
            sp          = bs(urllib2.urlopen(n_url).read())
    def chgpfx(self):
        pfxlist = [PREFIX_IMG1, PREFIX_IMG2]
        if self.pfx == '':
            return pfxlist[0]
        else :
            for i in range(len(pfxlist)):
                if self.pfx != pfxlist[i]:
                    continue
                return pfxlist[((i+1)%len(pfxlist))]
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
    def __del__(self):
        print "removing vol dir: %s" % self.path
        if os.path.exists(self.path):
            os.removedirs(self.path) 

class kkdm_comic:
    """kukudm comic index"""
    comic = ''
    comic_url = ''
    comic_path = ''
    vol = []
    def __init__(self,comic='',vols=[]):
        if comic != '':
            self.comic = comic
            self.comic_url = self.get_book_url(comic)
            comic_path = TMP_FOLDER + comic
            for ci in vols:
                curl = self.get_vol_url(self.comic_url,int(ci))
                self.vol.append(kkdm_vol(curl,comic_path,int(ci)))
                self.zipit(int(ci))

    def get_book_url(self, cname):
        if cname == "red":
            return  "http://comic.kukudm.com/comiclist/514/index.htm"  #red
        elif cname == "town":
            return  "http://comic.kukudm.com/comiclist/672/index.htm"  #town 
        elif cname == "wolf":
            return  "http://comic.kukudm.com/comiclist/536/index.htm"  #wolf
        elif cname == "flysky":
            return "http://comic.kukudm.com/comiclist/1005/index.htm"  #flysky
        elif cname == "rome":
            return "http://comic.kukudm.com/comiclist/975/index.htm"   #rome
        elif cname == "mathgirl":
            return "http://comic.kukudm.com/comiclist/997/index.htm"   #mathgirl
        else:
            print "kkdmdl doest not support %s" % cname
            sys.exit(0)
    def get_vol_url(self, url, vol):
        sp = bs(urllib2.urlopen(url).read())                # need time
        r_table = sp.body('table')[8]('dd')                 # round table
        for mi in [1,2,3,4]:
            try:
                c_url = r_table[vol - 1]('a')[mi]['href']   # (1,2,3,4) are available
                print "Comic Vol: %s" % r_table[vol - 1]('a')[0].string
                break
            except:
                print "Error: vol mirror (%d/4)error" % mi
                continue
        return c_url
    def zipit(self,zname):
    # use console command 'zip' to zip files
        zname = str(zname).rjust(3,'0') 
        zfname = zname + '.zip'
        command = 'zip -jq %(s1)s %(s2)s%(s3)s/%(s4)s/*' % {"s1":zfname ,"s2":TMP_FOLDER, "s3":self.comic , "s4":zname}
        #print command
        try:
            os.system(command)
            print "Comic ZIP File: %s saved." % zfname
        except Exception, e:
            print e
            print "Error: zip fail!"
        return 
    def update100(self,num=10,comic=0):
        html = urllib2.urlopen('http://comic.kukudm.com/top100.htm')
        soup = bs(html.read())

        for i in range(0,num):
            print soup.body('dd')[i]('a')[1].string                    # name
        if comic != 0:
            print "comic not 0"
            return soup.body('table')[9]('a')  # url and bookface
            #return soup.body('table')[9]('a')[2*(comic-1)+1].string  # url and bookface

    def __del__(self):
        if self.comic == '':
            return
        print "remove comic folder: %s" %self.comic_path
        if os.path.exists(self.comic_path):
            os.removedirs(self.comic_path)


def main():
    aprs = OptionParser("%prog [option] arg1 arg2 ...", version="%prog v0.1")
    aprs.add_option("-c", "--comic",             dest="comic",     help="indicate which comic ..")
    aprs.add_option("-s", "--start", type="int", dest="start",     help="vol start from ..")
    aprs.add_option("-e", "--end", type="int",   dest="end",       help="vol end from ..")
    aprs.add_option("-d", action="store_true",   dest="divided", default=False, help="devided download ..")
    aprs.add_option("-l", action="store_true",   dest="latest",  default=False, help="latest vol ..")
    aprs.add_option("-u", action="store_true",   dest="update",  default=False, help="list latest 100 updates ..")
    opts, args = aprs.parse_args()
    opts = opts.__dict__

    if opts["update"] == True:
        kkdm_comic().update100(int(args[0]))
    else:
        if opts["divided"] == True:
            x = kkdm_comic(opts["comic"],args)
        elif opts["divided"] == False:
            x = kkdm_comic(opts["comic"],range(opts["start"], opts["end"] + 1))

if __name__ == '__main__':
    main()

#  vim:fdm=indent
