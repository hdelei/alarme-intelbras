#!/usr/bin/env python3

class UtilsTX:

    def checksum(self, data):
        checksum = 0
        for n in data:
            checksum ^= int(n, 16)
        checksum ^= 0xff
        checksum &= 0xff
        return checksum

    def split_str(self, data, split_and_fill = False):          
        if split_and_fill:
            return [i.zfill(2) for i in data]
        if len(data) > 2:
            return [data[i:i+2] for i in range(0, len(data), 2)]
        return [data]    
    
    def replace_hex_a(self, data, command = ''):
        new_data = []        
        for byte in data:
            new_data.append(byte[1] + 'a' if byte[1] == '0' else byte[0:])    
        return new_data

    def create_array(self, data):  
        #command - 94 or b0
        packet = [data['command']] 
    
        #channel - on event: 11, 12,21, 22 | on connection: 45, 47, 48 
        packet.extend([data['channel']])

        if data['command'] == '94':
            #account 1234 = 12 34 - only 2 bytes             
            aux = self.split_str(data['account'])
            packet.extend(aux)

            #mac addres 300001 = 30 00 01 - last 3 bytes
            packet.extend(self.split_str(data['mac']))    
        elif data['command'] == 'b0':        
            #account 1234 = 01 02 03 04         
            aux = self.split_str(data['account'], True)        
            aux = self.replace_hex_a(aux)
            packet.extend(aux)
            
            #identifier 18 = 01 08
            packet.extend(self.split_str(data['identifier'], True))

            #qualifier 1 or 3 = 01 or 03
            packet.extend(self.split_str(data['qualifier'], True))

            #event 461 = 04 06 01
            aux = self.split_str(data['event'], True)
            aux = self.replace_hex_a(aux)
            packet.extend(aux)

            #partition/group/status pgm 00 = 0a 0a
            aux = self.split_str(data['partition'], True)
            aux = self.replace_hex_a(aux)
            packet.extend(aux)

            #zone 001 = 0a 0a 01
            aux = self.split_str(data['zone'], True)
            aux = self.replace_hex_a(aux)
            packet.extend(aux)
         
        return packet
