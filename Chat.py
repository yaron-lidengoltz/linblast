import time
import datetime
import CryptoChat

def acceptReq(socket,close):
	global listensoc
	listensoc=socket
	global toclose
	toclose=close

	print "--Waiting for connection--"
	try:
		while True:
			try:
				data,PeerAddr=listensoc.recvfrom(0x2048*2)	
			except Exception:
				print "Peer Disconnected"
				break
			datastr=data
			#print data
			if datastr[0]=='x' and datastr[1]=='x' and datastr[2]=='x' :
				#print 'Peer: '+datastr[3:]
				txtDecrypted,sender=CryptoChat.decrypt_Obj_Str_2_Txt(datastr[3:])
				print sender+': '+txtDecrypted+"       -"+datetime.datetime.now().strftime("%H:%M-")
			elif datastr==('xxxq'):	
				break
			#if (datastr!=('xxxq') and datastr[0]!='x'):
			#	print("junk:"+datastr)

	finally:
		toclose=True
		print "--Connection closed--"


def sendjunk(socket,addr):
	global listensoc
	listensoc=socket
	global PeerAddr
	PeerAddr=addr

	while True:
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
		#try:
		tosend=raw_input()
		encInput=CryptoChat.encrypt_Txt_2_Obj_Str(tosend)
		#except BaseException:
		#	print 'bad encryption'
		msg='xxx'+encInput
		if msg!='xxx':
			listensoc.sendto(msg,PeerAddr)#remember to change
		else:
			print "--Send Connection closed by YOU!--"
			break;

def subc(subcs,socket):
	global listensoc
	listensoc=socket
	print subcs
	if subcs=='y':
		listensoc.sendto('1'.encode('utf-8'),(raw_input("enter ip of connector"),int(raw_input("enter connector port"))))
		while True:
			data,ConAddr=listensoc.recvfrom(0x100)
			strdata=data.decode('utf-8')
			if len(strdata)>5:
				print strdata
				break;
def getClient(gets,socket):
	global listensoc
	listensoc=socket

	if gets=='y':
		cid=raw_input("Enter Client id to get info of:")
		listensoc.sendto(('get_client '+cid).encode('utf-8'),(raw_input("enter ip of connector"),int(raw_input("enter connector port"))))
		while True:
			data,ConAddr=listensoc.recvfrom(0x100)
			if len(data.decode('utf-8'))>5:
					print data.decode('utf-8')
					break;