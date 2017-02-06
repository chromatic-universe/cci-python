# ping.py   william k. johnson 2016


log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'

import os
import sys
#############
import copy
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
##############
import logging
import argparse
import socket
import fcntl
import struct
import subprocess as proc
import urllib2
import requests


##############
'''disable ipv6 console annoyance'''
logging.getLogger( "scapy.runtime" ).setLevel(logging.ERROR)
from scapy.all import *


# ---------------------------------------------------------------------------------------------
def retr_local_ip_info() :
		"""

		:return tuple of ips:
		"""

		# local
		local_ip = '0.0.0.0'
		remote_ip = '0.0.0.0'
		s = socket.socket( socket.AF_INET , socket.SOCK_DGRAM )
		try:
			# doesn't have to be reachable
			s.connect( ('10.255.255.255', 0 ) )
			local_ip = s.getsockname()[0]

			# if using nat will differ
			#ret = urllib2.urlopen( 'https://enabledns.com/ip' , timeout=4 )

			#remote_ip = ret.read()

		except :
			try :
				local_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1],
								   [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
								   socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
			except :
				# give it up for a lost cause
				pass
				local_ip = '0.0.0.0'

		finally:
			s.close()

		print local_ip  + ':' + remote_ip + '<ip_info>'

		return local_ip , remote_ip


# ---------------------------------------------------------------------------------------------
def retr_ifconfig() :
		"""

		:return ifconfig stdout:
		"""

		# ifconfig
		cmd = ['ifconfig']
		ifconfig =  proc.check_output( cmd )

		print ifconfig

		return ifconfig


# ---------------------------------------------------------------------------------------------
def chomp( source_str , delimiter = '' , keep_trailing_delim = True ) :
		"""
		truncate and return string at last delimiter
		easy to do wiht splicing , but this function is
		more of a predicate for loop processsing

		:param delimiter :
		:param keep_trailing_delim :
		:return
		"""

		idx = source_str.rfind( delimiter )
		temp_str = str()
		if idx is not -1 :
			temp_str = source_str[:idx]
			if keep_trailing_delim is True :
				temp_str += delimiter

		return temp_str


# ---------------------------------------------------------------------------------------------
def ping_atom( destination = None ) :
		"""
		ping single addr layer 3 with scapy

		:param  destination : parses local subnet from addr:
		:return : reply obj
		"""



		ip = IP()
		ip.dst = destination

		ping = ICMP()
		ping_request = ( ip/ping )

		ping_reply = sr1( ping_request , timeout = 1 )

		return ping_request , ping_reply


# ---------------------------------------------------------------------------------------------
def ping_subnet( destination = None ) :
			"""
			ping subnet
			:param  destination , parses local subnet from addr:
			:return ping reply obj list:
			"""

			prefix = chomp( source_str = destination , delimiter = '.' , keep_trailing_delim = True )
			replies = list()

			'''
			for each address in subnet
			'''
			for addr in range( 0 , 254 ):

				try :
					#put request on wire
					print prefix + str( addr )
					reply = ping_atom( prefix + str( addr ) )
					if reply is not None :
						replies.append( reply )
						print reply.display()
				except Exception as err :
					print err

			return replies

# ------------------------------------------------------------------------------------
if __name__ == '__main__' :


		parser = argparse.ArgumentParser()
		parser.add_argument('-s', action='store', dest='ip_value',
                    help='single ip value')
		parser.add_argument('-n', action='store', dest='ip_subnet',
                    help='ip subnet')
		parser.add_argument('-g', action='store_true' , help='ifconfig')
		parser.add_argument('-x', action='store_true', help='console information')
		args = parser.parse_args()

		ip = None
		if args.ip_value :

				ip = args.ip_value

				try :

					request , reply = ping_atom( ip )

					if reply :
						print 'ping succeeded....'
						print reply.summary()
						print '<reply>'
						print reply.display()
						print  '<request>'
						print request.display()
					else :
						print 'ping failed....'
						print  '<request>'
						print request.display()
						sys.exit( 1 )

				except Scapy_Exception :
					print 'exception in comm stack...'
					sys.exit( 1 )

				sys.exit( 0 )


		if args.x :

			retr_local_ip_info()

			sys.exit( 0 )

		if args.g :

			retr_ifconfig()

			sys.exit( 0 )






