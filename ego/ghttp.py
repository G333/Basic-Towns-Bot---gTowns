"""
Copyright 2011 by G3 at Metaplode.com
All rights reserved.
Version 1.1

For Python 2.7
"""
import urllib
import urllib2
from cookielib import CookieJar

import re

class GHttp():
    def __init__(self):
        """
        class initialisation, creates cookie jar and headers
        """

        self.lastpage = None
        self.lasterror = None
        
        self.cj = CookieJar()

        self.cookieH = urllib2.HTTPCookieProcessor(self.cj)
        self.redirectH = urllib2.HTTPRedirectHandler()
        self.proxyH = None

        self.opener = urllib2.build_opener(self.cookieH, self.redirectH)

    def addproxy(self, proxyipport):
        self.proxyH = urllib2.ProxyHandler({'http':proxyipport})
        self.opener = urllib2.build_opener(self.cookieH, self.redirectH, self.proxyH)
        if self.rq('http://google.com') is None:
            return False
        return True

    def removeproxy(self):
        """
        Removes the currently set proxy
        """
        self.proxyH = None
        self.opener = urllib2.build_opener(self.cookieH, self.redirectH)
        
    def clearcookies(self):
        """
        clears all cookies from the cookie jar :)
        """
        self.cj.clear()
    
    def rq(self, url, ref=None, data=None):
        """
        Http request, it either returns response html or
        none if there's an error.

        Keyword arguments:
        url -- the url you want to request
        data -- this is for the POST method, data that you will be seding
        ref -- the referer to your request page, if none specified it will
               use last page's url or the current url (default None)
        """
        # reset lasterror
        self.lasterror = None

        # set the referrer
        if ref is None:
            if self.lastpage is None:
                self.lastpage = url
            ref = self.lastpage

        self.opener.addheaders = [('Referer', ref),
        ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.98 Safari/534.13')]

        # if data is a dictionary type we will use urllibe to encode it
        # to url format
        if isinstance(data, dict):
            data = urllib.urlencode(data)
            
        # catch exceptions so program does not crash
        try:
            if data is not None:
                opnr = self.opener.open(url, data=data)
            else:
                opnr = self.opener.open(url)
        except urllib2.HTTPError, e:
            self.lasterror = 'The server couldn\'t fulfill the request.' + \
                             'Error code: %s' % e.code
            return None
        except urllib2.URLError, e:
            self.lasterror = 'We failed to reach a server. Reason: %s' % e.reason
            return None
        else:
            return opnr.read()
    
    def search(self, source, rg):
        rg = re.compile(rg)
        m = rg.search(source)

        if m is not None:
            return m.group(1)
        else:
            return None

    def unescape(self, s):
        s = s.strip()
        s = s.replace("&quot;", '"')
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&amp;", "&")
        return s
    
    def quote(self, s):
        return urllib.quote(s)
    
    def unquote(self, s):
        return urllib.unquote(s)


if __name__ == '__main__':    
    # example usage
    wrapper = GHttp()
    wrapper.addproxy('174.129.56.34:80')
    response = wrapper.rq('http://whatismyipaddress.com/')
    print response
    print wrapper.lasterror

    wrapper.addproxy('')
    response = wrapper.rq('http://whatismyipaddress.com/')
    print response
    print wrapper.lasterror
    
    response = wrapper.rq('http://metaplode.co')
    print response
    print wrapper.lasterror

    # no ref, just data? do this:
    response = wrapper.rq('http://metaplode.com', data='dataishere')
    print response
    print wrapper.lasterror
