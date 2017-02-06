from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix import image
from kivy.core.window import Window
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.treeview import TreeView , TreeViewLabel , TreeViewNode
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.bubble import Bubble
from kivy.uix.actionbar import ActionButton
from kivy.config import ConfigParser
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock , mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty

import os
import copy
import logging
import importlib
import datetime
from time import gmtime, strftime , sleep ,time
import subprocess as proc
import threading
import requests
from functools import partial

import sqlite3
import Queue
import uuid
import base64
import requests
import json


from king_console import screen
from king_console import resource_factory \
	                     as resources
from king_console import cci_mini_mongo as mongo_client
from king_console import kc_nmap



# -----------------------------------------------------------------------------------
def local_mac_addr() :
		"""

		:return mac string:
		"""

		try :
			return base64.b64encode( ( proc.check_output( ['cat' ,
														   '/sys/class/net/wlan0/address'] ).strip().lower() ) )
		except :
			pass





class kc_config( object ) :
				"""
				config
				"""


				def __init__( self  ,   log = None ) :

					"""
					:param log
					:return:
					"""

					if log is None :
						raise Exception( 'no logger provided' )




				@classmethod
				def _retr_resource( cls , resource_id ) :
					"""

					:param resource_id:
					:return ui resource:
					"""

					return resources.const_resource_ids[resource_id]



				@classmethod
				def _post_function_call( cls , func , params ) :
					"""

					:param func:
					:param params:
					:return:
					"""

					package = ( func , params )
					App.get_running_app().dbq.put( package )



				def _show_info( self, container ) :
					"""
					:param text container
					:return
					"""

					pass


				def _on_test_connect( self ) :
					"""
					:return
					"""

					pass


				def show_config( self ) :
					"""

					:param bootstrap:
					:return:
					"""

					pass








