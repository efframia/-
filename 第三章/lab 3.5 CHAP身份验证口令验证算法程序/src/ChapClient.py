import socket, hashlib, pickle
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto import Random
from binascii import b2a_hex

random_generator = Random.new().read

def decryptRSA(cipher):
    with open("private_key.pem") as f:
        privatekey = f.read()
        decryptor = RSA.importKey(privatekey)
        decryptor1 = Cipher_pkcs1_v1_5.new(decryptor)
        return decryptor1.decrypt(cipher,random_generator)

def hashit(text):
	result = hashlib.md5(text.encode())
	return result.hexdigest()

def encrypt(challenge, password):
    enc = AES.new(challenge, AES.MODE_ECB)
    #print(hashit(password))
    encrypted = enc.encrypt(hashit(password).encode())
    return b2a_hex(encrypted)

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 10000))
 
    while True:
        try:
            command =  s.recv(1024*1024)
            command =  pickle.loads(command)
            #print(command)

            if command == 0:
                print("口令正确！")
                break
            elif command == 1:
                print("口令错误！")
                break
            else:
                print("接收挑战：", decryptRSA(command))
                password = input("\n请输入验证口令：")
                res = encrypt(decryptRSA(command), password)
                #print(res)
                s.send(res)
        except Exception as e:
            break
        
    
if __name__ == '__main__':
    connect()
