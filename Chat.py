import time
import datetime
import CryptoChat

# !-- Read about the python Logging
# !-- I think you should work with pycharm community edition - it would help you keep your code clean
def acceptReq(socket,close):
	#  !-- Why do you need the global in here?
	global listensoc
	listensoc = socket
	#  !-- toclose is global and local from the function??
	global toclose
	toclose = close

	print "--Waiting for connection--"
	try:
		# !-- i think it could have been nicer if you would have used the toclose instead of the true
		while True:
			try:
				# !-- 0x2048*2 should be constant
				data,PeerAddr = listensoc.recvfrom(0x2048*2)
			# !-- NEVER catch exception without understanding it or at least passing it to the user
			except Exception:
				print "Peer Disconnected"
				break

			# !-- clean the old prints
			# !-- what is the difference between data and datastr??
			datastr = data
			#print data
			# !-- what is the meaning of that? isn't that like asking datastr.startswith('xxx') and if so, isn't that
			# conflicting with the elif?
			if datastr[0] == 'x' and datastr[1] == 'x' and datastr[2] == 'x':
				#print 'Peer: '+datastr[3:]
				txtDecrypted,sender = CryptoChat.decrypt_Obj_Str_2_Txt(datastr[3:])
				print sender+': '+txtDecrypted+"       -"+datetime.datetime.now().strftime("%H:%M-")
			elif datastr == ('xxxq'):
				break
			#if (datastr!=('xxxq') and datastr[0]!='x'):
			#	print("junk:"+datastr)

	finally:
		toclose = True
		print "--Connection closed--"


# !-- to close was not passed globally in here
def sendjunk(socket,addr):
	#  !-- Why do you need the global in here?
	global listensoc
	listensoc = socket
	#  !-- PeerAddr is global and local from the function??
	global PeerAddr
	PeerAddr = addr

	# !-- i think it could have been nicer if you would have used the toclose instead of the true
	while True:
		# !-- 'hi' should be constant
		listensoc.sendto(b'hi', PeerAddr)
		time.sleep(0.3)
		if toclose == True:
			print "keep alive connection sending stopped"
			break


def sendUsr(socket, addr):
	#  !-- Why do you need the global in here?
	global listensoc
	listensoc=socket
	#  !-- PeerAddr is global and local from the function??
	global PeerAddr
	PeerAddr = addr

	print "sending to:  %s" % str(PeerAddr)
	print "--Enter what to send, q to quit--"
	while True:
		# !-- why did you remove the try?
		#try:
		tosend = raw_input()
		encInput = CryptoChat.encrypt_Txt_2_Obj_Str(tosend)
		#except BaseException:
		#	print 'bad encryption'
		msg='xxx' + encInput
		# !-- you could have checked if the encInput is empty
		# !-- i would rather reverse the condition so it would be more readable
		if msg != 'xxx':
			listensoc.sendto(msg,PeerAddr)#remember to change
		else:
			print "--Send Connection closed by YOU!--"
			break

def subc(subcs, socket):
	#  !-- Why do you need the global in here?
	global listensoc
	listensoc = socket
	# !-- why do you print it?
	print subcs

	if subcs == 'y':
		listensoc.sendto('1'.encode('utf-8'),(raw_input("enter ip of connector"),int(raw_input("enter connector port"))))
		# !-- again i think that the while True should have a condition that is related to the content
		while True:
			# !-- 0x100 should be a constant
			data,ConAddr = listensoc.recvfrom(0x100)
			strdata = data.decode('utf-8')
			# !-- why should it be greater than 5?
			if len(strdata) > 5:
				print strdata
				break

def getClient(gets,socket):
	#  !-- Why do you need the global in here?
	global listensoc
	listensoc = socket

	if gets == 'y':
		cid = raw_input("Enter Client id to get info of:")
		# !-- never use an output straight out of the raw_input, you should always check it
		listensoc.sendto(('get_client '+cid).encode('utf-8'),(raw_input("enter ip of connector"), int(raw_input("enter connector port"))))
		# !-- again i think that the while True should have a condition that is related to the content
		while True:
			# !-- 0x100 should be a constant
			data,ConAddr = listensoc.recvfrom(0x100)
			# !-- why should it be greater than 5?
			if len(data.decode('utf-8')) > 5:
					print data.decode('utf-8')
					break