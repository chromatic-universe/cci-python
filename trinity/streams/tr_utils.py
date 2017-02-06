# trutils.py    william k. johnson 2016


import os
import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO    
import logging
from math import ceil

import subprocess as proc
import sqlite3
import time
import signal
import Queue
import requests
import datetime
import base64
import json
import itertools


log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'

##############
'''disable ipv6 console annoyance'''
logging.getLogger( "scapy.runtime" ).setLevel(logging.ERROR)
from scapy.all import *



# -----------------------------------------------------------------------------------
def dict_factory( cursor, row)  :
    d = {}
    for idx , col in enumerate( cursor . description ) :
        d[col[0]] = row[idx]
    return d



# -----------------------------------------------------------------------------------
def quoted( s ) :
	return '"' +  s  + '"'



# -----------------------------------------------------------------------------------
def quoted_list_to_tuple( lst ) :
	return tuple( [quoted( x ) for x in lst] )



# -----------------------------------------------------------------------------------
def local_mac_addr() :
		"""

		:return mac string:
		"""

		try :
			return base64.b64encode( proc.check_output( ['cat' ,
														 '/sys/class/net/wlan0/address'] ).strip() )
		except :
			try :
				return base64.b64encode( proc.check_output( ['cat' ,
														 '/sys/class/net/eth0/address'] ).strip() )
			except :
				pass

		return ''


# -----------------------------------------------------------------------
def split_seq( iterable , size ) :
		"""

		:param iterable:
		:param size:
		:return:
		"""
		it = iter(iterable)
		item = list(itertools.islice(it, size))
		while item:
			yield item
			item = list(itertools.islice(it, size))




# -----------------------------------------------------------------------
def iw_device_mode( dev = 'wlan0') :
		"""

		:param dev:
		:return exists , mode :
		"""

		b_ret = False

		cmd = ['iw' ,'dev']
		out = proc.check_output( cmd ).strip()
		lst = out.split( '\n' )
		for x in split_seq( lst , 4 ) :
			if x[1].find( 'wlan0' ) != -1 :
				b_ret = True
				s = x[3]
				s = s.replace( '\t' , '' )
				s = s.split()
				s = s[1]

				return b_ret , s , x[0]




# ----------------------------------------------------------------------
def port_vulture( port ) :
            """

            :param port:
            :return pid:
            """

            pid = -1
            try :

                if not os.geteuid() == 0 :
                    print  ( 'need to be root to call port vulture...\n' )
                    sys.exit( 1 )
                cmd = list()
                if os.path.exists( '/system/bin/busybox' ) :
                    cmd = [ 'busybox' , 'netstat' , '-tulpn']
                else :
                    cmd = ['netstat' , '-tulpn']
                nstat = proc.Popen( cmd , stdout=proc.PIPE )
                cmd = ['grep' , port]
                grep = proc.Popen( cmd , stdin=nstat.stdout , stdout=proc.PIPE )
                nstat.stdout.close()
                output = grep.communicate()[0]
                nstat.wait()

                segments = output.strip().split()
                if len( segments ) :
                    if segments[0] == 'tcp' or segments[0] == 'tcp6' :
                        # pid will be last segment
                        raw_pid = segments[len( segments ) - 1]
                    s = raw_pid.split( '/')
                    pos =  s[0].find( ' ' )
                    if pos != -1 :
                        x = s[0][pos:]
                        x = s.strip().split()
                        pid = str( x )
                    else :
                        pid = int( s[0] )

                return 	True , pid

            except ValueError as e :
                print ( "error in parameter list {:s}".format( e.message ) )
                return False , -1
            except OSError as e :
                print ( "binary does not exist?  {:s}".format( e.message ) )
                return False , -1



# -----------------------------------------------------------------------
def iw_supported_interface_modes( dev = 'phy#0' ) :
		"""

		:param dev:
		:return bool , list of interfaces :
		"""

		segment_lst = list()
		try :

			p = dev.replace( '#' , '' )
			cmd = ['iw' , 'phy' , p , 'info']
			out = proc.check_output( cmd ).strip()

			start_boilerplate = 'Supported interface modes:'
			end_boilerplate =  'software interface modes (can always be added):'

			start_pos = out.find( start_boilerplate )
			if start_pos :
				# walk past start boilerplate
				start_pos += len( start_boilerplate )
				end_pos = out.find( end_boilerplate )

				# get segment
				segment = out[start_pos:end_pos].strip()
				segment = segment.replace( '*' , '' )
				segment_lst = segment.split()

		except proc.CalledProcessError as e :
			print ( e.message )


		return segment_lst



# ---------------------------------------------------------------------------------------------
def retr_local_ip_info() :
		"""

		:return tuple of ips:
		"""

		# local
		local_ip = '0.0.0.0'
		remote_ip = '0.0.0.0'
		s = socket.socket( socket.AF_INET , socket.SOCK_DGRAM )

		try :
			local_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1],
							   [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
							   socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
		except :
			# give it up for a lost cause
			local_ip = '0.0.0.0'

		finally:
			s.close()


		return local_ip





# ------------------------------------------------------------------------
def init_logging( moniker = 'current_app' , fmt = log_format ) :

		"""
		initialize application logging
		:param logger:
		:param moniker:
		:param fmt:
		:return logger :
		"""

		logger = logging.getLogger( moniker )

		# setup logging

		# create logger
		logger.setLevel( logging.DEBUG )
		# create file handler strange file extension
		# tells python logging module to overwrite file
		fh = logging.FileHandler( moniker + '.log' + '-debug.log', mode = 'w')
		fh.setLevel( logging.DEBUG )

		# create console handler
		ch = logging.StreamHandler()
		ch.setLevel( logging.DEBUG )

		# create formatter and add it to the handlersuntitled
		formatter = logging.Formatter( fmt )
		fh.setFormatter( formatter )
		ch.setFormatter( formatter )

		# add the handlers to the self._logger
		logger.addHandler( fh )
		logger.addHandler( ch )

		return logger



if __name__ == '__main__' :

		print ( retr_local_ip_info() )
		"""
		print '* ' * 39
		print '\t\tchromatic universe cci-trinity packet streamer , 2016'
		print '* ' * 39
		print
		b_ret , mode , phys = iw_device_mode()
		if b_ret :
			print 'wlan0 in %s mode physical device id = %s' % ( mode , phys )

		else :
			print 'interface not found'

		supported = iw_supported_interface_modes( dev = phys )
		if len( supported ) :
			print '->supported modes: %s' % supported

		if( 'monitor' ) in supported :
			print '->device is capable of monitoring raw packets on network segment\n'
		else :
			print '->device is not capable of monitoring raw packets in network segment\n'


		print

		pid = port_vulture( '7080' )
		if pid :
			print 'cci-trinity application server is running with pid %d' % pid
		else :
			print 'cci-trinity application server is not running...'
		pid = port_vulture( '7081' )
		if pid :
			print 'cci-trinity application server is running with pid %d' % pid
		else :
			print 'cci-trinity application server is not running...'
		"""
