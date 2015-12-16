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
RandomAdress=('8.8.8.8',80)
PeerIp=''
port=0
PeerAddr=('',0)

listensoc=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

UI.ui(raw_input("Choose how to setup a connection enter 'm' for Myserver/ 'p' for public server  "),listensoc) # if added more option add description to here
tKeepAlive=threading.Thread(target=Chat.KeepAlive,args=(listensoc,RandomAdress))
tKeepAlive.start()
Chat.subc(raw_input("Do you wish to send your info to data base? 'y'/'n' "),listensoc)
Chat.getClient(raw_input("Do you wish to ask for info from the data base? 'y'/'n' "),listensoc)
PeerIp=raw_input("Enter peer ip:")
port=int(raw_input("enter port to connect: "))
PeerAddr=(PeerIp,port)
tjunk=threading.Thread(target=Chat.sendjunk,args=(listensoc,PeerAddr))
tjunk.start()
(M_Private_key,F_Public_key,Myname)=CryptoChat.cryptoUI()

tlisten=threading.Thread(target=Chat.acceptReq,args=(listensoc,F_Public_key,M_Private_key,Myname))
tlisten.start()
Chat.sendUsr(listensoc,PeerAddr,F_Public_key,M_Private_key,Myname)
