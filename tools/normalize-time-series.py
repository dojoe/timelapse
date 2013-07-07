#!/usr/bin/env python

"""\

This script will take a bunch of images with EXIF timestamps and normalize them into a time series.
The output time series will start at a time "starttime", end at a time "endtime" and have a regular interval of "raster".
If more than one source picture could contribute to one step of the time series, the first one will be used and the others dropped.
If there are gaps in the source pictures, i.e. no source pictures exist for a number of time steps, the action depends on the size of the gap:
  If the gap is less than eight time steps, the last source picture is repeated.
  If the gap is larger, a special "SMPTE Frame" is used, usually SMPTE test bars, hence the name, but you can use anything you like.

The output time series will consist of files named starting with 000000.jpg for the image corresponding to starttime and increasing by 1 with each time step. The files will be symbolic links to the source images or the SMPTE frame, so that no space is wasted.

The script assumes that enumerating the source files will yield them in an order of increasing timestamps. If this is not the case, you will get lots of dropped frames (and the script will tell you about those).

Usage:
  ./normalize-time-series.py outdir offset [starttime endtime raster smpte]

outdir: The directory to place the symlinks in. The source pictures are expected to be in subdirectories of outdir; all ".jpg" files will be used.
offset: Image timestamps will be adjusted by adding this many seconds. Can be used as a lightweight way of compensating differring camera clocks. Can be zero or negative if needed.
starttime: Start time in seconds since Epoch.
endtime: End time in seconds since Epoch.
raster: Size of one time step in seconds
smpte: Filename of the SMPTE frame. The image should have the same dimensions as the source images; Avisynth will not like them otherwise.

If you specify only outdir and offset, the script will determine the (offset adjusted) start and end time for the complete series of images in the outdir.

Note that there is no error checking; this used to be a quick hack.

Hacked together by Joachim Fenkes <timelapse-tools (the at sign goes here) dojoe (and a nice point here) net>

Released under the WTFPL (http://www.wtfpl.net/) in the hopes that someone else might find it useful some day.

"""

"""\
SVG.py - Construct/display SVG scenes.

The following code is a lightweight wrapper around SVG files. The metaphor
is to construct a scene, add objects to it, and then write it to a file
to display it.

This program uses ImageMagick to display the SVG files. ImageMagick also 
does a remarkable job of converting SVG files into other formats.
"""

import glob
import sys
import os
import math
import time
from multiprocessing import Pool
from PIL import Image
from PIL.ExifTags import TAGS
from win32file import CreateSymbolicLink

offset = 0

def getExifTime(fname):
    global offset
    image = Image.open(fname)
    exif = image._getexif()
    return int(time.mktime(time.strptime(exif[0x9003], "%Y:%m:%d %H:%M:%S"))) + offset

def mklink(linkname, target):
    #print("mklink %s -> %s" % (linkname, target))
    CreateSymbolicLink(linkname, target)

def useFile(index, fname):
    mklink(outdir + "/" + str(index).zfill(6) + ".jpg", fname)
    return

def fillFile(firstTime, lastTime, fname):
    print("using %s from %d to %d" % (fname, firstTime, lastTime))
    for i in range(firstTime, lastTime + 1):
        useFile(i, fname)

def main():
    global outdir
    global offset
    outdir = os.path.abspath(sys.argv[1])
    fnames = map(os.path.abspath, glob.glob(outdir + "/*/*.JPG"))

    offset = int(sys.argv[2])

    if len(sys.argv) < 7:
        print("first timestamp: %d" % getExifTime(fnames[0]))
        print("last timestamp: %d" % getExifTime(fnames[-1]))
        exit(1)

    firstTime = int(sys.argv[3])
    lastTime = int(sys.argv[4])
    raster = int(sys.argv[5])
    LostFrameLimit = 8  # number of lost frames before we get SMPTE bars
    numImages = ((lastTime - firstTime) / raster) + 1
    curFile = 0
    nextIndex = 0
    smpteFname = sys.argv[6]
    lastFname = smpteFname
    
    print("going from %d to %d -> %d images" % (firstTime, lastTime, numImages))

    while nextIndex < numImages:
        if curFile >= len(fnames):
            fillFile(nextIndex, numImages - 1, smpteFname)
            break

        fname = fnames[curFile]
        fileTime = getExifTime(fname)
        fileIndex = (fileTime - firstTime) / raster;

        if fileIndex < nextIndex:
            print("looking for %s, but %s has time %s, index %s - dropping frame" %
                  (`nextIndex`, fname, `fileTime`, `fileIndex`))
        elif fileIndex == nextIndex:
            useFile(nextIndex, fname)
            nextIndex += 1
        else:
            if (fileIndex - nextIndex) < LostFrameLimit:
                fillFname = lastFname
            else:
                fillFname = smpteFname
            fillFile(nextIndex, fileIndex - 1, fillFname)
            useFile(fileIndex, fname)
            nextIndex = fileIndex + 1

        curFile += 1
        lastFname = fname

if __name__ == "__main__": main()
