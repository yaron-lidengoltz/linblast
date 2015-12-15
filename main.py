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
tosend=None
toclose=False
tosend=''
PeerIp=''
port=0
PeerAddr=('',0)

listensoc=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

UI.ui(raw_input("Choose how to setup a connection enter 'm' for Myserver/ 'p' for public server  "),listensoc) # if added more option add description to here
Chat.subc(raw_input("Do you wish to send your info to data base? 'y'/'n' "),listensoc,RandomAdress)
Chat.getClient(raw_input("Do you wish to ask for info from the data base? 'y'/'n' "),listensoc,RandomAdress)
PeerIp=raw_input("Enter peer ip:")
port=int(raw_input("enter port to connect: "))
PeerAddr=(PeerIp,port)
tjunk=threading.Thread(target=Chat.sendjunk,args=(listensoc,PeerAddr,toclose))
tjunk.start()
(M_Private_key,F_Public_key,Myname)=CryptoChat.cryptoUI(listensoc,RandomAdress)# gets RandomAdress beacuse it calls KeepAlive()


tlisten=threading.Thread(target=Chat.acceptReq,args=(listensoc,toclose,F_Public_key,M_Private_key))
tlisten.start()
Chat.sendUsr(listensoc,PeerAddr,F_Public_key,M_Private_key,Myname)