# ------------------------------------------------------------------------------------------
class kc_mongo_config( kc_config ) :
				"""

				"""

				def __init__( self  , bootstrap = None ,
							  		  port = 27017 ,
							          log = None ,
									  device_id = None ,
									  last_ip = None ,
									  last_real_ip = None ) :
							"""

							:param bootstrap:
							:return:
							"""

							super( kc_mongo_config , self ).__init__( log )

							self._bootstrap = bootstrap
							self._port = port
							self._logger = log
							self._id = device_id
							self._last_ip = last_ip
							self._last_real_ip = last_real_ip




				def _show_info( self , container ) :
							"""

							:param container:
							:return:
							"""

							mongo = mongo_client.cci_mini_mongo( bootstrap = self._bootstrap ,
																 port = self._port ,
																 device_id = self._id )
							s = str()
							if mongo.connected :
								for key , value in mongo.device_info.iteritems() :
									s += str( key ) + ':   '  + str( value ) + '\n'
								mongo.mongo.close()
							else :
								s = 'mongo disconnected....no route to host...' ,
								s += 'could not connect to mongo host...'

							container.text = s




				def _show_extended_info( self , container ) :
							"""

							:param container:
							:return:
							"""

							container.text = '...standby..working...'

							b_ret , stream = kc_nmap.mongo_extended_metadata( self._bootstrap , self._port )
							if b_ret :
								container.text = stream
							else :
								container.text = '...could not retrieve extended info....'

							id = '(bootstrap=%s)' % self._bootstrap
							self._post_function_call( 'insert_session_call' , [ App.get_running_app()._session_id ,
																				'stream_config' ,
																				'_show_extended_info' ,
																				id ,
																				stream ] )



				# -------------------------------------------------------------------------------------------------
				def _add_console(  self ,
								   content ,
								   tag  ) :
							"""
							:param parent:
							:param content:
							:param: console_count:
							:param tag:

							:return:
							"""

							layout = GridLayout( cols = 1 ,
												 padding = [0 , 5 , 0 ,5]
												  )
							action_bar = Builder.load_string( self._retr_resource( 'dlg_action_bar_3' ) )
							layout.add_widget( action_bar )
							img = Image( source = './image/mongodb-log.png' , size_hint_y = .2  )
							layout.add_widget( img )
							layout.add_widget( Label( text = tag  ,
													  color = [ 1, 0 , 0 , 1] ,
													  font_size = 16 ,
													  size_hint_y = 0.1 ) )

							scrolly = Builder.load_string( self._retr_resource( 'text_scroller' ) )
							tx = scrolly.children[0]
							tx.text = ''
							tx.readonly = False

							layout.add_widget( scrolly )
							layout.add_widget( Label( text =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S" )  ,
													font_size = 16  ,
													size_hint_y = 0.2 ,
													color = [ 1, 0 , 0 , 1] ) )

							return layout





				def _on_test_connect( self ) :
							"""

							:return:
							"""





							layout = self._add_console( '..mongo extended' , 'mongo extended info(from nmap)' )
							popup = screen.ConsolePopup( title='mongo connect' , content = layout )
							vx = popup.content.children[1].children[0]
							b = popup.content.children[4].children[0].children[0]
							b.text = 'test connect'
							b.bind( on_press = lambda a:self._show_info( vx ) )
							c = ActionButton( text = 'info' )
							c.bind( on_press = lambda a:self._show_extended_info( vx ) )
							popup.content.children[4].children[0].add_widget( c )

							popup.open()



				def show_config( self ) :
							"""

							:param bootstrap:
							:return:
							"""


							layout = GridLayout( orientation = 'horizontal' ,
											  cols = 1 ,
											  background_color = [0,0,0,0])
							action_bar = Builder.load_string( self._retr_resource( 'dlg_action_bar_3' ) )
							layout.add_widget( action_bar )
							layout.add_widget( Image( source = './image/mongodb-log.png' , pos_hint_y = 0 ,
													  size_hint_y = .2 ) )
							scroll = ScrollView()
							grid = GridLayout( cols=1 , orientation = 'horizontal' , size_hint_y = None , size=(400 , 500 ) )
							grid.add_widget( Label(  text = 'active:' ) )
							grid.add_widget( Switch( active = True ) )
							grid.add_widget( Label(  text = 'bootstrap:' ) )
							grid.add_widget( TextInput(  text = self._bootstrap ,
														id = 'mongo_bootstrap' ,
														cursor_blink =  True ,
														readonly = False ,
														multiline =  True ,
														size_hint_y = .5 ) )
							grid.add_widget( Label(  text = 'bootstrap port:' ) )
							grid.add_widget( TextInput(  text = '27017' ,
														id = 'mongo_bootstrap_port' ,
														cursor_blink =  True ,
														readonly = False ,
														multiline =  True ,
														size_hint_y = .5 ) )

							scroll.add_widget( grid )
							layout.add_widget( scroll )


							#event = threading.Event()

							try :

								popup = screen.ConsolePopup( title='document context' , content=layout )
								b = popup.content.children[2].children[0].children[0]
								#btn = popup.content.children[1].children[0].children[0]
								b.bind( on_press = lambda a:self._on_test_connect() )
								popup.open()

							finally :
								#App.get_running_app().dbpq_lk.release()
								pass




				def _update_device_session( self ,
											open = True
											 ) :
							"""
							:open : boolean
							:return:
							"""

							s = str()
							if open :
								s = 'true'
							else :
								s = 'false'


							r = requests.post('http://localhost:7080/mongo/update_device_status',
										  data = json.dumps( {"device_id" : self._id ,
															  "active" : s ,
															  "last_known_ip" : self._last_ip ,
															  "last_known_remote_ip" : self._last_real_ip }) )






