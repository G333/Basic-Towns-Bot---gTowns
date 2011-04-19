"""
Copyright 2011 by G3 at Metaplode.com
All rights reserved.

For Python 2.7
"""
import time
import threading

#should probably be in gaiatcp
class KeepAlive(threading.Thread):
    def __init__(self, thread):
        self.t = thread
        threading.Thread.__init__(self)
    def run(self):
        while self.t.stop is False:
            time.sleep(10)
            self.t.sendPacket([['62','']])
        

class Town():
    def __init__(self, tcpthread, botuser):
        self.t = tcpthread
        self.bot = botuser
        
        self.stop = False
        self.id = 0
        self.townid = 0
        #self.temptownid = 0
        self.cbid = 3
        self.follow = False
    
    def get_townid(self):
        #loop through packets and find the packet with the town ids
        for i in xrange(10):
            try:
                packet = self.t.recvPacket()
                if packet[0] == '35':
                    #self.temptownid = packet[1]
                    for ky,vl in enumerate(packet):
                        if vl == 'gaiahood_'+self.bot.postcode:
                            self.townid = packet[ky-4]
                            return
            except:
                pass
        return
    
    def get_cbid(self):
        self.cbid += 1
        return str(self.cbid)

    def join(self):
        self.t.sendPacket([['39', self.townid, '0']])
        self.t.sendPacket([['20', self.get_cbid(), self.id, self.townid, '', '1', '1', '1', '', self.bot.shortavi, self.bot.username, self.bot.userid, '', '8', '0', '']])
        self.t.sendPacket([['19', self.get_cbid(), 'G_TS_PLUGIN', '0', self.bot.sid, '1.0', self.bot.userid]])
        self.t.sendPacket([['6', self.id, '452:632', '452:632', '7', '', self.bot.shortavi, self.bot.username, self.bot.userid, '', '8', '1', '']])
        
    def town_join(self):
        if self.bot.login():
            print '-> Logged in, [%s][%s][%s][%s]' % (self.bot.userid, self.bot.username, self.bot.shortavi, self.bot.sid)
            
            self.t.sendPacket([['S55', 'FLASH', '1', '0'], ['2', '41']])
            
            #get the bot's id
            self.id = self.t.recvPacket()[1]
            print '-> Received player id: ', self.id
            
            self.t.sendPacket([['29', '2', 'GaiaTown'], ['3', '10']])
            self.t.sendPacket([['45', '3', '1', '1', '1', '', self.bot.userid,'-1', '-1', '-1', '', self.bot.shortavi, self.bot.username,self.bot.userid, '', '8', '0', self.bot.sid]])
            
            self.get_townid()
            print '-> Received town id: ', self.townid
            
            if self.townid > 0:
                self.join()
                print '-> Connected to town (%s)' % (self.townid, )
            
        else:
            print '-> Gaia login failed. Stopping.'
            self.t.stop = True
            self.stop = True
        
    def monitor(self):
        #keep alive so we don't get kicked off
        tes = KeepAlive(self.t)
        tes.start()
        
        #monitor the received packets then do something with them
        while self.stop is False:
            try:
                packet = self.t.recvPacket()
            except:
                packet = None
                
            if packet is not None:
                self.dosomething(packet)
        
    def dosomething(self, packet):
        if packet[0] == '10':
            #someone says stop, so we stop the bot ;)
            if packet[4] == 'stop':
                self.stop = True
                self.t.stop = True
                
            print '->', packet[1],':',packet[4]
        
