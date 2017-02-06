__author__ = 'william k. johnson 2015'

# cci_mini_lex.py

import os
import pprint
import subprocess
import argparse
import clang.cindex as clang

#cci

from cci_mini_diag import cci_clang_tools_daemon
from cci_utils import cci_io_tools as io
import cci_utils.cci_constants as const
from cci_mini_interface import *



# ------------------------------------------------------------------------
"""
when passing args to the libclang library , be aware that this is an extern "C"
interface. libclang has no knowledge of c++ headers. you may or may not have to
pass them in the vargs list. Also be aware of mishegas and goofosity with standard
C headers due to the fact that clang has its own eccentric method for locating them.
if you get errors about limits.h or stdarg.h not found you'll have to explicitly
pass the clang include directory with the args.
"""

class cci_mini_lex( cci_mini_clang_tool ) :

        """
        small utility class to tokenize c/c++ source files
        """


        '''object model'''
        def __init__( self , fullpath = None , vargs_lst = None ) :

           super( cci_mini_lex , self).__init__( fullpath , vargs_lst )

           self._ostr = io.ostream_py()
           self._clang_file = None
           self._ticker = 0
           self._token_map = { 'TokenKind.IDENTIFIER' : 0 ,
                               'TokenKind.PUNCTUATION' : 0 ,
                               'TokenKind.KEYWORD' : 0 ,
                               'TokenKind.LITERAL' : 0 ,
                               'TokenKind.COMMENT' : 0 ,
                               'TokenKind.UNKNOWN' : 0
                             }

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
              return 'cci_mini_lex , 2015 , william k. johnson'

        def __bool__( self ) :
              """
              :rtype bool
              :return:
              """
              return True

        '''attributes'''
        @property
        def ostr( self ) :
            return self._ostr
        @ostr.setter
        def ostr( self , stm ) :
            self._ostr = stm
        @property
        def token_map( self) :
            return self._token_map


        '''helpers'''
        def _token_atom(  self , token , break_on = 5 ) :

            # pretty print with console color
            if repr( token.kind ) == 'TokenKind.IDENTIFIER' :
                self.ostr << "\033[94mIDENTIFIER("\
                          << token.spelling \
                          << ") " \
                          << "\033[0m"
            elif repr( token.kind ) == 'TokenKind.PUNCTUATION' :
                self.ostr << "PUNCTUATION("\
                          << token.spelling \
                          << ") "
            elif repr( token.kind ) == 'TokenKind.KEYWORD' :
                self.ostr << "\033[91mKEYWORD("\
                          << token.spelling \
                          << ") " \
                          << "\033[0m"
            elif repr( token.kind ) == 'TokenKind.LITERAL' :
                self.ostr << "LITERAL("\
                          << "\033[91m" << token.spelling << "\033[0m" \
                          << ") "
            elif repr( token.kind ) == 'TokenKind.COMMENT' :
                self.ostr << "COMMENT("\
                          << "\033[92m" << token.spelling << "\033[0m" \
                          << ") "
            elif repr( token.kind ) == 'TokenKind.UNKNOWN' :
                self.ostr << "UNKNOWN("\
                          << token.spelling \
                          << ") "

            # token dictionary
            sz = str( token.kind )
            if sz in self._token_map :
                self._token_map[sz] += 1

            # justify
            if self._ticker == break_on :
                self.ostr << const.endl
                self._ticker = 0

        '''services'''
        def prepare( self ) :
            """
            setup
            :return:
            """

            # command line
            self._args_parser.add_argument( '--fullpath',
                        required = True ,
                        help='required-full path to source c/c++ unit' )
            self._args_parser.add_argument('--daemon' ,
                        help='run as daemon process' )
            self._args_parser.add_argument('--xml' ,
                        help='xml output' )
            self._args_parser.add_argument('--output' ,
                        help='output to filename' )
            self._args_parser.add_argument( '--display_fan' ,
                        help='# of console display fan out cols' )
            args = vars( self._args_parser.parse_args() )
            self.fullpath =  args['fullpath']

        def perform( self ) :
            """
            tokenize for full_path
            :return:
            """

            try :

                self._ticker = 0
                # create clang index
                clang_index = clang.Index.create()
                if clang_index is not None :
                    self.log.info( 'created clang index......' + self.fullpath + '...' )
                    # create translation unit
                    trans_unit = clang.TranslationUnit.from_source(
                                                                    self.fullpath ,
                                                                    self._vargs ,
                                                                    None ,
                                                                    0
                                                                  )
                    if trans_unit is not None :
                        # translation unit
                        self.log.info( 'created translation unit....' )

                        # file source - we did stat file on construction
                        self._clang_file = clang.File.from_name( trans_unit , self._fullpath )
                        file_sz = os.stat( self._fullpath ).st_size
                        # start
                        source_start =  clang.SourceLocation().from_offset( trans_unit , self._clang_file , 0 )
                        # end
                        source_end =  clang.SourceLocation().from_offset( trans_unit , self._clang_file , file_sz - 1 )
                        # range
                        source_range = clang.SourceRange().from_locations( source_start , source_end )
                        # zero dictionary  counters
                        for key,value in self._token_map.items() :
                            value = 0
                        # process tokens
                        for tok in clang.TokenGroup.get_tokens( trans_unit , source_range ) :
                            self._token_atom( tok )
                            self._ticker += 1
                        self.ostr << const.endl << const.endl
                        # pretty print dump dictionary
                        pp = pprint.PrettyPrinter( indent=4 )
                        pp.pprint( self._token_map )

            except clang.TranslationUnitLoadError as e:
                self.log.error( e )
            finally :
                pass

# ------------------------------------------------------------------------
if __name__ == '__main__' :

        # clang arguments
        # c++11
        args = [
                 "-x" ,
                 "c++" ,
                 "-std=c++11" ,
                 "-I/dev_src/dev_src_a/dev_src/include"  ,
                 "-I/usr/lib/llvm-3.6/../lib/clang/3.6/include" ,
                 "-I/usr/lib/llvm-3.6/include"
               ]
        # we use prepare - alternativiely we could have instantiated without cli
        # by construction
        mini = cci_mini_lex( vargs_lst=args )
        mini.prepare()
        mini.perform()
