import socket
import threading
import time
import datetime
import cPickle as pickle

import stun
from Crypto.PublicKey import RSA

# !-- That should be in a different file
# !-- What is a connector and do you save it in a config file
# !-- Break in pyhton is without ;
# !-- Encrypt the config file
# !-- Clean the code from old prints

class msg(object):
	msg = ''
	info = ''
	sign = ''

	def __init__(self, text, SenderInfo, sign):
		self.msg = text
		self.info = SenderInfo
		self.sign = sign


M_Private_key = None
F_Public_key = None
Myname = None
tosend = None
toclose = False
tosend = ''
PeerIp = ''
port = 0
PeerAddr = ('', 0)


def acceptReq():
	print "--Waiting for connection--"
	try:
		while True:
			try:
				data, PeerAddr = listensoc.recvfrom(0x2048 * 2)
			except Exception:
				print "Peer Disconnected"
				break
			datastr = data
			print data
			if datastr[0] == 'x' and datastr[1] == 'x' and datastr[2] == 'x':
				print 'Peer: ' + datastr[3:]
				txtDecrypted, sender = decrypt_Obj_Str_2_Txt(datastr[3:])
				print sender + ': ' + txtDecrypted + "       -" + datetime.datetime.now().strftime("%H:%M-")
			elif datastr == ('xxxq'):
				break
			# if (datastr!=('xxxq') and datastr[0]!='x'):
			#	print("junk:"+datastr)

	finally:
		toclose = True
		print "--Connection closed--"


def sendjunk():
	global PeerAddr
	global PeerIp
	global port
	while True:
		listensoc.sendto(b'hi', PeerAddr)
		time.sleep(0.3)
		if toclose == True:
			print "keep alive connection sending stopped"
			break


def sendUsr():
	global PeerAddr
	global PeerIp
	global port
	global tosend
	print "sending to:  " + str(PeerAddr)
	print "--Enter what to send, q to quit--"
	while True:
		# try:
		tosend = raw_input()
		encInput = encrypt_Txt_2_Obj_Str()
		# except BaseException:
		#	print 'bad encryption'
		msg = 'xxx' + encInput
		if msg != 'xxx':
			listensoc.sendto(msg, PeerAddr)  # remember to change
		else:
			print "--Send Connection closed by YOU!--"
			break;


def uiStunserver():
	global PeerAddr
	global PeerIp
	global port
	nat_type, Myip, port = stun.get_ip_info()
	if Myip == "" or Myip == "none":
		print "Stun request falied! switching to manual server"
		uiMyserver()
	else:
		listenport = port
		listenAddr = ('0.0.0.0', listenport)
		listensoc.bind(listenAddr)
		print "your ip is: '" + Myip + "' and your port is: '" + str(port) + "'"


def uiMyserver():
	global PeerAddr
	global PeerIp
	global port
	listenport = int(raw_input("enter port to listen: "))
	listenAddr = ('0.0.0.0', listenport)
	listensoc.bind(listenAddr)


def cryptoUI():
	global M_Private_key
	global F_Public_key
	global Myname
	Myname = raw_input('enter your name: ')
	Friendname = raw_input('enter your friends name: ')
	try:
		M_Private_key = RSA.importKey(open("private_" + Myname + "_key.pem", "r").read())
	except BaseException:
		print "import failed!, can't import your private key "
	try:
		F_Public_key = RSA.importKey(open("public_" + Friendname + "_key.pem", "r").read())
	except BaseException:
		print "import failed!, can't import your friend's public key"


def encrypt_Txt_2_Obj_Str():
	global tosend
	global M_Private_key
	global F_Public_key
	global Myname
	(encstr,) = F_Public_key.encrypt(tosend, 65)
	# print "Encrypted form: \n"+ encstr+'\n' #debug
	(signature,) = M_Private_key.sign(encstr, 12)
	msg2send = msg(encstr, Myname, signature)
	msg2send_string = pickle.dumps(msg2send)
	return msg2send_string


def decrypt_Obj_Str_2_Txt(msgGot_string):
	global F_Public_key
	global M_Private_key
	msgGot = pickle.loads(msgGot_string)
	if F_Public_key.verify(msgGot.msg, (msgGot.sign, None)):
		encstr = msgGot.msg
		txtGot = M_Private_key.decrypt(encstr)
		SenderInfo = msgGot.info
		return txtGot, SenderInfo
	else:
		print 'Message is FAKE!!!'

# ---------------------------------------------------------
listensoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ui = raw_input(
	"Choose how to setup a connection enter 'm' for Myserver/ 'p' for public server  ")  # if added more option add description to here
if (ui == 'm'):
	uiMyserver()
elif (ui == 'p'):
	uiStunserver()
else:
	uiMyserver()

subcs = raw_input("Do you wish to send your info to data base? 'y'/'n' ")
if subcs == 'y':
	listensoc.sendto('1'.encode('utf-8'), (raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
	while True:
		data, ConAddr = listensoc.recvfrom(0x100)
		strdata = data.decode('utf-8')
		if len(strdata) > 5:
			print strdata
			break;
gets = raw_input("Do you wish to ask for info from the data base? 'y'/'n' ")
if gets == 'y':
	cid = raw_input("Enter Client id to get info of:")
	listensoc.sendto(('get_client ' + cid).encode('utf-8'),
	                 (raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
	while True:
		data, ConAddr = listensoc.recvfrom(0x100)
		if len(data.decode('utf-8')) > 5:
			print data.decode('utf-8')
			break;
cryptoUI()
PeerIp = raw_input("Enter peer ip:")
port = int(raw_input("enter port to connect: "))
PeerAddr = (PeerIp, port)


# sendsoc.bind(('0.0.0.0'),1001)

tlisten = threading.Thread(target=acceptReq)
tlisten.start()
tjunk = threading.Thread(target=sendjunk)
tjunk.start()
sendUsr()
