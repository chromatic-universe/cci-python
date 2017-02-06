# tr_bimini.py    william k. johnson  2016

import os
import sys
from StringIO import StringIO
import logging
from flask import Flask , request , send_file , render_template , url_for

#cci
import tr_trinity

from application import app

log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'

# logger
_logger = logging.getLogger( "tr_bimini" )
_logger.setLevel( logging.DEBUG )
fh = logging.FileHandler(  'tr_bimini.log' + '-debug.log', mode = 'a' )
fh.setLevel( logging.DEBUG )
formatter = logging.Formatter( log_format )
fh.setFormatter( formatter )
_logger.addHandler( fh )




# ------------------------------------------------------------------------------
@app.route( "/bimini" )
def cci_trinity():

                io = StringIO()
                try :
                    b_ret , out = tr_trinity.capture_screen( _logger )

                    if not b_ret :
                        _logger.error( out )
                    else :
                        io.write( out )
                        io.seek( 0 )


                except Exception as e :
                    #out =  'error in cci_trinity.....'  + e.message
                    _logger.error( e )
                    return

                return send_file( io , mimetype='image/png' )

app.add_url_rule( '/bimini' ,
				  'cci_trinity' ,
				  view_func=cci_trinity ,
				  methods=['GET'] )




# ------------------------------------------------------------------------
@app.route('/bimini/click')
def click() :
			"""

			:return:
			"""

			return tr_trinity.capture_clicks( log = _logger ,
										   request = request )

app.add_url_rule( '/bimini/click' ,
				  'click' ,
				  view_func=click ,
				  methods=['GET'] )




# ------------------------------------------------------------------------
@app.route('/bimini/key')
def key() :
			"""

			:return:
			"""

			return tr_trinity.capture_keys( log = _logger ,
										 request = request )

app.add_url_rule( '/bimini/key' ,
				  'key' ,
				  view_func=key ,
				  methods=['GET'] )


