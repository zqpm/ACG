#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sfacg3g import sfacg

def main():
    a = sfacg('index','big5')
    a.download()

if __name__ == '__main__':
    main()
