# cci_mini_ssh.py willliam k. johnson 2016


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



# -------------------------------------------------------------------------------------
class cci_ssh_util( object ) :

            __metaclass__ =  ABCMeta

            """
            minimal wrapper for paramiko and crypt
            """

            # object model
            def __init__( self ,
                          user_name = None ,
                          key_file = None ,
                          target_server = None ,
                          connect_immediate = True ) :
                """

                :param user name:
                :param key_file:
                :param target_server:
                :param connect_immediate:

                :return:
                """

                self._logger = io.init_logging( self.__class__.__name__  )
                self._logger.info( self.__class__.__name__ + '...'  )
                # private key file
                self._key_file = key_file ,
                self._target_server = target_server
                self._user_name = user_name
                self._lines = []
                self._buffer = str()
                self._connection_live = False
                # is nuop in compound expression , i.e. always true
                self._connect_immediate = connect_immediate
                #paramiko client
                self._raw_client = paramiko.SSHClient()
                # say yes to host key
                self._raw_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
                if connect_immediate :
                    self._start()


            def __repr__( self ) :
                 """
                 returns string representation and construction info
                 :rtype : basestring
                 :return:
                 """
                 return "{__class__.__name__}(user_name={_user_name!r},key_file={_key_file!r}," \
                        "target_server={_target_server!r} , connect_immediate={_connect_immediate!r})". \
                        format( __class__=self.__class__ , **self.__dict__ )

            def __str__( self ) :
                  """
                  returns pretty string

                  :rtype: basestring
                  :return: str
                  """
                  return self.__class__.__name__ + ' , 2016 , william k. johnson'


            def __bool__( self ) :
                  """
                  :rtype bool
                  :return:
                  """
                  return self._connection_live


            def __enter__( self ) :
                  """
                  compound statement

                  :return:
                  """

                  if not self._connection_live :
                      return self._start()
                  return self


            def  __exit__( self, type , value , traceback ) :
                  """
                  compound statement

                  :param type:
                  :param value:
                  :param traceback:
                  :return:
                  """

                  self._stop()


            # attributes
            @property
            def private_key( self ) :
                return self._key_file
            @private_key.setter
            def private_key( self , key ) :
                self._key_file = key
            @property
            def user_name( self ) :
                return self.user_name
            @user_name.setter
            def user_name( self , name ) :
                self.user_name = name
            @property
            def logger( self ) :
                return self._logger
            @logger.setter
            def logger( self , log ) :
                self._logger= log
            @property
            def lines( self ) :
                return self._lines
            @lines.setter
            def lines( self , li ) :
                self._lines = li
            @property
            def buffer( self ) :
                return self._buffer
            @buffer.setter
            def buffer( self ,buf ) :
                self._buffer = buf
            @property
            def live( self ) :
                return self._connection_live
            @live.setter
            def live( self ,lv ) :
                self._connection_live = lv
            @property
            def ssh( self ) :
                return self._raw_client
            @ssh.setter
            def ssh( self , raw ) :
                self._raw_client = raw

            # helpers
            @staticmethod
            @staticmethod
            def _line_atom_to_field_defs( line_atom ) :
                pass


            def lst_to_str( lst_stream ) :
                return ''.join( map( str , lst_stream ) )


            @staticmethod
            def lst_to_string_io( lst_stream ) :
                return  StringIO( cci_ssh_kafka.lst_to_str( lst_stream ) )


            @staticmethod
            def translate_ps_stream(  ) :
                """

                :return ps_dictionary#
                """

                # <pid-as-int>{ {<field><value>} }
                ps_dictionary = {}

                #


            def _start( self ) :
                """
                initialize session with class params

                :return sefl. aw client:
                """
                try :
                    self._raw_client.connect( self._target_server ,
                                              username = self._user_name ,
                                              key_filename = self._key_file )
                    self._connection_live = True
                    self._logger.info( 'ssh session %s@%s connected...'    % ( self._user_name ,
                                                                                self._target_server ) )
                except paramiko.AuthenticationException as err :
                    self._logger.error( err.message )
                    self._connection_live = False
                    raise

                return self._raw_client


            def _stop( self ) :
                """
                halt ssh session

                :return:
                """
                if self._connection_live :
                    self._raw_client.close()
                    self._logger.info( 'ssh session at %s@%s closed...'    % ( self._user_name ,
                                                                                self._target_server ) )


            # services
            def raw_key( self ) :
                 """
                 key from file

                 return: data
                 """

                 data = []
                 with open( self._key_file ) as file :
                    data = file.read()

                 return data


            def start( self ) :
                """
                start
                """

                if not self._connection_live :
                    self._start()
                else :
                    self._logger.info( '...already connected...' )




# -------------------------------------------------------------------------------------
class cci_ssh_kafka( cci_ssh_util ) :

            """
            kafka ssh
            """

            ps_headers = [ 'user' ,
                           'pid' ,
                           '%cpu' ,
                           '%mem' ,
                           'vsz' ,
                           'rss' ,
                           'tty' ,
                           'stat' ,
                           'start' ,
                           'time' ,
                           'command']

            # object model
            def __init__( self ,
                          user_name = None ,
                          key_file = None ,
                          target_server = None ,
                          connect_immediate = True
                          ) :

                super( cci_ssh_kafka , self ).__init__( user_name ,
                                                        key_file ,
                                                        target_server ,
                                                        connect_immediate )




# ------------------------------------------------------------------------------------
if __name__ == '__main__' :


            ostr = io.ostream_py()

            try :

                with cci_ssh_kafka( user_name = 'ubuntu' ,
                                    key_file = '/home/wiljoh/cci-develop.pem' ,
                                    target_server = 'cci-aws-1' ) as cci :

                    stdin, stdout, stderr =  cci.ssh.exec_command( 'ps -aux' )
                    cci.buffer =  cci_ssh_kafka.lst_to_str( stdout )


            except IOError as e :
                ostr << 'IO error ' << e.message << const.endl
            except Exception as e:
                ostr << 'error:' + e.message << const.endl
            finally :
                pass