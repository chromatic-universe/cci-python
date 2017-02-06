from __future__ import print_function

__author__ = 'william k. johnson 2015'

# cci_clang_mini_jit.py

# standard lib
import time
import os
import sys
import argparse
import doctest
import unittest
from ctypes import CFUNCTYPE, c_double
# llvm
import llvmlite.binding as llvm
# cci
import cci_utils.cci_constants as const
from cci_mini_tools.cci_mini_interface import *


const.cxx = '-std=c99'
const.cpp = '-std=c++11'


class cci_clang_mini_jit( cci_mini_tool ) :
        """
        minimal clang jit compiler
        """

        '''object model'''

        def __init__( self ,
                      target_triple = 'unknown-unknown-unknown' ,
                      target_layout = "" ,
                      daemonized = False ) :
            """
            clang mini jit

            :param target_triple:
            :param target_layout:
            :param daemonized:
            :return:
            """
            super( cci_clang_mini_jit , self).__init__( endpoint = 'localhost' ,
                                                        daemonize = True
                                                      )

            # environment initializations
            llvm.initialize()
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()

            self._logger.info( 'jit...'  )
            self._exec_engine = self.create_execution_engine()
            self._logger.info( 'instantiated clang execution engine...'  )
            self._triple = target_triple
            self._layout = target_layout


        def __eq__( self , other ) :

            """
            :param other:
            :return:
            """
            pass

        '''attributes'''

        @property
        def logger( self ) :
            return self._logger
        @logger.setter
        def logger( self , log ) :
            self._logger = log
        @property
        def triple( self ) :
            return self._triple
        @triple.setter
        def triple( self , tpl ) :
            self._triple = tpl
        @property
        def layout( self ) :
            return self._layout
        @layout.setter
        def layout( self , lay ) :
            self._layout = lay


        '''helpers'''

        def create_execution_engine( self ):
            """
            create an execution engine suitable for jit code generation on
            the host cpu. the engine is reusable for an arbitrary number of
            modules
            """

            # create a target machine representing the host
            target = llvm.Target.from_default_triple()
            target_machine = target.create_target_machine()
            # and an execution engine with an empty backing module
            backing_mod = llvm.parse_assembly( "" )
            engine = llvm.create_mcjit_compiler( backing_mod, target_machine )

            return engine

        '''services'''
        def check_config( self ) :
            """
            check jit config with canned routine
            :return :
            :rtype : bool
            """

            self._logger.info( 'exercising execution engine...'  )

            return True

        def prepare( self ) :
            """
            setup
            :return:
            """
            # command line
            self._args_parser.add_argument( '--daemonize',
                        type=bool ,
                        required = True ,
                        help='run clang-mini-jit as daemon process' )
            self._args_parser.add_argument('--amqp connection' ,
                        help='connect to host other than localhost' )
            self._args_parser.add_argument('--amqp channel' ,
                        help='amqp queue name' )
            args = vars( self._args_parser.parse_args() )

            # check config
            if self.check_config() is True :
                self.connect()
            else :
                return False

            '''if args['daemonize'] is not None :
                if args['daemonize'] is True :
                    return self.daemonize()
            '''

            return True

        def perform( self , filename = None , daemon = False ):
            """
            main program loop
            :return:
            """
            while True :
                time.sleep( 5 )
                self.logger.info( 'The Original Corny Snaps' )


# ------------------------------------------------------------------------
class cci_clang_driver_daemon( Daemon ) :

    """
    utility wrapper for daemon facility
    after some great pontification and brain damage
    this seems to be the best , if not most elegant
    solution to providing daemon support to our minimal
    implementations. the python-daemon library does
    not lend itself well to either inheritance or object
    composition due to scope problems(when a process is
    demonized it forks twice-object lifetimes are problematic).
    there was the possibility or muliple inhheritance , but wrapping
    a third party libary with an adapter class seemed to be more
    work than was neccessary for a small benefit. sometimes things
    can be over reduced. a single definition per mini bunch seems
    acceptable.
    """
    def __init__( self , pidfile , class_name , **kwargs ) :

        # daemon upcall
        super( cci_clang_driver_daemon , self ).__init__( pidfile )
        # transmogrify our runtime class
        self._cname = globals() [class_name]
        # unpack the runtime class args
        self._arg_str  = str()
        for key, value in kwargs.iteritems() :
            temp = "%s=%s" % ( key , value )
            self._arg_str += temp
            self._arg_str += ' '
        self._arg_str.strip()

    def run( self ) :
        """
        daemon loop
        :return:
        """
        # instantiate runtime class
        runtime_class = self._cname( self._arg_str )
        # call any abstract methods
        runtime_class.prepare()
        runtime_class.perform()

# ------------------------------------------------------------------------
if __name__ == '__main__' :

            # target triple
            triple = 'x86-linux-elf'
            g = cci_clang_driver_daemon( pidfile = '/var/run/cci_mini/cci_clang_mini_jit.pid' ,
                        class_name = 'cci_clang_mini_jit' ,
                        target_triple = triple  )
            g.start()














