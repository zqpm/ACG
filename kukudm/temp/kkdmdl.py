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
    #def __del__(self):
    #    print "remove img: %s" % self.fname
    #    if os.path.exists(self.fname):
    #        os.remove(self.fname)

class kkdm_vol:
    """kukudm vol page"""
    global PREFIX_LST
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
    comic = ''
    comic_url = ''
    comic_path = ''
    vol = []
    comic_list = {}  
    # initial
    def __init__(self,comic='',vols=[]):
        if comic != '':
            self.comic = comic                           # set comic name
            self.comic_url = self.get_book_url(comic)    # set comci url
            comic_path = TMP_FOLDER + self.comic         # set download folder
            if len(vols) == 0:
                sp = bs(urllib2.urlopen(self.comic_url).read())            
                r_table = sp.body('table')[8]('dd')             
                nvol = str(len(r_table))
                vols.append(nvol)
            for ci in vols:
                c_url = self.get_vol_url(self.comic_url,int(ci))
                self.vol.append(kkdm_vol(c_url,comic_path,int(ci)))
                self.zipit(int(ci))
    # get url of the comic
    def get_book_url(self, cname):
        self.comic_list['red']      = '514'
        self.comic_list['town']     = '672'
        self.comic_list['wolf']     = '536'
        self.comic_list['flysky']   = '1005'
        self.comic_list['rome']     = '975'
        self.comic_list['mathgirl'] = '997'
        self.comic_list['naruto']   = '3'
        self.comic_list['onepiece'] = '4'
        #error handle not be done.
        rtn = "http://comic.kukudm.com/comiclist/" + self.comic_list[cname] +\
               "/index.htm"
        return rtn
    def get_vol_url(self, url, vol):
        sp = bs(urllib2.urlopen(url).read())                # need time
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
    #def __del__(self):
    #    if self.comic == '':
    #        return
    #    print "remove comic folder: %s" %self.comic_path
    #    if os.path.exists(self.comic_path):
    #        os.removedirs(self.comic_path)


def main():
    aprs = OptionParser("%prog [option] arg1 arg2 ...", version="%prog v0.1")
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

    if opts["update"] == True:
        kkdm_comic().update100(int(args[0]))
    else:
        if opts["divided"] == True:
            x = kkdm_comic(opts["comic"],args)
        elif opts["divided"] == False:
            if opts["latest"] == False:
                x = kkdm_comic(opts["comic"], range(opts["start"], 
                               opts["end"] + 1))
            else:
                x = kkdm_comic(opts["comic"])

if __name__ == '__main__':
    main()

#  vim:fdm=indent
