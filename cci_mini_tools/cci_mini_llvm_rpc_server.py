# cci_mini_llvm_rpc_server.py    william K. johnson 2016

# standard lib
import sys
sys.path.append('gen-py' )
sys.path.insert( 0 , '/cci/dev_toools/thrift-0.9.3/lib/py/build/lib*' )
import doctest
import unittest
import logging

# cci
from cci_mini_llvm_rpc import cci_mini_llvm_rpc
from cci_mini_llvm_rpc.ttypes import *
from cci_mini_llvm_config import cci_mini_llvm_config
import cci_utils.cci_io_tools as io

# thrift
from shared.ttypes import SharedStruct
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class mini_llvm_rpc_handler :
    """
    rpc handler
    """

    '''object model'''
    def __init__(self) :
        """
        ctor
        :return:
        """
        self._logger = io.init_logging( self.__class__.__name__ )
        self._logger.info( self.__class__.__name__ + '...'  )

        self.llvm_config = cci_mini_llvm_config( '/cci/dev_t/bin/llvm-config' )

    '''attributes'''


    '''services'''
    # --------------------------------------------------------------------
    def atomic_config( self, index_config , cci_session ) :
        """
        one config
        :param index_config:
        :param cci_session:
        :return config param:
        """

        self.llvm_config.perform()
        config_stream = self.llvm_config.configs[index_config]
        self._logger.info( cci_session.comment )

        self._logger.info( self.__class__.__name__ + '...processed  request...<atomic config>' )

        return config_stream


    # --------------------------------------------------------------------
    def list_config( self, index_config , cci_session ) :
        """
        config list
        :param selfv:
        :param index_config:
        :param cci_session:
        :return :config list
        """
        lst = list()

        return lst


    # --------------------------------------------------------------------
    def config_all( self  ) :
        """
        map of configs
        :return : config map
        """

        dct = dict()

        return dct

# initialize proxy stubs
# ------------------------------------------------------------------------

handler = mini_llvm_rpc_handler()
processor = cci_mini_llvm_rpc.Processor( handler )
# transport params
transport = TSocket.TServerSocket( port = 9092 )
# object factories
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

# server instantiation
mini_llvm_server = TServer.TSimpleServer( processor ,
                                          transport ,
                                          tfactory ,
                                          pfactory )

# You could do one of these for a multithreaded server
#server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
#server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)

print( 'starting the server...' )

# start transport...run
mini_llvm_server.serve()

print( 'done.' )

