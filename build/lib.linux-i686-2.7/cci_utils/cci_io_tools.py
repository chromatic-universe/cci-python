"""io_tools William K. Johnson 2015"""

from datetime import datetime , timedelta
import logging, time
import doctest
import threading
import locale
import sys

from cci_utils import cci_constants as const

def abstractmethod( method ):
    """
    An @abstractmethod member fn decorator.
    (put this in some library somewhere for reuse).

    """
    def default_abstract_method(*args, **kwargs):
        raise NotImplementedError('call to abstract method '
                                  + repr(method))
    default_abstract_method.__name__ = method.__name__
    return default_abstract_method

# constants
const.log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'


# ------------------------------------------------------------------------
def init_logging( moniker = 'current_app' , fmt = const.log_format ) :

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

#---------------------------------------------------------------------------
def today():
    return datetime.datetime.now().isoformat()

#---------------------------------------------------------------------------
class io_manipulator( object ) :

    __slots__ = ()

    @abstractmethod
    def do( self , function ):
        pass

#---------------------------------------------------------------------------
class output_manipulator( io_manipulator ):

    def __init__( self , function=None ):
        self._function = function

    def do( self , output ):
        self._function( output )

    #attributes
    @property
    def function( self ) :
        return self._function
    @function.setter
    def function( self , func ):
        self._function = func

        #---------------------------------------------------------------------------
class input_manipulator( io_manipulator ):

    def __init__( self , function=None ):
        self._function = function

    def do( self , input ):
        self._function( input )

    #attributes
    @property
    def function( self ) :
        return self._function
    @function.setter
    def function( self , func ):
        self._function = func

#---------------------------------------------------------------------------
def do_default( stream ):
        stream.format = '%s'
const.default = output_manipulator( do_default )

#---------------------------------------------------------------------------
def do_endl( stream ):
        stream.output.write( '\n' )
        stream.output.flush()
const.endl = output_manipulator( do_endl )

#---------------------------------------------------------------------------
def do_timestamp( stream ):
        stream.output.write( today() )
        stream.output.write( ' ')
        stream.output.flush()
const.tstamp = output_manipulator( do_timestamp )

#---------------------------------------------------------------------------
def do_hex( stream ):
        stream.format = '%x'
const.hex = output_manipulator( do_hex )

#---------------------------------------------------------------------------
def do_octal( stream ):
        stream.format = '%x'
const.octal = output_manipulator( do_octal )

#---------------------------------------------------------------------------
class ostream_py( object ):

    def __init__(self , output = None ) :

        if output is None:
            output = sys.stdout
        self._output = output
        self.format = '%s'

    def __lshift__( self , thing ):

        if isinstance( thing , output_manipulator ):
            thing.do( self )
        else:
            self._output.write( self.format % thing )
        return self

    def __repr__( self ) :

        return ''

    def __str__( self ) :

        return ''

    @property
    def output( self ) :
        return self._output
    @output.setter
    def output( self , out ) :
        self._output = out

#---------------------------------------------------------------------------
class istream_py( object ):

    def __init__( self , input = None ) :
        if input is None:
            input = sys.stdin
        self._input = input


    def __rshift__( self , thing ) :
        pass



#---------------------------------------------------------------------------
def example_main():

    pyostr = ostream_py()
    pyostr << 'cci_utils'\
           << const.endl\
           << 'blase'\
           << const.endl\
           << 'corny'\
           << const.endl\
           << const.hex\
           << 1024\
           << const.endl\
           << 4090\
           << const.endl\
           << const.default\
           << 'cci_utils'


if __name__ == '__main__':

    example_main()



# ---------------------------------------------------------------------------------------------
def chomp( source_str , delimiter = '' , keep_trailing_delim = True ) :
    """
    truncate and return string at last delimiter
    easy to do wiht splicing , but this function is
    more of a predicate for loop processsing

    :param delimiter :
    :param keep_trailing_delim :
    :return
    """

    idx = source_str.rfind( delimiter )
    temp_str = str()
    if idx is not -1 :
        temp_str = source_str[:idx]
        if keep_trailing_delim is True :
            temp_str += delimiter

    return temp_str


# ---------------------------------------------------------------------------------------------
def gnaw( source_str , delimiter = ' ' ) :
    """
    truncate and return substring rend

    :param source_str:
    :param delimiter:
    :return:
    """

    temp_str = str()
    idx = source_str.rfind( delimiter )
    if idx is not -1 :
        temp_str = source_str[idx:]

    return temp_str