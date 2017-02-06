# cci_mini_scrapy.py william k. johnson 2016

import future
#############
import doctest
import unittest
##############
import requests
import logging
import argparse
##############
from abc import ABCMeta , abstractmethod
##############
import cci_utils.cci_io_tools as io
import cci_utils.cci_constants as const

const.security_level_zero = 0

# -----------------------------------------------------------------------------
class cci_scrapy_skel_impl( object) :
        """
        abstract base
        """
        _metaclass__ = ABCMeta
    
        '''object model'''
        def __init__( self ) :
            pass
           
        @property
        @abstractmethod
        def security_level( self ) :
            pass

# ------------------------------------------------------------------------------
class cci_mini_scrapy( cci_scrapy_skel_impl ) :
        """
        mini_scrapy implementation
        """
    
        def __init__( self ,
                      security_level=const.security_level_zero ,
                      default_base_url=None , 
                      validate_on_construct=False ) :
            """
            init

            :param default_base_url:
            :return:
            """
            super( cci_scrapy_skel_impl , self ).__init__()
            
            self._security_level = security_level
            self._default_base_url = default_base_url
            self._validate_on_construct = validate_on_construct
    
             # logging
            self._logger = io.init_logging( self.__class__.__name__  )
            self._logger.info( self.__class__.__name__ + '...'  )
    
        @property
        def security_level( self ) :
            return self._security_level
        @security_level.setter
        def security_level( self , level ) :
            self._security_level = level
        @property
        def validate_on_construct( self ) :
            return self._validate_on_construct
        @validate_on_construct.setter
        def validate_on_construct( self , val ) :
            self._validate_on_construct = val
        @property
        def base_url( self ) :
            return self._default_base_url
        @base_url.setter
        def base_url( self , url ) :
            self._default_base_url = url
        @property
        def logger( self ) :
            return self._logger
        @logger.setter
        def logger( self , log ) :
            self._logger = log
                
        
        def __repr__( self ) :
             """
             returns string representation and construction info
             :rtype : basestring
             :return:
             """
             return "{__class__.__name__}(security_level={_security_level!r},default_base_url={_default_base_url!r}," \
                    "validate_on_construct={_validate_on_construct!r})". \
                    format( __class__=self.__class__ , **self.__dict__ )
        
        
        def __str__( self ) :
              """
              returns pretty string
              :rtype: basestring
              :return: str
              """
              return 'cci_mini_scrapy , 2016 , william k. johnson'



# ------------------------------------------------------------------------
if __name__ == '__main__' :

        ostr = io.ostream_py()
        try :
            cci = cci_mini_scrapy()

            cci.logger.info( 'completed ...' )

            ostr << repr( cci )\
                 << const.endl

        except IOError as e :
            ostr << 'IO error ' << e.message << const.endl
        except Exception as e:
            ostr << 'error:' + e.message << const.endl



