"""
Copyright 2011 by G3 at Metaplode.com
All rights reserved.

For Python 2.7
"""
import select
import socket
import sys
import time
import threading
import Queue

import gserializer

BUFFER_SIZE = 2048

class gTCP(threading.Thread):
    def __init__(self, ip, port):
        #connect and setup everything
        s = None
        for res in socket.getaddrinfo(ip, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error, msg:
                print msg
                s = None
                continue
            try:
                s.connect(sa)
            except socket.error, msg:
                print msg
                s.close()
                s = None
                continue
            break
        if s is None:
            print 'could not open socket'
            sys.exit(1)
            
        self.socket = s
        self.socket.setblocking(0)

        self.stop = False
        #these queues will hold all the packets
        #inqueue = all of the received packets
        #outqueue = the packets that you want to send
        self.inQueue =  Queue.Queue()
        self.outQueue = Queue.Queue()

        self.serializer = gserializer.gSerializer()
        
        threading.Thread.__init__(self)

    def run(self):
        packetComplete = True
        packet = ''
        
        while self.stop is False:
            readReady, writeReady, _ = select.select([self.socket], [self.socket], [])
            #we are receiving packets so we will add them to the inQueue
            for socket in readReady:
                rdata = socket.recv(BUFFER_SIZE)
                if len(rdata) != 0:
                    if rdata[-1] == '\x00':
                        packetComplete = True
                    else:
                        packetComplete = False

                    packet += rdata

                    if packetComplete:
                        packets = self.serializer.deserialize(packet)
                        for p in packets:
                            #write all packets to txt file?
                            #self.append_line('packets.txt', str(p))
                            #print '--> Received packet: ', p[0]
                            
                            #put the received packet into the queue
                            self.inQueue.put(p)

                        packet = ''
                else:
                    self.stop = True

            #send the packets in the outQueue
            for socket in writeReady:
                if self.outQueue.empty() is False:
                    socket.send(self.outQueue.get())
             
            #if you want you can put a delay       
            #time.sleep(.1)

        print "end of tcp thread"

        self.socket.close()

    def sendPacket(self, packet):
        packet = self.serializer.serialize(packet)
        self.outQueue.put(packet)

    def recvPacket(self):
        return self.inQueue.get()

    #def append_line(self, filename, content):
    #    file = open(filename, 'a')
    #    file.write(content + '\n')
    #    file.close()


if __name__ == "__main__":
    pass
