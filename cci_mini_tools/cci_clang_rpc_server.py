# cci_clang_rpc_server.py   william k. johnson 2015

# standard lib
import sys
sys.path.append('gen-py' )
sys.path.insert( 0 , '/cci/dev_tools/thrift-0.9.3/lib/py/build/lib*' )
import doctest
import unittest
import logging

# cci
from cci_mini_rpc import cci_mini_clang_rpc
from cci_mini_rpc.ttypes import *
from cci_mini_diag import cci_mini_diag
import cci_utils.cci_io_tools as io

# thrift
from shared.ttypes import SharedStruct
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class mini_rpc_handler :
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

    '''attributes'''


    '''services'''
    # --------------------------------------------------------------------
    def perform_diag( self , index_module) :
        """
        diagnosis returns info buffer
        :param index_module:
        :rtype string
        :return : info
        """

        diag_stream = 'The Original Corny Snaps!'

        self._logger.info( self.__class__.__name__ + '...processed  request...<perform diag>' )

        return diag_stream




# initialize proxy stubs
# ------------------------------------------------------------------------
handler = mini_rpc_handler()
processor = cci_mini_clang_rpc.Processor( handler )
# transport params
transport = TSocket.TServerSocket( port = 9090 )
# object factories
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

# server instantiation
clang_server = TServer.TSimpleServer( processor ,
                                      transport ,
                                      tfactory ,
                                      pfactory )

# You could do one of these for a multithreaded server
#server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
#server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)

print( 'starting the server...' )

# start transport...run
clang_server.serve()

print( 'done.' )
