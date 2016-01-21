#!/usr/bin/python
# -*- coding: utf-8 -*-

# newclass.py

import wx, wx.html
import os
import pyfits
import time
import re
import sys

def check(infile):
    datfile = file(infile)
    found = False
    for line in datfile:
        if "END" in line:
            return 1
            break
    return 0
            


#Check to see if a file is "good"
def isgoodfile(self, file):
    #This takes a list of files and checks to be sure things look good
  
    
    fullfile = self.currentDirectory +'/' + file
    if os.path.isfile(fullfile):
        goodfile = 1
    else : 
        goodfile = 0
        return goodfile
    
    #This runs the *CHECK* routine, that basically ensures that the 
    #string END appears somewhere in the fits file. 
    if check(fullfile) == 0:
        return 0


    
    hdulist = pyfits.open(fullfile)


    for key in self.header_keys:
        #if hdulist[0].header.has_key(key) == False:
        if (key in hdulist[0].header) == False:
            goodfile = 0
    return goodfile

#Read the Night Parameters
def ReadParams(self):
	if os.path.exists(self.currentDirectory+'/.mmtlogger/'):
		if os.path.isfile(self.currentDirectory+'/.mmtlogger/nightparams.dat'):
			filein = open(self.currentDirectory+'/.mmtlogger/nightparams.dat', 'r')
			counter = 0
			for line in filein:
				if counter == 0 : self.observer = line.rstrip()
				if counter == 1 : self.instrument = line.rstrip()
				if counter == 2 : self.program = line.rstrip()
				if counter == 3 : self.date = line.rstrip()
				if counter == 4 : self.exclude_prefix = line.rstrip()
				counter += 1
			filein.close()
