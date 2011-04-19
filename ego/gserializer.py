"""
Copyright 2011 by G3 at Metaplode.com
All rights reserved.

For Python 2.7
"""
class gSerializer():
    """ 
    Convert packet into a usable data format 
    """
    def __init__(self):
        pass
    
    def serialize(self, packets):
        """
        Turns S55\x02FLASH\x021\x020\x032\x0248\x03\x00 into
        [['S55', 'FLASH', '1', '0'], ['2', '48']]
        """
        data = ''
        for packet in packets:
            for ky,vl in enumerate(packet):
                if isinstance(vl, list):
                    packet[ky] = '\x01'.join(vl)
            data += '\x02'.join(packet) + '\x03'
        
        return data+'\x00'
        
        
    def deserialize(self, packet):
        """
        Turns [['S55', 'FLASH', '1', '0'], ['2', '48']] into
        S55\x02FLASH\x021\x020\x032\x0248\x03\x00
        """
        data = []
        #seperators = ['\x00', '\x03', '\x02', '\x01']
        tansmission = packet.split('\x00')
        for packet in tansmission:
            packets = packet.split('\x03')
            for part in packets:
                if part:
                    thing = part.split('\x02')
                    for ky, vl in enumerate(thing):
                        if '\x01' in vl:
                            thing[ky] = vl.split('\x01')
                    
                    data.append(thing)        
        return data
        
if __name__ == "__main__":
    TSTRING = 'S55\x02FLASH\x021\x020\x032\x0248\x03\x00'
    
    g = gSerializer()
    test = g.deserialize(TSTRING)
    
    print TSTRING
    print test
    print g.serialize(test)
