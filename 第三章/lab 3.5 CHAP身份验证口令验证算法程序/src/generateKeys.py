from Crypto.Cipher import AES
from Crypto.PublicKey import RSA 

RSA_key_size = 1024

def keyGenRSA():
	new_key = RSA.generate(RSA_key_size) #1024, 2048, 3072, 4096
	public_key = new_key.publickey().exportKey("PEM") 
	private_key = new_key.exportKey("PEM") 

	with open('private_key.pem', 'wb') as privateKey:
		privateKey.write(private_key)

	with open('public_key.pem', 'wb') as publicKey:
		publicKey.write(public_key)

if __name__ == '__main__':
	keyGenRSA()
