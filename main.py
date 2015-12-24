import Chat
from ExternalServer import ExternalServer

###########################################
TEST = False
# in this case run in two different consoles
# on the same machine first time
# python main.py a
# second time
# python main.py b
###########################################

external_server = ExternalServer()
chatRef = Chat.Chat(external_server)
if not TEST:
	external_server.connect_to_server()
	chatRef.execute()
else:
	external_server.test_flight()
	chatRef.execute_test()
