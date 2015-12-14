import time
import datetime
import CryptoChat

Max_Port_Length=5
Buffer_Size=0x100
Big_buffer_Size=0x2048*2
def acceptReq(socket,close):
	global listensoc
	listensoc=socket
	global toclose
	toclose=close

	print "--Waiting for connection--"
	try:
		while toclose!=True:
			data,PeerAddr=listensoc.recvfrom(Big_buffer_Size)	
			if data.startswith('xxx'):
				txtDecrypted,sender=CryptoChat.decrypt_Obj_Str_2_Txt(data[3:])
				if txtDecrypted='q':
					break
				print sender+': '+txtDecrypted+"       -"+datetime.datetime.now().strftime("%H:%M-")

	finally:
		toclose=True
		print "--Connection closed--"


def sendjunk(socket,addr,close):
	global listensoc
	listensoc=socket
	global PeerAddr
	PeerAddr=addr
	global toclose
	toclose=close
	while toclose!=True:
		listensoc.sendto(b'hi',PeerAddr)
		time.sleep(0.3)
		if toclose==True:
			print "keep alive connection sending stopped"
			break


def sendUsr(socket,addr):
	global listensoc
	listensoc=socket
	global PeerAddr
	PeerAddr=addr

	print "sending to:  "+str(PeerAddr)
	print "--Enter what to send, q to quit--"
	while True:
		tosend=raw_input()
		if tosend:
			try:
				encInput=CryptoChat.encrypt_Txt_2_Obj_Str(tosend)
			except BaseException:
				print 'bad encryption'
			msg='xxx'+encInput
			listensoc.sendto(msg,PeerAddr)#remember to change
		else:
			print "--Send Connection closed by YOU!--"
			break;

def subc(subcs,socket):
	global listensoc
	listensoc=socket
	got_answer=False
	if subcs=='y':
		listensoc.sendto('1'.encode('utf-8'),(raw_input("enter ip of connector"),int(raw_input("enter connector port"))))
		while got_answer=False:
			data,ConAddr=listensoc.recvfrom(Buffer_Size)
			strdata=data.decode('utf-8')
			if len(strdata)>Max_Port_Length:
				print strdata
				got_answer=True

def getClient(gets,socket):
	global listensoc
	listensoc=socket
	got_answer=False
	if gets=='y':
		cid=raw_input("Enter Client id to get info of:")
		listensoc.sendto(('get_client '+cid).encode('utf-8'),(raw_input("enter ip of connector"),int(raw_input("enter connector port"))))
		while got_answer=False:
			data,ConAddr=listensoc.recvfrom(Buffer_Size)
			if len(data.decode('utf-8'))>Max_Port_Length:
					print data.decode('utf-8')
					got_answer=True