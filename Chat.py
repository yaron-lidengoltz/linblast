import logging
import threading
import time
import cPickle as pickle
import CryptoChat
import AudioChat

MAX_PORT_LENGTH = 5
BUFFER_SIZE = 0x100
BIG_BUFFER_SIZE = 0x2048 * 2
MAX_KEY_ROTATION=15

RESEND_REQUEST_STRING = '^_^Resend^_^'  # a string that represents a request to resend
VOICE_PROLOGUE='VVV'
JUNK_PROLOGUE='www'
PROLOGUE = 'xxx'
MACHINE_PROLOGUE = 'YYY'
INIT_PROLOUGE='ZZZ'
JUNK_STRING = 'hi'
RANDOM_ADDRESS = ('8.8.8.7', 80)

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

		self.Peer_Address = None
		self.ToClose = threading.Event()
		self.LastMessage = ''
		self.ToSend = None
		self.ConnectedToPeer=threading.Event()
		self.Server = server
		self.Listen_Socket = server.linsocket
		self.CryptoRef = CryptoChat.CryptoClass()
		self.User_Me=User()
		self.PhoneBook=None
		self.Char_INT=None
		self.AudioRef=AudioChat.ChatAudio()
		self.VoiceOperation=False

	def init_thread(self, method, args):
		holder = threading.Thread(target=method, args=args)
		holder.daemon = True
		self.threads.append(holder)
		return holder

	def execute_test(self):
		self.Peer_Address = (self.Server.my_ip, 5555 if self.Server.user == 'a' else 6666)
		time.sleep(5)
		self.keepAlive_thread.start()
		self.CryptoRef.test_flight(self.Server.user)
		self.User_Me.initME(self.CryptoRef.my_name,self.Server.listen_address,self.CryptoRef.M_Public_key,time.time())
		self.PhoneBook={self.User_Me.name:self.User_Me}
		self.start_threads()

	def execute(self):
		self.keepAlive_thread.start()
		self.CryptoRef.init_chat()
		self.User_Me.initME(self.CryptoRef.my_name,self.Server.listen_address,self.CryptoRef.M_Public_key,time.time())
		self.PhoneBook={self.User_Me.name:self.User_Me}
		#self.send_user_details_to_db()
		#self.get_phone_book_from_db()
		peer_ip = raw_input("Enter peer ip:")
		port = int(raw_input("enter port to connect: "))
		self.Peer_Address = (peer_ip, port)
		self.start_threads()

	def start_threads(self):
		self.junk_thread.start()
		self.listen_thread.start()
		self.start_chat()


	def accept_requests(self):
		Voice_Msg_Buffer=''
		AddToBufferFlag=False
		log.info('--Waiting for connection--')
		while not self.ToClose.isSet():
			try:
				data, peer_address = self.Listen_Socket.recvfrom(BIG_BUFFER_SIZE*12)
			except Exception, e:
				log.error('Exception caught')
				log.error('--Connection closed by peer--')
				self.ToClose.set()
				break

			if data.startswith(MACHINE_PROLOGUE):
				self.Change_key(2)
				data, sender = self.CryptoRef.Decrypt_AES(data[3:],2)
				if data.startswith('q'):           #q=quit
					log.info('%s Asked to quit!' % sender)
					break
				if data.startswith('p'):           #p=phonebook
					log.info('%s sent you his phonebook!' % sender)
					data=data[1:]                  #cutting the "p"
					self.UpdatePhoneBook(pickle.loads(data)) 
					print self.PhoneBook    
				if data == RESEND_REQUEST_STRING:
					log.info('%s asked for a resend' % sender)
					self.resend_message()
					continue

			elif data.startswith(PROLOGUE):
				self.Change_key(1)
				data, sender = self.CryptoRef.Decrypt_AES(data[3:],1)
				log.info('%s: %s' % (sender, data))

			elif data.startswith(VOICE_PROLOGUE):
				self.Change_key(1)
				data, sender = self.CryptoRef.Decrypt_AES(data[3:],1)
				if data=='start_record':
					started=time.time()
					print 'got audio'
					AddToBufferFlag=True
					continue
				elif data=='stop_record':
					print 'audio finished'
					AddToBufferFlag=False
					self.AudioRef.Play(Voice_Msg_Buffer)
					Voice_Msg_Buffer=''
					continue
				if AddToBufferFlag:
					Voice_Msg_Buffer+=data
					continue

				ended=time.time()
				if (ended-started)>7:
					AddToBufferFlag=False
					self.AudioRef.Play(Voice_Msg_Buffer)
					Voice_Msg_Buffer=''


			elif data.startswith(JUNK_PROLOGUE):
				continue
			elif data.startswith(INIT_PROLOUGE):
				continue
			else:
				log.warn('Got some weird message %s' % data)
		log.info('--Listening Connection closed by you--')

	def send_junk(self):
		while not self.ToClose.isSet():
			if self.Char_INT==None:
				self.Char_INT='j'
				self.Interrupt_Service()
			time.sleep(1)
		log.info('keep alive connection sending stopped')

	def start_chat(self):
		log.info('sending to: %s' % str(self.Peer_Address))
		log.info('--You can start chatting, press ctrl c to quit--')
		self.InitiateChat()
		time.sleep(2)
		self.ConnectedToPeer.set()
		time.sleep(2)
		self.SendPhoneBook_thread.start()
		while not self.ToClose.isSet():
			try:
				txt_to_send = raw_input()
				if txt_to_send != '':
					if txt_to_send=='record':
						self.VoiceOperation=True
						try:
							frames=self.AudioRef.Record()
						except BaseException:
							print 'no recording device'
							self.VoiceOperation=False
							continue
						self.Change_key(1)
						encrypted_txt = self.CryptoRef.Encrypt_AES('start_record',1)
						msg = VOICE_PROLOGUE + encrypted_txt
						self.Listen_Socket.sendto(msg, self.Peer_Address)
						FrameCount = len(frames)

						for i in range(0,FrameCount):
							txt_to_send=str(frames[i])
							self.Change_key(1)
							encrypted_txt = self.CryptoRef.Encrypt_AES(txt_to_send,1)
							msg = VOICE_PROLOGUE + encrypted_txt
							self.Listen_Socket.sendto(msg, self.Peer_Address)

						self.Change_key(1)
						encrypted_txt = self.CryptoRef.Encrypt_AES('stop_record',1)
						msg = VOICE_PROLOGUE + encrypted_txt
						self.Listen_Socket.sendto(msg, self.Peer_Address)
					else:
						self.Change_key(1)
						encrypted_txt = self.CryptoRef.Encrypt_AES(txt_to_send,1)
						self.LastMessage = txt_to_send
						msg = PROLOGUE + encrypted_txt
						self.Listen_Socket.sendto(msg, self.Peer_Address)
						self.VoiceOperation=False
			except KeyboardInterrupt, e:
				self.Char_INT='q'
				self.Interrupt_Service()
				self.ToClose.set()
				log.info('--Send Connection closed by YOU!--')

	def InitiateChat(self):
		got_answer=False
		got_msg=False
		data=''
		InitMsgThread=self.init_thread(self.Send_initiate_MSG,())
		InitMsgThread.start()
		while not got_answer:
			while not got_msg:
				data, peer_address = self.Listen_Socket.recvfrom(BIG_BUFFER_SIZE)
				if data.startswith(INIT_PROLOUGE):
					got_msg=True
			data,sender=self.CryptoRef.Decrypt_RSA(data[3:])                #cuts the proluge
			PeerPriority=int(data[0:2])    #first 2 characters
			PeerKey=data[2:18]             #next 16       key-1
			PeerIv=data[18:34]             #other next 16 iv-1
			PeerKey2=data[34:50]           #other next 16 key-2
			PeerIv2=data[50:66]            #other next 16 iv-2
			if PeerPriority<self.CryptoRef.Init_Priority:
				self.CryptoRef.Update_AES_Ref(PeerKey,PeerIv,1)
				self.CryptoRef.Update_AES_Ref(PeerKey2,PeerIv2,2)
				log.info('Peer key chosen') 
			elif PeerPriority==self.CryptoRef.Init_Priority:
				self.InitiateChat()
			else:
				log.info('My key chosen')	
			print self.CryptoRef.PrintKey(self.CryptoRef.AES_KEY)
			print self.CryptoRef.PrintKey(self.CryptoRef.AES_KEY2)
			got_answer=True

	def request_resend(self):
		self.Change_key(2)
		msg = MACHINE_PROLOGUE + self.CryptoRef.Encrypt_AES(RESEND_REQUEST_STRING,2)
		self.Listen_Socket.sendto(msg, self.Peer_Address)

	def resend_message(self):
		log.info('Resending: %s' % self.LastMessage)
		self.Change_key(1)
		msg = PROLOGUE + self.CryptoRef.Encrypt_AES(self.LastMessage,1)
		self.Listen_Socket.sendto(msg, self.Peer_Address)

	def send_user_details_to_db(self):
		got_answer = False
		if raw_input("Do you wish to send your info to data base? 'y'/'n' ") == 'y':
			# !-- fix it by yourself
			self.Listen_Socket.sendto('1'.encode('utf-8'),
			                          (raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
			while not got_answer:
				data, ConAddr = self.Listen_Socket.recvfrom(BUFFER_SIZE)
				strdata = data.decode('utf-8')
				if len(strdata) > MAX_PORT_LENGTH:
					print strdata
					got_answer = True

	def get_phone_book_from_db(self):
		got_answer = False
		if raw_input("Do you wish to ask for info from the data base? 'y'/'n' ") == 'y':
			# !-- fix it by yourself
			cid = raw_input("Enter Client id to get info of:")
			self.Listen_Socket.sendto(('get_client ' + cid).encode('utf-8'),
			                          (raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
			while not got_answer:
				data, ConAddr = self.Listen_Socket.recvfrom(BUFFER_SIZE)
				if len(data.decode('utf-8')) > MAX_PORT_LENGTH:
					print data.decode('utf-8')
					got_answer = True

	def keep_alive(self):
		while not self.ConnectedToPeer.isSet():
			RANDOM_ADDRESS=self.CryptoRef.InventAdress()
			self.Listen_Socket.sendto(b'KeepAlive', RANDOM_ADDRESS)
			time.sleep(0.1)

	def SendPhoneBook(self):
		while not self.ToClose.isSet():
			self.Char_INT='p'
			self.Interrupt_Service()
			time.sleep(15)
	def UpdatePhoneBook(self,NewPhoneBook):
		Copy={}  #Copy is a copy of the incoming dictionary without merging conflicts 
		Copy.update(NewPhoneBook)
		for n in NewPhoneBook:
			if self.PhoneBook.has_key(n):
				if NewPhoneBook[n].timestamp<self.PhoneBook[n].timestamp:
					self.PhoneBook[n].timestamp=NewPhoneBook[n].timestamp
				del Copy[n]
		if len(Copy)>0:
			self.PhoneBook.update(Copy)

	def Change_key(self,number):
		if number==1:
			RotatedKey=self.CryptoRef.Shuffle(self.CryptoRef.AES_KEY)
			RotatedIV=self.CryptoRef.Shuffle(self.CryptoRef.AES_IV)
			self.CryptoRef.Update_AES_Ref(RotatedKey,RotatedIV,1)
		if number==2:
			RotatedKey=self.CryptoRef.Shuffle(self.CryptoRef.AES_KEY2)
			RotatedIV=self.CryptoRef.Shuffle(self.CryptoRef.AES_IV2)
			self.CryptoRef.Update_AES_Ref(RotatedKey,RotatedIV,2)

	def Interrupt_Service(self):
			if self.Char_INT=='q':
				self.Change_key(2)
				msg = MACHINE_PROLOGUE + self.CryptoRef.Encrypt_AES('q',2)
				self.Listen_Socket.sendto(msg, self.Peer_Address)
				self.Char_INT=None

			if self.Char_INT=='p' and self.VoiceOperation==False:
				self.Change_key(2)
				PhoneBook_String=pickle.dumps(self.PhoneBook)
				msg = MACHINE_PROLOGUE + self.CryptoRef.Encrypt_AES('p'+PhoneBook_String,2)
				self.Listen_Socket.sendto(msg, self.Peer_Address)
				self.Char_INT=None

			if self.Char_INT=='j':
				self.Listen_Socket.sendto(JUNK_PROLOGUE+JUNK_STRING, self.Peer_Address)
				self.Char_INT=None
			time.sleep(1)

	def Send_initiate_MSG(self):
		while not self.ConnectedToPeer.isSet():
			infokey=self.CryptoRef.AES_KEY+self.CryptoRef.AES_IV
			infokey2=self.CryptoRef.AES_KEY2+self.CryptoRef.AES_IV2
			msg =INIT_PROLOUGE+self.CryptoRef.Encrypt_RSA(str(self.CryptoRef.Init_Priority)+infokey+infokey2)
			self.Listen_Socket.sendto(msg, self.Peer_Address)
			time.sleep(0.1)


