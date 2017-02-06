
# kc_arp.py   william k. johnson 2016


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
import Queue
import threading
from time import gmtime, strftime , sleep


##############
'''disable ipv6 console annoyance'''
logging.getLogger( "scapy.runtime" ).setLevel(logging.ERROR)
from scapy.all import *

buf = str()

# ---------------------------------------------------------------------------------------------
def arp_display( pkt ) :
		"""

		:param pkt:
		:return:
		"""

		s = str()

		global buf
		if pkt[ARP].op == 1: #who-has (request)
			s =  "request: " + pkt[ARP].psrc + " is asking about " + pkt[ARP].pdst
			print s
		if pkt[ARP].op == 2: #is-at (response)
			s = "*response: " + pkt[ARP].hwsrc + " has address " + pkt[ARP].psrc
			print s







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



# ----------------------------------------------------------------------------------------------
def arp_scan_range( ip_range=None , timeout=2 , verbose=0 ) :
		"""


		:param ip_range:
		:param timeout:
		:param verbose:
		:return:
		"""

		try:
			alive,dead=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_range) , timeout=timeout , verbose=verbose )
			print "MAC - IP"
			for i in range(0,len(alive)) :
					print alive[i][1].hwsrc + " - " + alive[i][1].psrc
		except:
			print 'arg_scan_range failed...'
			sys.exit( 1 )


# ----------------------------------------------------------------------------------------------
def arp_atom( ip=None , timeout=1 , verbose=1 ) :
		"""

		:param ip:
		:param timeout:
		:param verbose:
		:return:
		"""

		try:
			resp = arping( ip , timeout=timeout , verbose=verbose )
			print resp

		except Exception as e :
			print 'arp_scan failed...' + e.message
			sys.exit( 1 )




# ----------------------------------------------------------------------------------------------
def arp_monitor( items = 15 ) :
		"""

		:return:		"""



		try:


				print sniff( prn=arp_display ,
							 filter="arp" ,
							 store=0 ,
							 count=items )



		except Exception as e :
			print 'arp_monitor failed...' + e.message
			sys.exit( 1 )


		print buf

		return buf




# ------------------------------------------------------------------------------------
if __name__ == '__main__' :



		parser = argparse.ArgumentParser()
		parser.add_argument('-s', action='store', dest='arp_value',
                    help='single arp value' )
		parser.add_argument('-n', action='store', dest='arp_subnet',
                    help='arp subnet' )
		parser.add_argument('-x', action='store', dest='arp_monitor',
                    help='arp monitor items' )

		args = parser.parse_args()


		if args.arp_subnet :

			arp_scan_range( args.arp_subnet )

			sys.exit( 0 )

		if args.arp_value :

			arp_atom( args.arp_value )

			sys.exit( 0 )

		if args.arp_monitor :


			arp_monitor( int( args.arp_monitor ) )

			sys.exit( 0 )