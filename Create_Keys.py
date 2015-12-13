import Crypto
from Crypto.PublicKey import RSA

key=RSA.generate(2048)
name=raw_input("enter your name")
fprivate=open('private_'+name+'_key.pem',"w")
fpublic=open('public_'+name+'_key.pem',"w")
fprivate.write(key.exportKey('PEM'))
fpublic.write(key.publickey().exportKey('PEM'))
