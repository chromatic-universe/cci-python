# cci_clang_rpc_client.py   william k. johnson 2015

# standard lib
import sys
sys.path.append('gen-py' )
sys.path.insert( 0 , '/dev_tools/thrift-0.9.3/lib/py/build/lib*' )
import doctest
import unittest

# cci
from cci_mini_rpc import cci_mini_clang_rpc
from cci_mini_rpc.ttypes import *
from cci_mini_diag import cci_mini_diag

# thrift
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# make socket
transport = TSocket.TSocket( 'localhost', 9090 )

# buffering is critical. raw sockets are very slow
transport = TTransport.TBufferedTransport( transport )

# wrap in a protocol
protocol = TBinaryProtocol.TBinaryProtocol( transport )

# create a client to use the protocol encoder
clang_client = cci_mini_clang_rpc.Client( protocol )

# connect
transport.open()

try :

    try :
        diagnostics = clang_client.perform_diag( 'blase' )
        print( diagnostics )
    except invalid_clang_op as err :
        print( 'invalid clang operation: %r' % e  )

except Thrift.TException as tx :
    print( '%s' % tx.message  )
finally :

    try :
        transport.close()
    except :
        pass