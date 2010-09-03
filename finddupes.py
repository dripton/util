#!/usr/bin/env python

import os
import sys
import hashlib

def find_dupes(dirs):
    size_to_paths = {}
    for dir_ in dirs:
        for fn in os.listdir(dir_):
            path = os.path.join(dir_, fn)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                size_to_paths.setdefault(size, []).append(path)
    md5_to_paths = {}
    for size, paths in size_to_paths.iteritems():
        if len(paths) > 1:
            for path in paths:
                with open(path) as fil:
                    contents = fil.read()
                hasher = hashlib.md5()
                hasher.update(contents)
                md5 = hasher.hexdigest()
                md5_to_paths.setdefault(md5, []).append(path)
    for md5, paths in md5_to_paths.iteritems():
        if len(paths) > 1:
            for path in paths:
                print path
            print


def main():
    if len(sys.argv) == 1:
        dirs = ["."]
    else:
        dirs = sys.argv[1:]
    find_dupes(dirs)

if __name__ == "__main__":
    main()
