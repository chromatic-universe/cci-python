# kc_tcp.py   william k. johnson 2016


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
import struct
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
def get_default_gateway_linux() :
			"""
			read the default gateway directly from /proc.
			"""

			with open( "/proc/net/route" ) as fh :
				for line in fh:
					fields = line.strip().split()
					if fields[1] != '00000000' or not int( fields[3] , 16) & 2 :
						continue
					return socket.inet_ntoa ( struct.pack ( "<L" , int( fields[2], 16 ) ) )




# ---------------------------------------------------------------------------------------------
def syn_ack_scan( ip=None , port=80 ) :
				"""

				:param ip:
				:param port_range:
				:return:
				"""

				reply = None
				try :

					reply = sr1( IP( dst = ip )/ TCP( dport = int( port ) ,flags = 'S') , timeout=5 )
					if reply :
						print reply.display()

				except Exception  as e :
					print e.message
					sys.exit( 1 )

				return reply



# ---------------------------------------------------------------------------------------------
def syn_ack_ports( ip  = None , port_range = None ) :
				"""
				:param ip:
				:param port_range:
				:return:
				"""

				if port_range.find( ':' ) != -1 :
					# tuple range
					begin , end = port_range.split( ':' )

					try :

						ans , unans = sr( IP ( dst= ip )/TCP( sport = 666 ,
															   dport = ( int( begin ) , int( end ) ) ,
															   flags = "S" ) , timeout=20 )
						print 'answered:'
						print ans.summary( lambda( s ,r ) : r.sprintf( "%TCP.sport% \t %TCP.flags%" ) )

					except Exception  as e :
						print e.message
						sys.exit( 1 )
				elif port_range.find( ',' ) != -1 :
					# set
					try :
						p =  [int(x) for x in port_range.split( ',' )]
						ans , unans = sr( IP ( dst= ip )/TCP( sport = 666 ,
															   dport = ( p ) ,
															   flags = "S" ) , timeout=10)
						print 'answered:'
						print ans.summary( lambda( s ,r ) : r.sprintf( "%TCP.sport% \t %TCP.flags%" ) )

					except Exception  as e :
						print e.message
						sys.exit( 1 )







# ------------------------------------------------------------------------------------
if __name__ == '__main__' :


			parser = argparse.ArgumentParser()
			parser.add_argument('-s', action='store', dest='syn_ip',
						help='single syn ip  value')
			parser.add_argument('-p', action='store', dest='syn_port',
						help='syn ack port scan')
			parser.add_argument('-r', action='store', dest='syn_range',
						help='syn ack port scan')

			args = parser.parse_args()



			if args.syn_ip and args.syn_port :

				syn_ack_scan( args.syn_ip , args.syn_port )

				sys.exit( 0 )

			if args.syn_ip and args.syn_range :

				syn_ack_ports( args.syn_ip , args.syn_range )

				sys.exit( 0 )