# ------------------------------------------------------------------------------------------
class kc_kafka_config( kc_config ) :
				"""

				"""

				def __init__( self  , bootstrap = None ,
							          log = None ) :
							"""

							:param bootstrap:
							:return:
							"""

							super( kc_kafka_config , self ).__init__( log )

							self._bootstrap = bootstrap
							self._logger = log




				def _show_info( self, container ) :
							"""

							:param container:
							:return:
							"""

							try:

								r = requests.get( 'http://localhost:7080/kafka/topics' )
								if r.status_code == 200 :
									j = r.json()
									topics =j['topics']
									s = 'topics for %s' % self._bootstrap
									s += '\n\n'
									for x in topics :
										s += x
										s += '\n'
									container.text = s

							except Exception as e :
								App.get_running_app()._logger.error( e.message )
								container.text = '..failed to retrieve kafka metadata'






				def _on_test_connect( self ) :
							"""

							:return:
							"""


							layout = GridLayout( orientation = 'horizontal' ,
											  cols = 1 ,
											  background_color = [0,0,0,0])
							action_bar = Builder.load_string( self._retr_resource( 'dlg_action_bar_3' ) )
							layout.add_widget( action_bar )
							img = Image( source = './image/kafka-logo.png' , size_hint_y = .15)
							scroll = ScrollView( id = 'scrlv' )
							grid = GridLayout( cols=1 , orientation = 'horizontal' , size_hint_y = None , size=(400 , 500 ) )
							grid.add_widget( img  )
							vx =  TextInput(
											text = '',
											background_color = [0,0,0,0] ,
											foreground_color =  [1,1,1,1] ,
											multiline = True ,
											font_size =  16 ,
											readonly =  True  )
							#vx.height = max( (len(vx._lines)+1) * vx.line_height, scroll.height )
							grid.add_widget( vx )
							scroll.add_widget( grid )
							layout.add_widget( scroll )

							popup = screen.ConsolePopup( title='kafka connect' , content = layout )
							b = popup.content.children[1].children[0].children[0]
							b.text = 'test connect'
							b.bind( on_press = lambda a:self._show_info( vx ) )
							popup.open()



				def show_config( self ) :
							"""

							:param bootstrap:
							:return:
							"""


							event = threading.Event()

							try:
								r = requests.get( 'http://localhost:7080/kafka/bootstrap' )
								if r.status_code == 200 :
									j = r.json()
									self._bootstrap = j['bootstrap_servers']
								else :
									raise Exception( '...retrieve config atom failed...' )

							except Exception as e :
								App.get_running_app()._logger.error( e.message )

								return


							layout = GridLayout( orientation = 'horizontal' ,
											  cols = 1 ,
											  background_color = [0,0,0,0])
							action_bar = Builder.load_string( self._retr_resource( 'dlg_action_bar_3' ) )
							layout.add_widget( action_bar )
							layout.add_widget( Image( source = './image/kafka-logo.png' , pos_hint_y = 0 ,
													  size_hint_y = .2 ) )
							scroll = ScrollView()
							grid = GridLayout( cols=1 , orientation = 'horizontal' , size_hint_y = None , size=(480 , 700 ) )
							grid.add_widget( Label(  text = 'active:' ) )
							grid.add_widget( Switch( active = True ) )
							grid.add_widget( Label(  text = 'default publishing topic:' ) )
							grid.add_widget( Label(  text = 'king-console-cci-maelstrom' ) )
							grid.add_widget( Label(  text = 'bootstrap broker:' ) )
							boot , port = self._bootstrap.split( ':' )
							grid.add_widget( Label(  text = boot  ) )
							grid.add_widget( Label(  text = 'bootstrap broker port:' ) )
							grid.add_widget( Label(  text = port ) )

							grid.add_widget( Label( text = 'stream stack' )  )
							grid.add_widget( Switch( active = True , id = 'stream_stack_switch' ) )
							grid.add_widget( Label( text = 'stream errors' )  )
							grid.add_widget( Switch( active = True , id = 'stream_errors_switch' ) )
							grid.add_widget( Label( text = 'honor blacklist stream' )  )
							grid.add_widget( Switch( active = True , id = 'honor_blacklist_switch' ) )

							scroll.add_widget( grid )
							layout.add_widget( scroll )


							#event = threading.Event()

							try :

								popup = screen.ConsolePopup( title='publish/subscribe context' , content=layout )
								b = popup.content.children[2].children[0].children[0]
								#btn = popup.content.children[1].children[0].children[0]
								b.bind( on_press = lambda a:self._on_test_connect() )
								popup.open()

							finally :
								#App.get_running_app().dbpq_lk.release()
								pass

