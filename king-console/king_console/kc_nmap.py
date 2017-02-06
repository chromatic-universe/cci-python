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
import fcntl
import struct
import subprocess as proc
import urllib2
import requests
from kivy.utils import platform

firewalk_params = { 'max_retries' : 'firewalk.max-retries=%d' ,
					'probe_timeout' : 'firewalk.probe-timeout=%d' ,
					'recv_timeout' : 'firewalk.recv-timeout=%d' ,
					'max_ports' : 'firewalk.max-probed-ports=%d' }


# ---------------------------------------------------------------------------------------------
def nmap_platform_dispatch( cmdline ) :
			"""

			:param cmdline:
			:return:
			"""

			cmd = list()
			if platform == 'android' :
				cmd = [ "su" ,
					   "-c" ,
					   "/system/bin/nmap"]
				cmd.extend( cmdline )
			else :
				cmd = ['nmap']
				cmd.extend( cmdline )


			return cmd



# ---------------------------------------------------------------------------------------------
def quick_fingerprint( ip = None ) :
			"""

			:param ip:
			:return:
			"""

			if ip is None :
				raise Exception( 'no ip supplied' )

			out = str()
			boiler = str()
			b_ret = True
			try :


				cmd = ["su" ,
					   "-c" ,
					   "/system/bin/nmap" ,
					   "-O" ,
					   '-v' ,
					   ip
					  ]

				try :
					out = proc.check_output( cmd  )
				except proc.CalledProcessError as e :
					b_ret = False
			except Exception as e :
				b_ret = False
				raise Exception(  'quick fingerprint...' + e.message )


			return b_ret , out



# ---------------------------------------------------------------------------------------------
def fat_fingerprint( ip = None ) :
			"""

			:param ip:
			:return:
			"""

			if ip is None :
				raise Exception( 'no ip supplied' )

			out = str()
			boiler = str()
			b_ret = True
			try :


				cmd = ["su" ,
					   "-c" ,
					   "/system/bin/nmap" ,
					   "-p0" ,
					   '-v' ,
					   '-A' ,
					   '-T4' ,
					   ip
					  ]

				try :
					out = proc.check_output( cmd  )
				except proc.CalledProcessError as e :
					b_ret = False
			except Exception as e :
				b_ret = False
				raise Exception(  'quick fingerprint...' + e.message )


			return b_ret , out



# ---------------------------------------------------------------------------------------------
def ping_ip_subnet( ip = None ) :
			"""

			:param ip:
			:return:
			"""

			if ip is None :
				raise Exception( 'no ip supplied' )



			cmd = nmap_platform_dispatch( ["-n" ,
										   '-sP',
										   ip
										  ] )


			return spawn_nmap_output(  cmd , 'ping_ip_subnet' )




# ---------------------------------------------------------------------------------------------
def mongo_extended_metadata( ip = None  , port = None ) :
			"""

			:param ip:
			:return exntended info:
			"""


			if ip is None :
				raise ValueError( 'no ip supplied' )

			cmd = nmap_platform_dispatch( [
											"-p" ,
											str( port ) ,
											"--script",
											"mongodb-info" ,
										    ip
									     ] )
			return spawn_nmap_output(  cmd , 'mongo_extended_metadata' )




# ---------------------------------------------------------------------------------------------
def firewalk( ip = None ,
			  max_retries = 1 ,
			  probe_timeout = 0  ,
			  recv_timeout = 0  ,
			  max_ports = 7 )  :
			"""
			:param ip:
			:param max_retries:
			:param probe_timeout:
			:param max_ports:
			:return:
			"""


			if ip is None or len( ip ) == 0 :
				raise ValueError( 'no ip supplied' )

			s = '--script-args='
			if max_retries != 0 :
				s += firewalk_params['max_retries'] % max_retries
				s += ','
			if probe_timeout != 0 :
				s += ' '
				s += firewalk_params['probe_timeout'] % probe_timeout
				s += ','
			if recv_timeout != 0 :
				 s += ' '
				 s += firewalk_params['recv_timeout'] % recv_timeout
				 s += ','
			if max_ports != 0 :
				 s += ' '
				 s +=  firewalk_params['max_ports'] % max_ports
			s.strip( ',' )

			cmd = [
				   "su" ,
				   "-c" ,
				   "/system/bin/nmap" ,
				   "--script=firewalk" ,
				   "--traceroute" ,
				   s ,
				   ip
				   ]


			return spawn_nmap_output(  cmd , 'firewalk' )






# ---------------------------------------------------------------------------------------------
def spawn_nmap_output( cmdline = None , moniker = 'nmap' ) :
			"""

			:param cmdline:
			:return output:
			"""

			if cmdline is None :
				raise Exception( '..spawn_nmap_output...no cmdline supplied' )
			print cmdline
			out = str()
			boiler = str()
			b_ret = True
			try :

				try :
					out = proc.check_output( cmdline  )
				except proc.CalledProcessError as e :
					b_ret = False
			except Exception as e :
				b_ret = False
				out = moniker + ' '  + e.message



			return b_ret , out




# ------------------------------------------------------------------------------------
if __name__ == '__main__' :

			#b_ret , out = mongo_extended_metadata( 'cci-aws-3'  )
			#b_ret , out = firewalk( ip = 'cci-aws-1' , max_ports = 7 )
			#b_ret , out = ip_geography( '52.84.127.83' , '../ip_geo_key' )
			pass
