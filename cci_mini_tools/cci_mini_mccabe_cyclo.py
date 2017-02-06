__author__ = 'william k. johnson 2015'

# cci_mini_mccabe_cyclo.py

import os
import sys
import subprocess
import argparse
import clang.cindex as clang
from clang.cindex import CursorKind
import unittest



from cci_mini_interface import cci_mini_clang_tool
import cci_utils.cci_io_tools as io
import cci_utils.cci_constants as const

const.cxx = '-std=c99'
const.cpp = '-std=c++11'

class cci_mini_mccabe_cyclo( cci_mini_clang_tool ) :

        """
        small utility class to for line cyclometric complexity
        """

        '''object model'''
        def __init__( self , fullpath = None , vargs_lst = None ) :

           super( cci_mini_mccabe_cyclo , self).__init__( fullpath , vargs_lst )

           self._keywordOpList = ["if","while","for","case"];

        def __repr__( self ) :
             """
             returns string representation and construction info
             :rtype : basestring
             :return:
             """
             return "{__class__.__name__}(fullpath={_fullpath!r},vargs_lst={_vargs!r})". \
                    format( __class__=self.__class__ , **self.__dict__ )

        def __str__( self ) :
              """
              returns pretty string
              :rtype: basestring
              :return: str
              """
              return 'cci_mini_mccabe_cyclo , 2015 , william k. johnson'

        def __bool__( self ) :
              """
              :return:
              """
              return True

        '''helpers'''
        def compute_branches( self , node ) :
            """
            :param node:
            :return:
            """
            branch_count = 0

            for tok in node.get_tokens() :
                if tok.spelling in self._keywordOpList :
                    branch_count += 1
            return branch_count

        def find_subs( self , node ) :
            """
            :param node:
            :return:
            """

            if ( node.is_definition() and
                 node.kind in [CursorKind.FUNCTION_TEMPLATE ,
                               CursorKind.FUNCTION_DECL]) :
                 branch_count = self.compute_branches( node )
                 print '%s: %d' % ( node.spelling , branch_count + 1 )
            else:
                 for c in node.get_children():
                     self.find_subs( c )

        '''services'''
        def perform( self ) :
            """
            do mcCabe for full_path
            :return:
            """
            try :

                index = clang.Index.create()
                tu = index.parse( self._fullpath )

                self.find_subs( tu.cursor )

            except clang.TranslationUnitLoadError as e:
                self.log.error( e )
            finally :
                pass

# ------------------------------------------------------------------------
if __name__ == '__main__' :


        ostr = io.ostream_py()

        try :
            cci = cci_mini_mccabe_cyclo(
                                            # file from wherever
                                            fullpath = '/chromatic-src/chromatic-c99/cci/cci_memory_utils.c'
                                       )
            cci.perform()
        except IOError as e :
            ostr << 'IO error ' << e.message << const.endl
        except Exception as e:
            ostr << e.message << const.endl
