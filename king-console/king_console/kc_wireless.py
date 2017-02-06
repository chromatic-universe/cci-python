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
import json
import requests
import pprint
from ipwhois import IPWhois

##############
'''disable ipv6 console annoyance'''
logging.getLogger( "scapy.runtime" ).setLevel(logging.ERROR)
from scapy.all import *


# ---------------------------------------------------------------------------------------------
def quick_wireless_sniff() :
			"""

			:return:
			"""
			try :

				ret = sniff(iface="wlan0",prn=lambda x:x.sprintf("{Dot11Beacon:%Dot11.addr3%\t%Dot11Beacon.info%\t%PrismHeader.channel%\tDot11Beacon.cap%}"))

			except Exception as e :
				print e.message



# ---------------------------------------------------------------------------------------------
def essid_scan() :
			"""

			:return:
			"""

			out = str()
			try :
				cmd = ['su' ,'-c' , '/system/bin/iwlist' , 'scan']
				out = proc.check_output( cmd )

			except proc.CalledProcessError as e :

				return e.message

			return out



# ---------------------------------------------------------------------------------------------
def ip_geography( ip = None ,
			      key_file = None ) :
			"""

			:param ip:
			:param key_file:
			:return:
			"""


			key = str()
			b_ret = False
			out = str()

			if ip is None or key_file is None :
				raise ValueError( 'bad parameter list' )


			with open( key_file  )as f  :
				key = f.readline().strip()

			try :

				req = 'http://api.ipinfodb.com//v3/ip-city/?key=%s&format=json&ip=%s' % \
					  ( key , ip )

				r = requests.get( req )
				x = r.json()
				for item in  x  :
					out += '%s : %s\n' % ( item , x[item] )


				obj = IPWhois( ip )
				results = obj.lookup_rdap(depth=1)
				s = StringIO()
				pprint.pprint( results , s )
				out += '\n\n\n'
				out += s.getvalue()


				b_ret = True

			except Exception as e :
				out = e.message



			return b_ret , str( out )




# ------------------------------------------------------------------------------------
if __name__ == '__main__' :

			#quick_wireless_sniff()
			print ip_geography( '173.167.195.34' , '../ip_geo_key' )


