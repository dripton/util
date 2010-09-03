#!/usr/bin/env python

"""Hunting for the TrendNet print server"""

import socket
import threading
import Queue

socket.setdefaulttimeout(5)

port = 631
num_threads = 250

class ConnectThread(threading.Thread):
    def __init__(self, in_queue, out_queue):
        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.setDaemon(True)

    def run(self):
        while True:
            ip = self.in_queue.get()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip, port))
            except socket.error:
                self.out_queue.put((ip, False))
            else:
                self.out_queue.put((ip, True))
            self.in_queue.task_done()

def main():
    job_queue = Queue.Queue()
    result_queue = Queue.Queue()
    count = 0
    for net in range(1, 255+1):
        for addr in range(1, 255 + 1):
            ip = "10.2.%d.%d" % (net, addr)
            count += 1
            job_queue.put(ip)
    for unused in xrange(num_threads):
        ConnectThread(job_queue, result_queue).start()
    job_queue.join()

    for unused in xrange(count):
        ip, status = result_queue.get()
        if status:
            print ip
    

if __name__ == "__main__":
    main()
