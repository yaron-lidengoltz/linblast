import cPickle as pickle
import logging
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
from random import randint
import base64

log = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.setLevel(logging.DEBUG)
log.addHandler(ch)

class InitMsg(object):
	msg = ''
	info = ''
	sign = ''

	def __init__(self, text, SenderInfo, sign):
		self.msg = text
		self.info = SenderInfo
		self.sign = sign

class ChatMsg(object):
	msg = ''
	info = ''

	def __init__(self, text, SenderInfo):
		self.msg = text
		self.info = SenderInfo

class CryptoClass(object):
	def __init__(self):
		self.my_name = None
		self.friend_name = None
		self.M_Private_key = None
		self.M_Public_key=None
		self.F_Public_key = None
		self.AES_KEY=Random.new().read(AES.block_size)
		self.AES_IV=Random.new().read(AES.block_size)
		self.AES_KEY2=Random.new().read(AES.block_size)
		self.AES_IV2=Random.new().read(AES.block_size)
		self.AES_Ref=AES.new(self.AES_KEY,AES.MODE_CFB,self.AES_IV)
		self.AES_Ref2=AES.new(self.AES_KEY2,AES.MODE_CFB,self.AES_IV2)
		self.Init_Priority=randint(10,99)

	def test_flight(self, user):
		self.my_name = 'joe' if user == 'a' else 'dan'
		self.friend_name = 'dan' if user == 'a' else 'joe'
		self.init_keys()

	def init_chat(self):
		self.my_name = raw_input('enter your name: ')
		self.friend_name = raw_input('enter your friends name: ')
		self.init_keys()

	def init_keys(self):
		try:
			self.M_Public_key = RSA.importKey(open("public_" + self.my_name + "_key.pem", "r").read())
		except BaseException:
			log.error('import failed!, cant import your friends public key')
		try:
			self.M_Private_key = RSA.importKey(open("private_" + self.my_name + "_key.pem", "r").read())
		except BaseException:
			log.error('import failed!, cant import your private key')
		try:
			self.F_Public_key = RSA.importKey(open("public_" + self.friend_name + "_key.pem", "r").read())
		except BaseException:
			log.error('import failed!, cant import your friends public key')

	def Encrypt_RSA(self, tosend):
		(encstr,) = self.F_Public_key.encrypt(tosend, 65)
		(signature,) = self.M_Private_key.sign(encstr, 12)
		msg2send = InitMsg(encstr, self.my_name, signature)
		msg2send_string = pickle.dumps(msg2send)
		return msg2send_string

	def Decrypt_RSA(self, msgGot_string):
		msgGot = pickle.loads(msgGot_string)
		if not self.F_Public_key.verify(msgGot.msg, (msgGot.sign, None)):
			log.warn('the message below is FAKE!!!')
		encstr = msgGot.msg
		txtGot = self.M_Private_key.decrypt(encstr)
		SenderInfo = msgGot.info
		return txtGot, SenderInfo

	def Encrypt_AES(self, tosend,number):
		if number==1:
			encstr = base64.b64encode(self.AES_IV+self.AES_Ref.encrypt(tosend))
		elif number ==2:
			encstr = base64.b64encode(self.AES_IV2+self.AES_Ref2.encrypt(tosend))	
		msg2send = ChatMsg(encstr, self.my_name)
		msg2send_string = pickle.dumps(msg2send)
		return msg2send_string
	def Decrypt_AES(self,msgGot_string,number):
		msgGot = pickle.loads(msgGot_string)
		encstr = msgGot.msg
		if number==1:
			txtGot = self.AES_Ref.decrypt(base64.b64decode(encstr))
		elif number ==2:
			txtGot = self.AES_Ref2.decrypt(base64.b64decode(encstr))
		txtGot=txtGot[16:]
		SenderInfo = msgGot.info
		return txtGot, SenderInfo

	def Update_AES_Ref(self,PeerKey,PeerIv,number):
		if number==1:
			self.AES_Ref=AES.new(PeerKey,AES.MODE_CFB,PeerIv)
			self.AES_KEY=PeerKey
			self.AES_IV=PeerIv
		if number==2:
			self.AES_Ref2=AES.new(PeerKey,AES.MODE_CFB,PeerIv)
			self.AES_KEY2=PeerKey
			self.AES_IV2=PeerIv
	def Shuffle(self,st):
		a=st[0]
		st=st[1:]
		st+=a
		return st
