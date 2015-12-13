import socket
import threading
import CryptoChat
import Chat
import UI
#CryptoChat
M_Private_key=None
F_Public_key=None
Myname=None
#Chat UI modules
tosend=None
toclose=False
tosend=''
PeerIp=''
port=0
PeerAddr=('',0)

listensoc=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

UI.ui(raw_input("Choose how to setup a connection enter 'm' for Myserver/ 'p' for public server  "),listensoc) # if added more option add description to here

Chat.subc(raw_input("Do you wish to send your info to data base? 'y'/'n' "),listensoc)
Chat.getClient(raw_input("Do you wish to ask for info from the data base? 'y'/'n' "),listensoc)
CryptoChat.cryptoUI()
PeerIp=raw_input("Enter peer ip:")
port=int(raw_input("enter port to connect: "))
PeerAddr=(PeerIp,port)

tlisten=threading.Thread(target=Chat.acceptReq,args=(listensoc,toclose))
tlisten.start()
tjunk=threading.Thread(target=Chat.sendjunk,args=(listensoc,PeerAddr))
tjunk.start()
Chat.sendUsr(listensoc,PeerAddr)