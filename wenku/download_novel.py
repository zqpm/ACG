#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('./')
from wenku8 import wenku8
from optparse import OptionParser, OptionGroup

def main():
    aprs = OptionParser("%prog [option] arg1 arg2 ...", version="%prog v0.1")
    aprs.add_option('-n', '--novel', dest='novel', help='indicate which novel ..')
    aprs.add_option("-u", action="store_true", dest="update",  default=False, help="list latest 100 updates ..")
    opts, args = aprs.parse_args()
    opts = opts.__dict__

    if opts['update'] == True:
        pass
    else:
        a = wenku8(opts['novel'],'big5')
        a.download([2,3])

if __name__ == '__main__':
    main()
