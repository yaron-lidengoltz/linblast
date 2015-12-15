import time
import datetime
import CryptoChat

Max_Port_Length = 5
Buffer_Size = 0x100
Big_buffer_Size = 0x2048 * 2


def acceptReq(listensoc, toclose, FriendKey, MyKey):
	print "--Waiting for connection--"
	try:
		while toclose != True:
			data, PeerAddr = listensoc.recvfrom(Big_buffer_Size)
			if data.startswith('xxx'):
				txtDecrypted, sender = CryptoChat.decrypt_Obj_Str_2_Txt(data[3:], FriendKey, MyKey)
				if txtDecrypted == 'q':
					break
				print sender + ': ' + txtDecrypted + "       -" + datetime.datetime.now().strftime("%H:%M-")

	finally:
		# !-- logically i don't understand why do you need to reassign it to True
		toclose = True
		print "--Connection closed--"


def sendjunk(listensoc, PeerAddr, toclose):
	# !-- Wouldn't it be nicer to while not toClose: ?
	while toclose != True:
		# !-- hi should be constant
		listensoc.sendto(b'hi', PeerAddr)
		time.sleep(0.3)
		# !-- use instead if toClose:
		if toclose == True:
			print "keep alive connection sending stopped"
			break


def sendUsr(listensoc, PeerAddr, FriendKey, MyKey, Myname):
	print "sending to:  " + str(PeerAddr)
	print "--Enter what to send, q to quit--"
	while True:
		tosend = raw_input()
		if tosend:
			try:
				encInput = CryptoChat.encrypt_Txt_2_Obj_Str(tosend, FriendKey, MyKey, Myname)
			except BaseException:
				print 'bad encryption'
			# !-- use constant instead xxx
			msg = 'xxx' + encInput
			listensoc.sendto(msg, PeerAddr)  # remember to change
		else:
			print "--Send Connection closed by YOU!--"
			# !-- NO ; in python
			break;


def subc(subcs, listensoc, RandomAdress):
	got_answer = False
	if subcs == 'y':
		listensoc.sendto('1'.encode('utf-8'),(raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
		# !-- use while not got_answer:
		while got_answer == False:
			data, ConAddr = listensoc.recvfrom(Buffer_Size)
			strdata = data.decode('utf-8')
			if len(strdata) > Max_Port_Length:
				print strdata
				got_answer = True
	else:
		KeepAlive(listensoc, RandomAdress)


def getClient(gets, listensoc, RandomAdress):
	got_answer = False
	if gets == 'y':
		cid = raw_input("Enter Client id to get info of:")
		listensoc.sendto(('get_client ' + cid).encode('utf-8'), (raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
		# !-- use while not got_answer:
		while got_answer == False:
			data, ConAddr = listensoc.recvfrom(Buffer_Size)
			if len(data.decode('utf-8')) > Max_Port_Length:
				print data.decode('utf-8')
				got_answer = True
	else:
		KeepAlive(listensoc, RandomAdress)


def KeepAlive(MySocket, RandomAdress):
	MySocket.sendto(b'KeepAlive', RandomAdress)
