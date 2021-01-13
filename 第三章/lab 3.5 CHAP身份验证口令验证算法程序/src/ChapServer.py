import os, socket, hashlib, pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

from binascii import a2b_hex

def hashit(text):
	result = hashlib.md5(text.encode())
	return result.hexdigest()

passwordHash= hashit("123")
Challenge = os.urandom(32)

def encryptRSA(message):
    with open("public_key.pem") as f:
        publickey = f.read()
        encryptor = RSA.importKey(publickey)
        cipher = Cipher_pkcs1_v1_5.new(encryptor)
        cipher_text = cipher.encrypt(message)
        #print("1",cipher_text)
    return cipher_text

def decrypt(encrypted):
	dec = AES.new(Challenge, AES.MODE_ECB)
	decrypted =  dec.decrypt(a2b_hex(encrypted))
	return decrypted .decode('utf-8','ignore')

def connect(ip,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    s.bind((ip, int(port)))                           
    s.listen(1)          

    print('[+] 正在监听端口上传入的TCP连接...',port)
    conn, addr = s.accept()     
    print('[+] 一个连接来自：', addr)

    data = encryptRSA(Challenge)
    #print("2",data)
    command = pickle.dumps(data)
    print("发送挑战（生成的随机数）：", Challenge)
    conn.send(command)
    #print("3",command)

    str = 'terminate'
    str = str.encode()
    if str in command:
        conn.send(str)
        conn.close()
    else:
        res= conn.recv(1024*1024)
        #print("Received: ", decrypt(res))
        print("生成的MD5摘要：",passwordHash)
        if passwordHash in decrypt(res):
            print("客户端验证成功！")
            conn.send(pickle.dumps(0))
        else:
            print("客户端验证失败！")
            conn.send(pickle.dumps(1)) 

if __name__ == '__main__':
    connect("localhost", 10000)
