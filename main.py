"""
By G3 at Metaplode.com
(04/2011)

For Python 2.7
"""
import time

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
        self.s = ego.gserializer.gSerializer()
        
    def get_time(self):
        return str(int(time.time()*1000))
    
    def get_ip(self):
        """
        we get the ip for the town we want to join then use it to connect with tcp
        """
        resp = self.w.rq(GSIGATEWAY, ref=TOWNSSWF,
                         data='X='+self.get_time()+'&v=sushi&m=301%01' + self.postcode)
        ip = self.s.deserialize(self.w.unquote(resp))[0][-1][-4]
        return ip
        #208.85.93.172

    def get_sid(self):
        for cookie in self.w.cj:
            if cookie.name == 'gaia55_sid':
                return cookie.value
        
        
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
            self.sid = self.get_sid()
            
            resp = self.w.rq(GSIGATEWAY, ref=TOWNSSWF,
                             data='X='+self.get_time()+'&v=sushi&m=107%01'+self.sid+'%04')
            resp = self.s.deserialize(self.w.unquote(resp))
            
            self.userid = resp[0][0][2]
            self.shortavi = resp[0][0][4]
            self.longavi = resp[0][0][-2]
            
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
