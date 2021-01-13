import socket
import json

address = ('127.0.0.1', 31500)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(address)
json_string, addr = s.recvfrom(2048)
mylist = json.loads(json_string)
#print(mylist)
for i in mylist:
    print(i)
s.shutdown(socket.SHUT_RDWR)
s.close()
