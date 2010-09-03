#!/usr/bin/env python

"""Parse the output of nettest.py into a human-readable list of
outage periods.

The input is a sorted list of lines like:

1157962502 0
1157962802 1

where the first number is a Unix timestamp, and the second is a 0
for Internet connection down or 1 for Internet connection up.
"""

import sys
import time

def prettify(timestamp):
    return time.ctime(int(timestamp))


def main():
    if len(sys.argv) != 2:
        print "usage: %s nettest-log-filename" % sys.argv[0]
        return 1
    filename = sys.argv[1]
    fil = open(filename)
    prev_timestamp = None
    prev_up = None
    for line in fil:
        tokens = line.strip().split()
        timestamp, up = tokens
        if prev_timestamp is None:
            prev_timestamp = timestamp
        elif up != prev_up:
            if up == "1" and prev_up =="0":
                print prettify(prev_timestamp), "-", prettify(timestamp)
            else:
                prev_timestamp = timestamp
            prev_up = up
    if not up:
        print prettify(prev_timestamp), "-", prettify(timestamp)


if __name__ == "__main__":
    main()
