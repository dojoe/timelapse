A few tools I hacked together for batch processing images for timelapse videos.

The tools are released under the WTFPL (http://www.wtfpl.net/) in the hopes that someone else might find them useful some day.

These tools require [Python 2.x](http://www.python.org/), [PIL](http://www.pythonware.com/products/pil/) and [ImageMagick](http://www.imagemagick.org/script/index.php) to work.


Clocks from a simple timelapse
==============================

Use clocks-from-images.py to generate the small clock you find in [my first Graffitti timelapse on Vimeo](http://vimeo.com/32865163). Here's the lowdown as written in the initial comment:

Generate analog clock pictures from image timestamps.

Program arguments: None whatsoever, everything is hardcoded.

* Source images must be in a directory called "photos". They will not be modified.
* Clock images will be generated in a directory called "clocks" and named like the source images, with ".png" appended.
* The "clocks" folder must exist, the script will not create it.
* The script must be run in the parent folder of "photos" and "clocks".
* The clock images will be 500x500 pixels large, to be scaled down at leisure.

Oh, no error checking either. See, I was only going to use this for one single project ;)


Multi-angle timelapse videos
============================

So you recorded something using multiple cameras at once and want to make one video of it. Problem: All your cameras run on separate clocks, and these clocks are neither in sync nor will the cameras all shoot at the same instant or even at the precisely same interval. They probably lost some frames (e.g. due to battery or memory card swaps or because they couldn't focus a specific frame) and the lost frames are all at different times.

I wrote two scripts for this situation -- one will normalize all images from one camera into a standardized time series with uniform time steps, the other will generate analog clocks like the script above, matching the time series.

They were used to build [the timelapse video documenting our "Sprühling" graffitti event](http://vimeo.com/45386061).

The rough process I used was this:

1. Sort all pictures into subdirectories of one directory per camera, such as
   * cam1/set1/*.jpg
   * cam1/set2/*.jpg
   * cam2/set1/*.jpg
   * ... you get the idea.
2. Analyze all cameras' directories using normalize-time-series.py for start and end times, determine min/max for global start and end times.
3. Normalize all cameras using the same starttime, endtime and raster values
4. Generate clock images for the time series using clock-from-time-series.py, again with the same starttime, endtime and raster as above
5. Generate videos from the images using Avisynth.

clock-from-time-series.py
-------------------------

This one's rather simple -- I'll let the initial comment speak for itself:

Generate analog clock pictures for a given time interval.

Program arguments: outdir starttime endtime raster

* Clock images will be generated in outdir and be named with incrementing numbers, starting from "000000.png"
* starttime and endtime are seconds since Epoch -- a common Unix time specification.
* The first image will show starttime, for each following image the time will be advanced by raster seconds until endtime is reached.
* The output directory must exist, the script will not create it.
* The clock images will be 1000x1000 pixels large, to be scaled down at leisure.

normalize-time-series.py
------------------------

This script will take a bunch of images with EXIF timestamps and normalize them into a time series.

The output time series will start at a time "starttime", end at a time "endtime" and have a regular interval of "raster".

If more than one source picture could contribute to one step of the time series, the first one will be used and the others dropped.

If there are gaps in the source pictures, i.e. no source pictures exist for a number of time steps, the action depends on the size of the gap:
* If the gap is less than eight time steps, the last source picture is repeated.
* If the gap is larger, a special "SMPTE Frame" is used, usually SMPTE test bars, hence the name, but you can use anything you like.

The output time series will consist of files named starting with 000000.jpg for the image corresponding to starttime and increasing by 1 with each time step. The files will be symbolic links to the source images or the SMPTE frame, so that no space is wasted.

The script assumes that enumerating the source files will yield them in an order of increasing timestamps. If this is not the case, you will get lots of dropped frames (and the script will tell you about those).

Usage:
  ./normalize-time-series.py outdir offset [starttime endtime raster smpte]

* __outdir:__ The directory to place the symlinks in. The source pictures are expected to be in subdirectories of outdir; all ".jpg" files will be used.
* __offset:__ Image timestamps will be adjusted by adding this many seconds. Can be used as a lightweight way of compensating differring camera clocks. Can be zero or negative if needed.
* __starttime:__ Start time in seconds since Epoch.
* __endtime:__ End time in seconds since Epoch.
* __raster:__ Size of one time step in seconds
* __smpte:__ Filename of the SMPTE frame. The image should have the same dimensions as the source images; Avisynth will not like them otherwise.

If you specify only outdir and offset, the script will determine the (offset adjusted) start and end time for the complete series of images in the outdir.

Note that there is no error checking; this used to be a quick hack.
