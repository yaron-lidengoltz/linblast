import Crypto
from Crypto.PublicKey import RSA
import cPickle as pickle
import Chat

class msg(object):
	msg=''
	info=''
	sign=''
	def __init__(self,text,SenderInfo,sign):
		self.msg=text
		self.info=SenderInfo
		self.sign=sign

def cryptoUI(listensoc,RandomAdress):
	Myname=raw_input('enter your name: ')
	Friendname=raw_input('enter your friends name: ')
	try:
		M_Private_key=RSA.importKey(open("private_"+Myname+"_key.pem","r").read())
		Chat.KeepAlive(listensoc,RandomAdress)	
	except BaseException:
		print "import failed!, can't import your private key "
	try:
		F_Public_key=RSA.importKey(open("public_"+Friendname+"_key.pem","r").read())
		Chat.KeepAlive(listensoc,RandomAdress)	
	except BaseException:
		print "import failed!, can't import your friend's public key"
	return (M_Private_key,F_Public_key,Myname)


def encrypt_Txt_2_Obj_Str(tosend,F_Public_key,M_Private_key,Myname):
	(encstr,)=F_Public_key.encrypt(tosend,65)
	#print "Encrypted form: \n"+ encstr+'\n' #debug
	(signature,)=M_Private_key.sign(encstr,12)
	msg2send=msg(encstr,Myname,signature)
	msg2send_string=pickle.dumps(msg2send)
	return msg2send_string

def decrypt_Obj_Str_2_Txt(msgGot_string,F_Public_key,M_Private_key):
	msgGot=pickle.loads(msgGot_string)
	if F_Public_key.verify(msgGot.msg,(msgGot.sign,None)):
		encstr=msgGot.msg
		txtGot=M_Private_key.decrypt(encstr)
		SenderInfo=msgGot.info
		return txtGot,SenderInfo
	else:
		print 'Message is FAKE!!!'
