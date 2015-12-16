import time
import datetime
import CryptoChat

Max_Port_Length = 5
Buffer_Size = 0x100
Big_buffer_Size = 0x2048 * 2
toSend=None
Junk=b'hi'
ResendRequest='^_^Resend^_^' #a string that represents a request to resend
LastSent=''
Prolouge='xxx'
toClose=False

def acceptReq(listensoc, FriendKey, MyKey,Myname):
	global LastSent
	global toClose
	print "--Waiting for connection--"
	while not toClose:
		try:
			data, PeerAddr = listensoc.recvfrom(Big_buffer_Size)
		except BaseException:
			toClose=True
			print "--Connection closed by peer--"
			exit(0)
		if data.startswith(Prolouge):
			txtDecrypted, sender = CryptoChat.decrypt_Obj_Str_2_Txt(data[3:], FriendKey, MyKey,listensoc,PeerAddr,Myname)
			if txtDecrypted == 'q':
				break
			if txtDecrypted==ResendRequest:
				ResendMsg(listensoc,PeerAddr,FriendKey,MyKey,Myname,LastSent)
				continue
			print sender + ': ' + txtDecrypted + "       -" + datetime.datetime.now().strftime("%H:%M-")	
	print "--Listening Connection closed by you--"	
	exit(0)




def sendjunk(listensoc, PeerAddr):
	global toClose
	while not toClose:
		listensoc.sendto(Junk, PeerAddr)
		time.sleep(0.3)
	print "keep alive connection sending stopped"
	exit(0)


def sendUsr(listensoc, PeerAddr, FriendKey, MyKey, Myname):
	global LastSent
	global toClose
	print "sending to:  " + str(PeerAddr)
	print "--You can start chating, press Enter to quit--"
	while not toClose:
		toSend = raw_input()
		if toSend != '':
			try:
				encInput = CryptoChat.encrypt_Txt_2_Obj_Str(toSend, FriendKey, MyKey, Myname)
			except BaseException:
				print 'bad encryption'
			LastSent=toSend
			msg = Prolouge + encInput
			listensoc.sendto(msg, PeerAddr)  # remember to change
		else:
			toClose = True
			print "--Send Connection closed by YOU!--"
			exit(0)

def ReqResend(listensoc, PeerAddr, FriendKey, MyKey, Myname):
	encInput = CryptoChat.encrypt_Txt_2_Obj_Str(ResendRequest, FriendKey, MyKey, Myname)
	msg = Prolouge + encInput
	listensoc.sendto(msg, PeerAddr)

def ResendMsg(listensoc, PeerAddr, FriendKey, MyKey, Myname,ToSendAgain):
	encInput = CryptoChat.encrypt_Txt_2_Obj_Str(ToSendAgain, FriendKey, MyKey, Myname)
	msg = Prolouge + encInput
	listensoc.sendto(msg, PeerAddr)

def subc(subcs, listensoc):
	got_answer = False
	if subcs == 'y':
		listensoc.sendto('1'.encode('utf-8'),(raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
		while not got_answer:
			data, ConAddr = listensoc.recvfrom(Buffer_Size)
			strdata = data.decode('utf-8')
			if len(strdata) > Max_Port_Length:
				print strdata
				got_answer = True


def getClient(gets, listensoc):
	got_answer = False
	if gets == 'y':
		cid = raw_input("Enter Client id to get info of:")
		listensoc.sendto(('get_client ' + cid).encode('utf-8'), (raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
		while not got_answer:
			data, ConAddr = listensoc.recvfrom(Buffer_Size)
			if len(data.decode('utf-8')) > Max_Port_Length:
				print data.decode('utf-8')
				got_answer = True



def KeepAlive(MySocket, RandomAdress):
	for i in range(99):
		MySocket.sendto(b'KeepAlive', RandomAdress)
		time.sleep(0.5)