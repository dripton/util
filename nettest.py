#!/usr/bin/env python

"""Log whether the Internet connection is up.

Call this script from cron every few minutes.  Append the output
to a file.  It will contain a Unix timestamp then a 1 for up or
0 for down.
"""

# Configuration
public_hosts = set([
  "http://yahoo.com",
  "http://google.com",
  "http://myspace.com",
  "http://msn.com",
  "http://ebay.com",
  "http://amazon.com",
  "http://craigslist.org",
  "http://cnn.com",
  "http://wikipedia.org",
])

num_retries = 2


import time
import random
import urllib
import socket

def pick_random_host(tried):
    host = random.choice(list(public_hosts - tried))
    tried.add(host)
    return host

def connect_to_host(host):
    try:
        fil = urllib.urlopen(host)
        unused = fil.read()
        return unused
    except IOError:
        return False

def is_internet_up():
    tried = set()
    while len(tried) < num_retries:
        host = pick_random_host(tried)
        connected = connect_to_host(host)
        if connected:
            return True
    return False

def main():
    socket.setdefaulttimeout(20)
    now = int(time.time())
    up = int(is_internet_up())
    print "%d %d" % (now, up)

if __name__ == "__main__":
    main()
