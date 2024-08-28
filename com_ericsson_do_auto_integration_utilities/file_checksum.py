'''
Created on Mar 13, 2020

@author: eiaavij
'''

import sys
import zlib

fileName = sys.argv[1]
prev = 0
for eachLine in open(fileName,"rb"):
    prev = zlib.crc32(eachLine, prev)
    
print( "%X"%(prev & 0xFFFFFFFF)) 