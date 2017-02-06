 # cci_packet_tools.py willliam k. johnson 2016


import os
import sys
#############
import doctest
import unittest
from sets import Set
from abc import abstractmethod , ABCMeta
import copy
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
##############
import requests
import logging
import argparse
import subprocess as proc

##############
import cci_utils.cci_io_tools as io
from cci_stream_inf import cci_stream_intf
import cci_utils.cci_constants as const

##############
'''disable ipv6 console annoyance'''
logging.getLogger( "scapy.runtime" ).setLevel(logging.ERROR)
from scapy.all import *

import paramiko


# ---------------------------------------------------------------------------------------------
def ping_atom( destination = None ) :
        """
        ping single addr layer 3 with scapy

        :param  destination : parses local subnet from addr:
        :return : reply obj
        """

        return sr1( IP( dst = destination )/ICMP() , timeout = 1 )


# ---------------------------------------------------------------------------------------------
def ping_subnet( destination = None ) :
        """
        ping subnet
        :param  destination , parses local subnet from addr:
        :return ping reply obj list:
        """

        prefix = io.chomp( source_str = destination , delimiter = '.' , keep_trailing_delim = True )
        replies = list()

        '''
        for each address in subnet
        '''
        for addr in range( 0 , 255 ):
            try :
                #put request on wire
                print prefix + str( addr )
                reply = ping_atom( prefix + str( addr ) )
                if reply is not None :
                    replies.append( reply )
            except Exception as err :
                print err

        return replies


# ------------------------------------------------------------------------------------
if __name__ == '__main__' :

        stream = sys.stdout
        reply = ping_atom( 'www.google.com' )
        if reply is None :
            print "ping failed....."
        else :
            print 'ping succeeded'


