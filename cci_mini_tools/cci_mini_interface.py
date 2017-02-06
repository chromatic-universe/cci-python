__author__ = 'william k. johnson 2015'

# cci_mini_interface.py

# standard
from abc import ABCMeta , abstractmethod
import os
import argparse

# cci
import cci_utils.cci_io_tools as io
from cci_mini_tools.daemon import Daemon


# daemonization

#rabbit mq
import pika

from cci_mini_tools.daemon import Daemon

# ------------------------------------------------------------------------
class cci_mini_intf( object ) :

        metaclass = ABCMeta

        """
        base mini tool
        """


        '''object model'''
        def __init__( self ) :

           super( cci_mini_intf , self ).__init__()


        '''services'''
        @abstractmethod
        def prepare( self ) :
            pass

        @abstractmethod
        def perform( self ) :
            pass

# ------------------------------------------------------------------------
class cci_mini_tool( cci_mini_intf )  :
        """
        minimal utility class exposing
        daemon , logging and publish/subscribe facilities
        """

        '''object model'''
        def __init__( self , endpoint = 'localhost' ,
                             daemonize = False  ) :

           super( cci_mini_tool , self).__init__()

           # logging
           self._logger = io.init_logging( self.__class__.__name__  )
           self._logger.info( self.__class__.__name__ + '...'  )

           # publish/subscribe
           self._queue_name = self.__class__.__name__
           self._connection_endpoint = endpoint
           self._channel = None

           # daemonizing
           self._daemonized = False
           self._daemonize = daemonize
           self._daemonized = False

           try :
               self._connection = pika.BlockingConnection(pika. \
                                  ConnectionParameters( self._connection_endpoint ) )
           except :
               self._connection = None
               self._logger.warning( 'could not acquire amqp connection handle....' )


           # command line
           self._args_parser = argparse.ArgumentParser( description= self.__class__.__name__   + ' william k. johnson 2015 ' ,
                                      epilog='...minimal utilities...')
           self._args_parser._optionals.title = 'flag arguments'


        '''attributes'''
        @property
        def daemonized( self ) :
            return self._daemonized
        @daemonized.setter
        def daemonized( self , daemoned ) :
            self._daemonized = daemoned
        @property
        def queue_conn( self) :
            return self._connection
        @queue_conn.setter
        def queue_conn( self , conn ) :
            self._connection = conn
        @property
        def args_parser( self ) :
            return self._args_parser
        @args_parser.setter
        def args_parser( self , args ) :
            self._args_parser = args

        def __del__(self ) :
            """
            delete
            """

            if self._connection is not None:
                 self._logger.info( 'closing amqp queue channel....' )
                 self._connection.close()

        '''helpers'''


        '''services'''
        def connect( self ) :
            """
            connect queue
            """
            try :
                channel = self._connection.channel()
                self._logger.info( 'connected to amqp queue channel....' )
            except pika.exceptions.ChannelError as err :
                self._logger.error( 'could not connect to amqp queue channel....' )
                pass

        def prepare( self ) :
            pass

        def perform( self ) :
            self._logger.info( 'perform...'  )
            pass



# ------------------------------------------------------------------------
class cci_mini_clang_tool( cci_mini_tool ) :

        """
        clang utilities
        """

        '''object model'''
        def __init__( self ,
                      fullpath = None ,
                      vargs_lst = None ,
                      raise_bool = False ,
                      clang_lib_path = '/usr/lib') :

            super( cci_mini_clang_tool , self).__init__( endpoint = 'localhost' ,
                                                         daemonize = False  )


            if vargs_lst is None:
                # default args
                self._vargs = [ '-I./', '-I../']
            else :
                self._vargs = vargs_lst
                self._fullpath = fullpath
            self._fullpath = fullpath
            self._clang_lib_path = clang_lib_path


            # publish/subscribe amqp
            self._queue_name = self.__class__.__name__

            # stat file
            if fullpath is not None :
              if not os.path.exists( fullpath ) or not os.path.isfile( fullpath ) :
                  if raise_bool is True :
                      import sys
                      self._logger.error( 'could not stat full path....exiting' )
                      sys.exit( 1 )
                  else :
                      pass

        '''attributes'''
        @property
        def log( self ) :
            return self._logger
        @log.setter
        def log( self , lg ) :
            self._logger = lg
        @property
        def fullpath( self ) :
            return self._fullpath
        @fullpath.setter
        def fullpath( self , path ) :
            self._fullpath = path
        @property
        def clang_args( self ) :
            return self._vargs
        @clang_args.setter
        def clang_args( self , vargs ) :
            self._vargs = vargs
        @property
        def clang_lib( self ) :
            return self._clang_lib_path
        @clang_lib.setter
        def clang_lib( self , path ) :
            self._clang_lib_path = path

        '''helpers'''

        '''services'''
        def prepare( self ) :
            """
            prepare
            :return:
            """
            pass

        def perform( self ) :
            """
            retrieve diagnostics for full_path
            :return:
            """
            pass