#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb
import os,re,sys,string,time
import urllib,urllib2
from BeautifulSoup import BeautifulSoup as bs
import tarfile
#import argparse
from optparse import OptionParser, OptionGroup


PREFIX_IMG_OK = ''
PREFIX_IMG_SET  = 0
PREFIX_IMG1 = "http://ascrsbdtdb.kukudm.net:82/"
PREFIX_IMG2 = "http://ascrsbdfdb.kukudm.net:81/"

PREFIX_WEBSITE = "http://comic.kukudm.com"

COMIC_RT = ''

def update100(num=10,comic=0):
    html = urllib2.urlopen('http://comic.kukudm.com/top100.htm')
    soup = bs(html.read())

    for i in range(0,num):
        print soup.body('table')[9]('a')[2*i+1].string  # name
    if comic != 0:
        return soup.body('table')[9]('a')[2*(comic-1)+1].string # url/bookface


def kkdmdl_dlimg(suburl,name):
    #
    # Download img from given img url
    #
    global PREFIX_IMG_OK                       # use global value
    global PREFIX_IMG_SET 

    img = urllib.URLopener() 

    if PREFIX_IMG_SET == 0:
        for ppp in [PREFIX_IMG1, PREFIX_IMG2]: # choose the correct img url 
            img_link = ppp + suburl            # in PREFIX_* database 
            try:
                img.retrieve(img_link, name)
                PREFIX_IMG_OK = ppp
                PREFIX_IMG_SET = 1
                break
            # url error
            except IOError, e:
                if e[1] == 404:
                    print "Warning: URL Error(404) with prefix:\n%s" % ppp
                    continue

    img_link = PREFIX_IMG_OK + suburl

    #debug
    #print "Download ... %s" % img_link

    while (1):                                 # download img
        try:                                   # check if fake file(size<500)
            img.retrieve(img_link, name)
            if os.path.getsize(name) < 500:
                continue
            else:
                break
        except IOError, e:
            print "Warning: Retrived %s error \nsleep(5) and do it again" \
                   % img_link
            time.sleep(5)
            img.retrieve(img_link, name)
    #debug
    #print "%s Saved" % name
    return

def getbooklist(rdidx, url):
    # 
    # Return the url of book vol.
    #
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
          
    req = urllib2.Request(url)
    req.add_header('User-Agent', user_agent )
    response = urllib2.urlopen(req)

    # coding issue
    html = response.read() #.encode('gbk')#.encode('utf-8')
    soup = bs(html) 

    r_table = soup.body('table')[8]('dd')            # round table
                                                     # comic url
                                                     # 1 means:
    try:                                             #  use no.2 mirror site
        c_url = r_table[rdidx - 1]('a')[1]['href']   # (1,2,3,4) are available
        print "Comic Vol: ", r_table[rdidx -1]('a')[0].string
    except:
        print "Error: vol error"
        sys.exit(2)


    return c_url

def dlimg(c_url,fdr,fnm):
    # 
    # Download img from the result of the getbooklist()
    #
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
          
    req = urllib2.Request(c_url) 
    req.add_header('User-Agent', user_agent )
    response = urllib2.urlopen(req)

    c_html = response.read() #.encode('gbk') #.encode('utf-8')
    c_soup = bs(c_html)

    # parse source
    # parse the img url from 
    # java script
    # jimg: containing the a java stript code with a img url
    jimg = c_soup.body('table')[1]('td')[0]('script')[0]        
    jimg_re = re.compile(r""" 
            [(document.write)]
            (.)*
            ('><span)
            """,re.VERBOSE) 
    jimgidx = jimg_re.finditer(str(jimg))
    for out in jimgidx:
        haha = out.group() 
        img_sublink = haha.split('"')[3].split("'")[0]
    img_sublink = urllib.quote(img_sublink)             # get the key-url              

    # prepare the filename for saving
    subname = img_sublink.split('/')[-1].split('.')[-1] 
    tgtname = fnm + '.' + subname

    # create folder and download the image
    fdr = '/dev/shm/' + fdr
    if not os.path.exists(fdr):
        os.makedirs(fdr) 
    kkdmdl_dlimg(img_sublink,fdr + '/' + tgtname)

    # return url for next comic img
    lenofidx =  len(c_soup.findAll('a'))
    nextimg_sublink = c_soup.findAll('a')[lenofidx - 1]['href']
    nextimg_link = PREFIX_WEBSITE + nextimg_sublink
    return nextimg_link

