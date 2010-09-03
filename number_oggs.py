#!/usr/bin/env python

"""Number my .ogg files

A directory has m3u files with names like $artist-$album.m3u
Songs fit into a directory structure like:
   $artist/$album/$song.ogg
The m3u file lists songs, one per line, in order:
   $artist/$album/$song.ogg
We want to prepend "$tracknumber-" to each song title, in both
the ogg filename and within the m3u file.  Track numbers should
be in %02d format.

Skip songs that already have track numbers.
"""

import sys
import os

def main():
    for fn in sys.argv[1:]:
        if fn.endswith(".m3u"):
            process_m3u(fn)

def process_m3u(fn):
    fil = open(fn)
    line_number = 0
    out_lines = []
    for line in fil:
        line_number += 1
        song_path = line.strip()
        if not os.path.exists(song_path):
            # Just remove data.ogg noise by hand
            print "file not found", song_path
            return
        dirname = os.path.dirname(song_path)
        basename = os.path.basename(song_path)
        track = "%02d-" % line_number
        if basename.startswith(track):
            print "already has track number", song_path
            return
        new_path = os.path.join(dirname, track + basename)
        os.rename(song_path, new_path)
        out_lines.append(new_path)
    fil.close()

    fil = open(fn, "w")
    for line in out_lines:
        print >> fil, line
    fil.close()


if __name__ == "__main__":
    main()
