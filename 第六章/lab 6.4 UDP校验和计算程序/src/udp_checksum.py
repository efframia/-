import socket
import struct
from Config import config

def ip2int(ip):
         return struct.unpack("!I",socket.inet_aton(ip))[0]

def extract(start, length):
    return int(data[start:start+length], 16)

def parse_data(name, start, length):
    print(name, ":", extract(start,length))

def UDP_checksum(data):
    checksum = []
    for i in range(0, len(data), 4):
        checksum.append(int(data[i:i+4], 16))
    checksum[9] = 0
    checksum = sum([i for i in checksum])
    if checksum > 65535:
        checksum = int(hex(checksum)[2], 16) + int(hex(checksum)[3:], 16)
    checksum = checksum ^ 0xffff
    return checksum

if __name__ == '__main__':
    data = config.udpsegment
    source = config.sourceip
    dest = config.destip
    Protocol = config.protocol


    fake = hex(ip2int(source)).strip('0x')+ hex(ip2int(dest)).strip('0x')+"00"+"%02x"%Protocol + data[8:12]
    print("Source:",source)
    print("Destination:",dest)
    print("Protocol:",Protocol)
    parse_data("Lenth",8,4)
    parse_data("Source Port",0,4)
    parse_data("Destination Port",4,4)
    parse_data("Lenth",8,4)
    parse_data("Checksum",12,4)
    data = fake + data
    print("The calculated udp checksum is: ",UDP_checksum(data))