def tbz2it(tname):
    # use tarfile module to tbz2 files
    tfname = tname + ".tbz2"
    tar = tarfile.open(tfname, "w:bz2") 
    for name in [tname]:
        tar.add(name)
    tar.close()
    return

def zipit(zname):
    # use console command 'zip' to zip files
    zfname = zname + '.zip'
    command = 'zip -q %(s1)s /dev/shm/%(s2)s/*' % {"s1":zfname ,"s2":zname}
    os.system(command)
    print "Comic ZIP File: %s saved." % zfname
    return 
def kkdmdl_dltop(comic):
    #
    # download latest update comic
    # {{{

    print "kkdmdl_dltop"

    # }}}

def kkdmdl_dlvol(args):
    # 
    # download a vol, from the list: args
    # {{{
    global COMIC_RT
    global PREFIX_IMG_SET 

    for i in args: 
        url        = getbooklist(int(i), COMIC_RT)# url of current comic page 
        n_url      = url                          # url of next comic page
                                                                               
        page_count = 1                            # page count
        filename   = str(page_count)              # setting the filename
        filename   = filename.rjust(3,'0')        # fill with '0' in 3 digits
        vol        = str(i).rjust(3,'0')
                                                                                    
        while ( n_url != "http://comic.kukudm.com/exit/exit.htm" ):
            n_url = dlimg(n_url,vol,filename)
            page_count += 1
            filename = str(page_count)
            filename = filename.rjust(3,'0')    
        
        zipit(vol)                                     # zip it
        command ='rm -rf /dev/shm/%s' % vol            # then remove
        if os.system(command) == 0:
            print "tmp folder /dev/shm/%s Removed" % vol
        PREFIX_IMG_SET = 0

    return 
    # }}}

def kkdmdl_selrt(ar):
    #
    # return the COMIC url, from teh argument: ar
    # {{{
    global COMIC_RT

    if ar == "red":
        return  "http://comic.kukudm.com/comiclist/514/index.htm"  #red
    elif ar == "town":
        return  "http://comic.kukudm.com/comiclist/672/index.htm"  #town 
    elif ar == "wolf":
        return  "http://comic.kukudm.com/comiclist/536/index.htm"  #wolf
    elif ar == "flysky":
        return "http://comic.kukudm.com/comiclist/1005/index.htm" #flysky
    else:
        print "kukudmdl doest not support %s" % opts["comic"]
        sys.exit(0)
    # }}}


def main():
    global COMIC_RT
    global PREFIX_IMG_SET 

    aprs = OptionParser("%prog [option] arg1 arg2 ...", version="%prog v0.1")

    aprs.add_option("-c", "--comic", dest="comic", help="indicate comic ..")
    aprs.add_option("-s", "--start", type="int", dest="start", \
                    help="vol start from ..")
    aprs.add_option("-e", "--end", type="int", dest="end", \
                    help="vol end from ..")
    aprs.add_option("-d", action="store_true", dest="divided", default=False,\
                    help="devided download ..")
    aprs.add_option("-u", action="store_true", dest="update", default=False, \
                    help="list latest 100 updates ..")

    opts, args = aprs.parse_args()
    opts = opts.__dict__

    if opts["update"] == True:
        topn = int(args[0])
        print update100(topn, 0)
        sys.exit(0)

    COMIC_RT = kkdmdl_selrt(opts["comic"])

    if opts["divided"] == True:
        kkdmdl_dlvol(args)
    elif opts["divided"] == False:
        kkdmdl_dlvol(range(opts["start"], opts["end"] + 1))



    return




if __name__ == '__main__':
    main()

#  vim:fdm=marker
