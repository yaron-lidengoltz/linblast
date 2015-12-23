import logging
import stun
import socket

import sys

log = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.setLevel(logging.DEBUG)
log.addHandler(ch)

class ExternalServer(object):
	def __init__(self):
		self.user = None
		self.listen_address = None
		self.local_port = None
		self.nat_type = None
		self.my_ip = '10.169.106.179'#!_!_!_!_!_!_!_!_!_!_!_!_!_!Remember to change to your IP
		self.port = None
		self.linsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def test_flight(self):
		self.user = sys.argv[1]
		self.local_port = 6666 if self.user == 'a' else 5555
		log.info('External address: %s:%s' % (self.my_ip, self.port))
		self.listen_address = ('0.0.0.0', self.local_port)
		log.info('Listening on address: %s:%s' % (self.listen_address[0], self.listen_address[1]))
		self.linsocket.bind(self.listen_address)

	def connect_to_server(self):
		ch = raw_input("Choose how to setup a connection\n 1.m for private server\n 2.p for public server\n")
		self.local_port = int(raw_input("enter port to listen: "))
		if ch == 'p':
			self.nat_type, self.my_ip, self.port = stun.get_ip_info('0.0.0.0', self.local_port)
			if not self.my_ip:
				log.warn('Stun request failed! switching to manual server')
			else:
				log.info('External address: %s:%s' % (self.my_ip, self.port))

		self.listen_address = ('0.0.0.0', self.local_port)
		log.info('Listening on address: %s:%s' % (self.listen_address[0], self.listen_address[1]))
		self.linsocket.bind(self.listen_address)


