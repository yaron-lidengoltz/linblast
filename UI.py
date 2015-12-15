import stun

def ui(ch,socket):
	if (ch=='m'):
		uiMyserver(socket)
	elif (ch=='p'):
		uiStunserver(socket)
	else:
		uiMyserver(socket)

def uiStunserver(listensock):

	local_port=int(raw_input("enter port to listen: "))
	nat_type, Myip, port = stun.get_ip_info('0.0.0.0',local_port)
	if Myip=="" or Myip=="none":
		print "Stun request falied! switching to manual server"
		uiMyserver(socket)
	else:
		listenAddr=('0.0.0.0',local_port)
		listensock.bind(listenAddr)
		print "your ip is: '"+Myip+ "' and your port is: '"+str(port)+"'"

def uiMyserver(listensock):

	listenport=int(raw_input("enter port to listen: "))
	listenAddr=('0.0.0.0',listenport)
	listensock.bind(listenAddr)