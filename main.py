import socket
import Chat
import UI

listensoc=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

UI.ui(raw_input("Choose how to setup a connection enter 'm' for Myserver/ 'p' for public server  "),listensoc) # if added more option add description to here
chatRef=Chat.ChatClass(listensoc)
chatRef.Execute()



