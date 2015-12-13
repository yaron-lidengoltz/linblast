import stun

def ui(ch,socket):
	if (ch=='m'):
		uiMyserver(socket)
	elif (ch=='p'):
		uiStunserver(socket)
	else:
		uiMyserver(socket)

def uiStunserver(socket):
	global listensoc
	listensoc=socket

	nat_type, Myip, port = stun.get_ip_info()
	if Myip=="" or Myip=="none":
		print "Stun request falied! switching to manual server"
		uiMyserver(socket)
	else:
		listenAddr=('0.0.0.0',port)
		listensoc.bind(listenAddr)
		print "your ip is: '"+Myip+ "' and your port is: '"+str(port)+"'"

def uiMyserver(socket):
	global listensoc
	listensoc=socket
	
	listenport=int(raw_input("enter port to listen: "))
	listenAddr=('0.0.0.0',listenport)
	listensoc.bind(listenAddr)