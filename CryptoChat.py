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

class CryptoClass(object):
	M_Private_key=None
	F_Public_key=None
	Myname=None
	def __init__(self):
		self.Myname=raw_input('enter your name: ')
		Friendname=raw_input('enter your friends name: ')
		try:
			self.M_Private_key=RSA.importKey(open("private_"+self.Myname+"_key.pem","r").read())	
		except BaseException:
			print "import failed!, can't import your private key "
		try:
			self.F_Public_key=RSA.importKey(open("public_"+Friendname+"_key.pem","r").read())	
		except BaseException:
			print "import failed!, can't import your friend's public key"
		
	def encrypt_Txt_2_Obj_Str(self,tosend):
		(encstr,)=self.F_Public_key.encrypt(tosend,65)
		#print "Encrypted form: \n"+ encstr+'\n' #debug
		(signature,)=self.M_Private_key.sign(encstr,12)
		msg2send=msg(encstr,self.Myname,signature)
		msg2send_string=pickle.dumps(msg2send)
		return msg2send_string

	def decrypt_Obj_Str_2_Txt(self,msgGot_string,ChatRef):
		msgGot=pickle.loads(msgGot_string)
		if self.F_Public_key.verify(msgGot.msg,(msgGot.sign,None)):
			encstr=msgGot.msg
			txtGot=self.M_Private_key.decrypt(encstr)
			SenderInfo=msgGot.info
			return txtGot,SenderInfo
		else:
			print 'the message below is FAKE!!!'
			ChatRef.ReqResend()
			txtGot="Message is fake"
			SenderInfo='Spoofer'
			return txtGot,SenderInfo

