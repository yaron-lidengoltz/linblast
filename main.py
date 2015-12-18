import Chat
from ExternalServer import ExternalServer

TEST = True

external_server = ExternalServer()
chatRef = Chat.Chat(external_server)
if not TEST:
	external_server.connect_to_server()
	chatRef.execute()
else:
	external_server.test_flight()
	chatRef.execute_test()
