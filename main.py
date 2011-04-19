"""
Copyright 2011 by G3 at Metaplode.com
All rights reserved.

For Python 2.7
"""
import re

import ego

GSIGATEWAY = 'http://www.gaiaonline.com/chat/gsi/gateway.php'
TOWNSSWF = 'http://s.cdn.gaiaonline.com/images/towns/007/towns.swf?007'
TOWNPOSTCODE = '81001000'
PORT = 443

class gBotUser():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.sid = None
        self.userid = None
        self.shortavi = None
        self.longavi = None
        
        self.postcode = TOWNPOSTCODE
        
        self.w = ego.ghttp.GHttp()

    def get_ip(self):
        """
        we get the ip for the town we want to join then use it to connect with tcp
        """
        resp = self.w.rq(GSIGATEWAY, ref=TOWNSSWF, data='v=sushi&m=301%01' + self.postcode)
        ip = self.w.search(resp, '%01208.85.(.*?)%01')
        return '208.85.' + ip
        #208.85.93.172

        
    def login(self):
        resp = self.w.rq('http://www.gaiaonline.com/auth/login', ref='http://www.gaiaonline.com/')

        if '<div id="recaptcha_widget" style="display:none;">' in resp:
            print "Captcha. Can't login"
            return False

        token = self.w.search(resp, '<input type="hidden" name="token" value="(.*?)" />')
        sid = self.w.search(resp, '<input type="hidden" name="sid" value="(.*?)" />')

        resp = self.w.rq('http://www.gaiaonline.com/auth/login/', ref='http://www.gaiaonline.com/auth/',
                    data={'token': token, 'sid': sid, 'username': self.username, 'password': self.password,
                          'redirect': ''})
        #print resp
        if ' title="Logout from your Gaia account">Logout</a>' in resp:
            #GET SID
            resp = self.w.rq(GSIGATEWAY, ref=TOWNSSWF,
                        data=('X=1297114636174&v=sushi&m=50%04109%0410%01avatar%5Fcdn%04115%04'))
            self.sid = self.w.unquote(self.w.search(resp, '%04109%01%05%01(.*?)%04'))

            
            resp = self.w.rq(GSIGATEWAY, ref=TOWNSSWF,
                        data=('X=1297114636174&v=sushi&m=112%01towns%04107%01' + self.sid + '%04'))

            rg = re.compile('107%01%05%01(.*?)%01(.*?)%01(.*?)%01(.*?)%01h(.*?)%01')
            m = rg.search(resp)
            
            self.userid = m.group(1)
            self.shortavi = self.w.unquote(m.group(3))
            self.longavi = self.w.unquote('h' + m.group(5))
            
            return True

        else:
            return False


def main():
    print "Basic Towns Bot -- Metaplode.com by G3"
    print "Starting...\n" 
    
    #create instance of the user
    user = gBotUser('username', 'password')
    
    #get ip of the town
    ip = user.get_ip()
    print '->', ip
    
    #start tcp thread
    thread = ego.gaiatcp.gTCP(ip, PORT)
    thread.start()
    
    #join town and monitor packets
    town = ego.gaiatown.Town(thread, user)
    town.town_join()
    if town.townid > 0:
        town.monitor()

if __name__ == "__main__":
    main()
