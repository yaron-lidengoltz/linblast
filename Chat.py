import time
import datetime
import threading
import CryptoChat

Max_Port_Length = 5
Buffer_Size = 0x100
Big_buffer_Size = 0x2048 * 2
Junk=b'hi'
ResendRequest='^_^Resend^_^' #a string that represents a request to resend
Prolouge='xxx'
RandomAdress=('8.8.8.8',80)

class ChatClass(object):
	CryptoRef=None
	listensoc=None
	PeerAddr=None
	toClose=False
	LastSent=''
	toSend=None
	def __init__(self, Socket):
		self.listensoc = Socket
		tKeepAlive=threading.Thread(target=self.KeepAlive,args=())
		tKeepAlive.start()
		self.CryptoRef=CryptoChat.CryptoClass()
	def Execute(self):

		self.subc(raw_input("Do you wish to send your info to data base? 'y'/'n' "))
		self.getClient(raw_input("Do you wish to ask for info from the data base? 'y'/'n' "))
		PeerIp=raw_input("Enter peer ip:")
		port=int(raw_input("enter port to connect: "))
		self.PeerAddr=(PeerIp,port)
		tjunk=threading.Thread(target=self.sendjunk,args=())
		tjunk.start()
		tlisten=threading.Thread(target=self.acceptReq,args=())
		tlisten.start()
		self.sendUsr()
	def acceptReq(self):
		print "--Waiting for connection--"
		while not self.toClose:
			try:
				data, PeerAddr = self.listensoc.recvfrom(Big_buffer_Size)
			except BaseException:
				self.toClose=True
				print "--Connection closed by peer--"
				exit(0)
			if data.startswith(Prolouge):
				txtDecrypted, sender = self.CryptoRef.decrypt_Obj_Str_2_Txt(data[3:],self)
				if txtDecrypted == 'q':
					break
				if txtDecrypted==ResendRequest:
					self.ResendMsg()
					continue
				print sender + ': ' + txtDecrypted + "       -" + datetime.datetime.now().strftime("%H:%M-")	
		print "--Listening Connection closed by you--"	
		exit(0)

	def sendjunk(self):
		while not self.toClose:
			self.listensoc.sendto(Junk, self.PeerAddr)
			time.sleep(0.3)
		print "keep alive connection sending stopped"
		exit(0)


	def sendUsr(self):
		print "sending to:  " + str(self.PeerAddr)
		print "--You can start chating, press Enter to quit--"
		while not self.toClose:
			toSend = raw_input()
			if toSend != '':
#				try:
				encInput = self.CryptoRef.encrypt_Txt_2_Obj_Str(toSend)
#				except BaseException:
#					print 'bad encryption'
				self.LastSent=toSend
				msg = Prolouge + encInput
				self.listensoc.sendto(msg, self.PeerAddr)  # remember to change
			else:
				self.toClose = True
				encInput = self.CryptoRef.encrypt_Txt_2_Obj_Str('q')
				msg = Prolouge + encInput
				self.listensoc.sendto(msg, self.PeerAddr) 
				print "--Send Connection closed by YOU!--"

	def ReqResend(self):
		encInput = self.CryptoRef.encrypt_Txt_2_Obj_Str(ResendRequest)
		msg = Prolouge + encInput
		self.listensoc.sendto(msg, self.PeerAddr)

	def ResendMsg(self):
		print 'Resending: '+self.LastSent+' ...'
		encInput = self.CryptoRef.encrypt_Txt_2_Obj_Str(self.LastSent)
		msg = Prolouge + encInput
		self.listensoc.sendto(msg, self.PeerAddr)

	def subc(self,subcs):
		got_answer = False
		if subcs == 'y':
			self.listensoc.sendto('1'.encode('utf-8'),(raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
			while not got_answer:
				data, ConAddr = self.listensoc.recvfrom(Buffer_Size)
				strdata = data.decode('utf-8')
				if len(strdata) > Max_Port_Length:
					print strdata
					got_answer = True


	def getClient(self,gets):
		got_answer = False
		if gets == 'y':
			cid = raw_input("Enter Client id to get info of:")
			self.listensoc.sendto(('get_client ' + cid).encode('utf-8'), (raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
			while not got_answer:
				data, ConAddr =self.listensoc.recvfrom(Buffer_Size)
				if len(data.decode('utf-8')) > Max_Port_Length:
					print data.decode('utf-8')
					got_answer = True

	def KeepAlive(self):
		for i in range(99):
			self.listensoc.sendto(b'KeepAlive', RandomAdress)
			time.sleep(0.5)