import cPickle as pickle
import logging

from Crypto.PublicKey import RSA

log = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.setLevel(logging.DEBUG)
log.addHandler(ch)

class msg(object):
	msg = ''
	info = ''
	sign = ''

	def __init__(self, text, SenderInfo, sign):
		self.msg = text
		self.info = SenderInfo
		self.sign = sign


class CryptoClass(object):
	def __init__(self):
		self.my_name = None
		self.friend_name = None
		self.M_Private_key = None
		self.M_Public_key=None
		self.F_Public_key = None

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

	def encrypt_Txt_2_Obj_Str(self, tosend):
		(encstr,) = self.F_Public_key.encrypt(tosend, 65)
		(signature,) = self.M_Private_key.sign(encstr, 12)
		msg2send = msg(encstr, self.my_name, signature)
		msg2send_string = pickle.dumps(msg2send)
		return msg2send_string

	def decrypt_Obj_Str_2_Txt(self, msgGot_string, ChatRef):
		msgGot = pickle.loads(msgGot_string)
		if not self.F_Public_key.verify(msgGot.msg, (msgGot.sign, None)):
			log.warn('the message below is FAKE!!!')
		encstr = msgGot.msg
		txtGot = self.M_Private_key.decrypt(encstr)
		SenderInfo = msgGot.info
		return txtGot, SenderInfo
