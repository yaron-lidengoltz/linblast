import logging
import threading
import time
import cPickle as pickle
import CryptoChat

MAX_PORT_LENGTH = 5
BUFFER_SIZE = 0x100
BIG_BUFFER_SIZE = 0x2048 * 2

SET_DB_STRING='public:'
RESEND_REQUEST_STRING = '^_^Resend^_^'  # a string that represents a request to resend
PROLOGUE = 'xxx'
MACHINE_PROLOGUE = 'YYY'
JUNK_STRING = 'hi'
RANDOM_ADDRESS = ('8.8.8.8', 80)

log = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.setLevel(logging.DEBUG)
log.addHandler(ch)

class User(object):
	
	def __init__(self):
		self.name =None
		self.adress = None
		self.public_key =None
		self.timestamp=None
	def initME(self,name,adress,public_key,timestamp):
		self.name = name
		self.adress = adress
		self.public_key = public_key
		self.timestamp=timestamp

class Chat(object):
	def __init__(self, server):
		self.threads = []
		self.keepAlive_thread = self.init_thread(self.keep_alive, ())
		self.listen_thread = self.init_thread(self.accept_requests, ())
		self.junk_thread = self.init_thread(self.send_junk, ())
		self.SendPhoneBook_thread= self.init_thread(self.SendPhoneBook, ())

		self.peer_Address = None
		self.toClose = threading.Event()
		self.lastMessage = ''
		self.toSend = None
		self.server = server
		self.listen_socket = server.linsocket
		self.CryptoRef = CryptoChat.CryptoClass()
		self.User_Me=User()
		self.PhoneBook=None

	def init_thread(self, method, args):
		holder = threading.Thread(target=method, args=args)
		holder.daemon = True
		self.threads.append(holder)
		return holder

	def execute_test(self):
		self.peer_Address = (self.server.my_ip, 5555 if self.server.user == 'a' else 6666)
		time.sleep(5)
		self.keepAlive_thread.start()
		self.CryptoRef.test_flight(self.server.user)
		self.User_Me.initME(self.CryptoRef.my_name,self.server.listen_address,self.CryptoRef.M_Public_key,time.time())
		self.PhoneBook={self.User_Me.name:self.User_Me}
		self.start_threads()

	def execute(self):
		self.keepAlive_thread.start()
		self.CryptoRef.init_chat()
		self.User_Me.initME(self.CryptoRef.my_name,self.server.listen_address,self.CryptoRef.M_Public_key,time.time())
		self.PhoneBook={self.User_Me.name:self.User_Me}
		self.send_user_details_to_db()
		self.get_phone_book_from_db()
		peer_ip = raw_input("Enter peer ip:")
		port = int(raw_input("enter port to connect: "))
		self.peer_Address = (peer_ip, port)
		self.start_threads()

	def start_threads(self):
		self.junk_thread.start()
		self.listen_thread.start()
		self.SendPhoneBook_thread.start()
		self.start_chat()


	def accept_requests(self):
		log.info('--Waiting for connection--')
		while not self.toClose.isSet():
			try:
				data, peer_address = self.listen_socket.recvfrom(BIG_BUFFER_SIZE)
			except Exception, e:
				log.error('Exception caught')
				log.error('--Connection closed by peer--')
				self.toClose.set()
				break

			if data.startswith(MACHINE_PROLOGUE):
				data, sender = self.CryptoRef.decrypt_Obj_Str_2_Txt(data[3:], self)
				if data == 'q':           #q=quit
					log.info('%s Asked to quit!' % sender)
					break
				if data.startswith('p'):         #p=phonebook
					log.info('%s sent you his phonebook!' % sender)
					data=data[1:]         #cutting the "p"
					self.UpdatePhoneBook(pickle.loads(data))
					print self.PhoneBook
				if data == JUNK_STRING:
					continue

			elif data.startswith(PROLOGUE):
				data, sender = self.CryptoRef.decrypt_Obj_Str_2_Txt(data[3:], self)

				if data == RESEND_REQUEST_STRING:
					log.info('%s asked for a resend' % sender)
					self.resend_message()
					continue
				log.info('%s: %s' % (sender, data))
			else:
				log.warn('Got some weird message %s' % data)
	log.info('--Listening Connection closed by you--')

	def send_junk(self):
		junk = MACHINE_PROLOGUE + self.CryptoRef.encrypt_Txt_2_Obj_Str(JUNK_STRING)
		while not self.toClose.isSet():
			self.listen_socket.sendto(junk, self.peer_Address)
			time.sleep(0.9)
		log.info('keep alive connection sending stopped')

	def start_chat(self):
		log.info('sending to: %s' % str(self.peer_Address))
		log.info('--You can start chatting, press ctrl c to quit--')
		while not self.toClose.isSet():
			try:
				txt_to_send = raw_input()
				if txt_to_send != '':
					encrypted_txt = self.CryptoRef.encrypt_Txt_2_Obj_Str(txt_to_send)
					self.lastMessage = txt_to_send
					msg = PROLOGUE + encrypted_txt
					self.listen_socket.sendto(msg, self.peer_Address)
			except KeyboardInterrupt, e:
				self.toClose.set()
				encrypted_txt = self.CryptoRef.encrypt_Txt_2_Obj_Str('qaki')
				msg = MACHINE_PROLOGUE + encrypted_txt
				self.listen_socket.sendto(msg, self.peer_Address)
				log.info('--Send Connection closed by YOU!--')

	def request_resend(self):
		msg = PROLOGUE + self.CryptoRef.encrypt_Txt_2_Obj_Str(RESEND_REQUEST_STRING)
		self.listen_socket.sendto(msg, self.peer_Address)

	def resend_message(self):
		log.info('Resending: %s' % self.lastMessage)
		msg = PROLOGUE + self.CryptoRef.encrypt_Txt_2_Obj_Str(self.lastMessage)
		self.listen_socket.sendto(msg, self.peer_Address)

	def send_user_details_to_db(self):
		got_answer = False
		if raw_input("Do you wish to send your info to data base? 'y'/'n' ") == 'y':
			# !-- fix it by yourself
			self.listen_socket.sendto('1'.encode('utf-8'),
			                          (raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
			while not got_answer:
				data, ConAddr = self.listen_socket.recvfrom(BUFFER_SIZE)
				strdata = data.decode('utf-8')
				if len(strdata) > MAX_PORT_LENGTH:
					print strdata
					got_answer = True

	def get_phone_book_from_db(self):
		got_answer = False
		if raw_input("Do you wish to ask for info from the data base? 'y'/'n' ") == 'y':
			# !-- fix it by yourself
			cid = raw_input("Enter Client id to get info of:")
			self.listen_socket.sendto(('get_client ' + cid).encode('utf-8'),
			                          (raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
			while not got_answer:
				data, ConAddr = self.listen_socket.recvfrom(BUFFER_SIZE)
				if len(data.decode('utf-8')) > MAX_PORT_LENGTH:
					print data.decode('utf-8')
					got_answer = True

	def keep_alive(self):
		while not self.toClose.isSet():
			self.listen_socket.sendto(b'KeepAlive', RANDOM_ADDRESS)
			time.sleep(0.5)

	def SendPhoneBook(self):
		while not self.toClose.isSet():
			PhoneBook_String=pickle.dumps(self.PhoneBook)
			msg = MACHINE_PROLOGUE + self.CryptoRef.encrypt_Txt_2_Obj_Str('p'+PhoneBook_String)
			self.listen_socket.sendto(msg, self.peer_Address)
			time.sleep(3)
	def UpdatePhoneBook(self,NewPhoneBook):
		Copy={}  #Copy is a copy of the incoming dictionary without merging conflicts 
		Copy.update(NewPhoneBook)
		for n in NewPhoneBook:
			if self.PhoneBook.has_key(n):
				if NewPhoneBook[n].timestamp<self.PhoneBook[n].timestamp:
					self.PhoneBook[n].timestamp=NewPhoneBook[n].timestamp
				del Copy[n]
		self.PhoneBook.update(Copy)



