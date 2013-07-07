#!/usr/bin/env python

"""\

Generate analog clock pictures from image timestamps.

Program arguments: None whatsoever, everything is hardcoded.

Source images must be in a directory called "photos". They will not be modified.
Clock images will be generated in a directory called "clocks" and named like the source images, with ".png" appended.
The "clocks" folder must exist, the script will not create it.
The script must be run in the parent folder of "photos" and "clocks".
The clock images will be 500x500 pixels large, to be scaled down at leisure.

Oh, no error checking either. See, I was only going to use this for one single project ;)

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
display_prog = 'imdisplay' # Command to execute to display images.
      
class Scene:
    def __init__(self,name="svg",height=400,width=400):
        self.name = name
        self.items = []
        self.height = height
        self.width = width
        return

    def add(self,item): self.items.append(item)

    def strarray(self):
        var = ["<?xml version=\"1.0\"?>\n",
               "<svg height=\"%d\" width=\"%d\" >\n" % (self.height,self.width),
               " <g style=\"fill-opacity:1.0; stroke:black;\n",
               "  stroke-width:1;\">\n"]
        for item in self.items: var += item.strarray()            
        var += [" </g>\n</svg>\n"]
        return var

    def write_svg(self,filename=None):
        if filename:
            self.svgname = filename
        else:
            self.svgname = self.name + ".svg"
        file = open(self.svgname,'w')
        file.writelines(self.strarray())
        file.close()
        return

    def convert(self, filename=None):
        if not filename:
            filename = self.svgname + ".png"
        os.system("convert %s -resize 20%% %s" % (self.svgname,filename))
        return
    def del_svg(self):
        os.unlink(self.svgname)
        return
        

class Line:
    def __init__(self,start,end,stroke_width):
        self.start = start #xy tuple
        self.end = end     #xy tuple
        self.stroke_width = stroke_width
        return

    def strarray(self):
        return ["  <line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" style=\"stroke-linecap: round; stroke-width: %spx;\" />\n" %\
                (self.start[0],self.start[1],self.end[0],self.end[1],self.stroke_width)]


class Circle:
    def __init__(self,center,radius,color):
        self.center = center #xy tuple
        self.radius = radius #xy tuple
        self.color = color   #rgb tuple in range(0,256)
        return

    def strarray(self):
        return ["  <circle cx=\"%d\" cy=\"%d\" r=\"%d\"\n" %\
                (self.center[0],self.center[1],self.radius),
                "    style=\"fill: none; stroke:%s; stroke-width: 100px;\"  />\n" % colorstr(self.color)]

class Rectangle:
    def __init__(self,origin,height,width,color):
        self.origin = origin
        self.height = height
        self.width = width
        self.color = color
        return

    def strarray(self):
        return ["  <rect x=\"%d\" y=\"%d\" height=\"%d\"\n" %\
                (self.origin[0],self.origin[1],self.height),
                "    width=\"%d\" style=\"fill:%s;\" />\n" %\
                (self.width,colorstr(self.color))]

class Text:
    def __init__(self,origin,text,size=24):
        self.origin = origin
        self.text = text
        self.size = size
        return

    def strarray(self):
        return ["  <text x=\"%d\" y=\"%d\" font-size=\"%d\">\n" %\
                (self.origin[0],self.origin[1],self.size),
                "   %s\n" % self.text,
                "  </text>\n"]

factor = 2.5
    
def colorstr(rgb): return "#%x%x%x" % (rgb[0]/16,rgb[1]/16,rgb[2]/16)
def radial(a, r):
    arad = math.radians(a)
    return (100 * factor + math.cos(arad) * r, 100 * factor - math.sin(arad) * r)

def run(fname):
    scene = Scene(fname, 200 * factor, 200 * factor)
    image = Image.open("photos/" + fname)
    exif = image._getexif()
    mtime = time.strptime(exif[0x9003], "%Y:%m:%d %H:%M:%S")

    #print mtime
    #time.localtime(os.path.getmtime("photos/" + fname))
    print "%s: %ih %im %is" % (fname, mtime.tm_hour, mtime.tm_min, mtime.tm_sec)
    #scene.add(Circle((1000, 1000), 950, (0, 0, 0)))

    # dial
    for a in range(0, 359, 30):
        if a % 90 == 0:
            scene.add(Line(radial(a, 60 * factor), radial(a, 94 * factor), 10 * factor))
        else:
            scene.add(Line(radial(a, 70 * factor), radial(a, 94 * factor), 7 * factor))

    # hour hand
    scene.add(Line((100 * factor,100 * factor), radial(90 - (30 * (mtime.tm_hour - 1) + float(mtime.tm_min) / 2 + float(mtime.tm_sec) / 120), 60 * factor), 9 * factor))

    # minute hand
    scene.add(Line((100 * factor,100 * factor), radial(90 - (6 * mtime.tm_min + float(mtime.tm_sec) / 10), 85 * factor), 6 * factor))
    scene.write_svg()
    scene.convert("clocks/" + fname + ".png")
    scene.del_svg()
    return

def main():
    fnames = map(os.path.basename, glob.glob("photos/*.jpg"))
    pool = Pool(processes = 2)
    pool.map(run, fnames)

if __name__ == "__main__": main()
