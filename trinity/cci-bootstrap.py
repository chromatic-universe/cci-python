import os
import logging
from time import sleep

if __name__ == '__main__':
    
        log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'


# logger
        _logger = logging.getLogger( "cci-trinity-server" )
        _logger.setLevel( logging.DEBUG )
        fh = logging.FileHandler(  'cci-trinity-server.log' + '-debug.log', mode = 'a' )
        fh.setLevel( logging.DEBUG )
        formatter = logging.Formatter( log_format )
        fh.setFormatter( formatter )
        _logger.addHandler( fh )

        with open( 'cci-trinity-pid' , 'w' ) as f :
            f.write( '%d' % os.getpid() )

        while True :
            _logger.info( 'the_original_corny_snaps!' )
            sleep( 2 )
		
