# kivy
import kivy
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix import image
from kivy.core.window import Window
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.treeview import TreeView , TreeViewLabel , TreeViewNode
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.config import ConfigParser
from kivy.uix.progressbar import ProgressBar
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock , mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.settings import SettingsWithSidebar , SettingsWithSpinner
from kivy.config import Config
from kivy.loader import Loader
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.clock import Clock , mainthread
from kivy.base import EventLoop
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.image import Image

Window.softinput_mode = 'pan'

# python standard
import os
import sys
import copy
import logging
import datetime
import importlib
import urllib
from time import gmtime, strftime , sleep
import subprocess as proc
import threading
import socket
import requests
#import evdev



try:  # python 2
    from urllib import urlencode
except ImportError:  # python 3
    from urllib.parse import urlencode

try:  # python 2
    from urllib2 import urlopen
except ImportError:  # python 3
    from urllib.request import urlopen


from bimini import resource_factory \
	                     as resources , \
						 screen


kivy.require( '1.9.1' )

const_back_btn = 27

try:  # python 2
    from urllib import urlencode
except ImportError:  # python 3
    from urllib.parse import urlencode



def timestamp() :
	return datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S"  )



# ------------------------------------------------------------------------------------------------
class ConsoleAccordion( Accordion ) :

		btn_text = StringProperty('')
		_orientation = StringProperty('vertical')
		_inner_orientation = StringProperty( 'horizontal' )
		orientation_handler = ObjectProperty(None)

		stop = threading.Event()

		def __init__( self, *args, **kwargs):
			super( ConsoleAccordion , self ).__init__( *args, **kwargs)

			# get the original orientation
			self._orientation = 'horizontal' if Window.width > Window.height else 'vertical'
			# inform user
			self.btn_text = self._orientation
			self.orientation = self._orientation
			self._inner_orientation =  'vertical' if self.orientation == 'horizontal' else 'horizontal'


		def check_orientation( self , width , height ) :
			"""

			:param width:
			:param height:
			:return:
			"""

			orientation = 'vertical' if height > width else 'horizontal'
			if orientation != self._orientation:
				self._orientation = orientation
				self.orientation_cb(orientation)



		def orientation_cb( self , orientation ) :
			"""

			:param orientation:
			:return:
			"""
			self.btn_text = orientation
			self.orientation = 'horizontal' if Window.width > Window.height else 'vertical'
			self._inner_orientation =  'vertical' if self._orientation == 'horizontal' else 'horizontal'


# -----------------------------------------------------------------------------------------------
class FocusImage( FocusBehavior , Image ):
                """
                focus
                """

                def on_touch_down( self , touch ) :
                    self.focus = True




def win_cb( window, width, height):
		print 'width: %d  height: %d' % ( width , height )
# ------------------------------------------------------------------------------------------------
class biminiApp( App ) :
				"""
				urnack
				"""


				def __init__( self ) :
					"""

					:return:
					"""

					super( biminiApp , self ).__init__()

					# logger
					self._logger = logging.getLogger( "cci-bimini-client" )
					self._logger.setLevel( logging.DEBUG )
					fh = logging.FileHandler(  'cci-bimini.log' + '-debug.log', mode = 'a' )
					fh.setLevel( logging.DEBUG )
					formatter = logging.Formatter( resources.log_format )
					fh.setFormatter( formatter )
					self._logger.addHandler( fh )
					self._logger.info( self.__class__.__name__ + '...'  )
					self._screen_width = 0
					self._screen_height = 0
					self.url  = str()
					self.send_url = str()
					self.send_key_url = str()
					self._is_android = False
					self._key_from_remote = False
					self._connected = False
					self._is_full_screen = False
					self._clock_event = None
					self._connect_event = None
					self._full_screen_lst = list()
					self._thred = None
					self._ev = threading.Event()

					self.settings_cls = SettingsWithSpinner
					Window.on_rotate = self._on_rotate
					#Window.bind(on_resize=win_cb)



				def update_status( self ) :
					"""

					:return:
					"""



				def _move_carousel( self  ) :
					"""

					:return:
					"""

					if self.root.ids.screen_config_btn.text ==  'screen' :
						self.root.ids.maelstrom_carousel_id.load_next()
						self.root.ids.screen_config_btn.text = 'console'
					else :
						self.root.ids.maelstrom_carousel_id.load_previous()
						self.root.ids.screen_config_btn.text = 'screen'


				def on_connect( self ) :
					"""

					:return:
					"""

					self.root.current = 'desktop'
					self.root.ids.desktop.source = 'remote_2.png'


					from kivy.core.window import Window

					#Window.size = ( 640 , 480 )

					if self._thred :
						self._ev.set()
						self._thred.join()
						self._ev.clear()
						self._thred = None

					self._thred = threading.Thread( target = self._on_connect , kwargs=dict( event = self._ev ) )
					self._thred.start()



				def _on_connect( self , event = None  ) :
					"""

					:return:
					"""

					#self._connect_event = Clock.schedule_interval( my_callback , 1.0 )


					try :

						self._logger.info( ',,,on_connect...'  )
						self.url = ('http://%s:7080/bimini' %
									self.root.ids.server.text )
						self.send_url = ('http://%s:7080/bimini/click?' %
										 self.root.ids.server.text)
						self.send_key_url = ('http://%s:7080/bimini/key?' %
										 self.root.ids.server.text)


						self.root.ids.console_interface.text += '%s   ....attempting connection to %s\n' %\
																( timestamp() ,self.root.ids.server.text )


						self._screen_width = int( self.root.ids.window_width_slider.value )
						self._screen_height = int( self.root.ids.window_height_slider.value )

						Window.size = ( self._screen_width , self._screen_height )
						self.root.ids.cci_bimini_accordion.canvas.ask_update()

						try :
							urlopen( self.url , timeout = 5 )
							self.root.ids.current_connection_text.text = 'current connection: %s\n' \
																			% self.root.ids.server.text
							self.root.ids.console_interface.text += '%s   ....connected to %s\n' % ( timestamp() ,self.root.ids.server.text )
							self.move_to_accordion_item( self.root.ids.cci_bimini_accordion ,
												 'remote console' )

						except Exception as e :
							self._logger.error( e )
							self.root.ids.console_interface.text += '%s   ....could not connect to %s->%s\n' % \
																	( timestamp() ,self.root.ids.server.text , e.message )
							self.root.ids.desktop.source = './img/stop.png'
							popup = Popup(title='bimini error',
									content=Label( text = 'error in connecting to remote host...' ),
									size_hint=(None, None), size=(400, 200) )
							popup.open()
							self.root.ids.maelstrom_carousel_id.index = 0
							self.move_to_accordion_item( self.root.ids.cci_bimini_accordion , 'cci-bimini' )




						self.reload_desktop()
						self._connected = True


					except IOError as e :
						self._logger.error( e.message )
						self._connected = False

					except Exception as e :
						self._logger.error( e.message )
						self._connected = False




				@mainthread
				def reload_desktop( self , *args ) :
					"""

					:param args:
					:return:
					"""

					if self._ev.isSet() :
						sys.exit( 1 )

					try :
						desktop = Loader.image( self.url , nocache=True )
						desktop.bind( on_load=self.desktop_loaded )

					except Exception as e :
						self._clock_event.cancel()
						self._logger.error( 'reload_desktop ' + e.message )
						self.root.ids.desktop.source = './img/stop.png'
						sys.exit( 1 )



				@mainthread
				def desktop_loaded( self , desktop ) :
					"""

					:param desktop:
					:return:
					"""


					try :
						if desktop.image.texture:
							self.root.ids.desktop.texture = \
								desktop.image.texture
						del desktop

						if self._ev.isSet() :
							self._clock_event.cancel()

						self._clock_event = Clock.schedule_once(self.reload_desktop, .5 )
						self.root.current = 'desktop'
						#self.move_to_accordion_item( self.root.ids.cci_bimini_accordion ,
						#							 'remote console' )



					except IOError as e :
						self._logger.error( 'desktop_loaded ' + e.message )
					except Exception as e :
						self._clock_event.cancel()
						self._logger.error( 'desktop ' + e.message )
						self.root.ids.desktop.source = './img/stop.png'
						sys.exit( 1 )


				def send_click( self , event ):



					try :


						params = {'x': int(event.x),
								  'y': int(self.root.ids.desktop.size[1] -
										   event.y)}
						self._logger.info( '...event x: %d , event y: %d ....' % ( event.x , event.y ) )
						self._logger.info( self.send_url + urlencode( params ) )
						urlopen( self.send_url + urlencode( params ) ,  timeout = 5  )



					except Exception as e :
						self._clock_event.cancel()
						self.root.ids.desktop.source = './img/stop.png'
						self._logger.error( 'send_click ' + e.message )



				def send_key( self , key ):



					try :
						if not self._connected :
							self._clock_event.cancel()
							return

						params = {'key': int(key) }
						self._logger.info( '...event key:%d' %  key )
						self._logger.info( self.send_key_url + urlencode( params ) )
						s = self.send_key_url + urlencode( params )
						urlopen( s )

					except Exception as e :
						self._clock_event.cancel()
						self._logger.error( 'send_key ' + e.message )



				def on_pause(self):
					# save data
					return True




				def on_resume(self):
					# something
					pass





				def on_stop( self ) :
					"""

					:return:
					"""

					if self._thred :
						self._thred.join()



				def on_start( self ) :
					"""

					:return:
					"""

					"""
					devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
					for device in devices:
						self._logger.info( 'input device: %s  %s  %s' % ( device.fn , device.name , device.phys ) )

					self.root.ids.status_text.text = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S"  )
					self.root.ids.console_interface.text = timestamp() + '   ...no current connection...\n'
					"""
					pass


				def _on_rotate( self , rotation ) :
					"""

					:param rotation:
					:return:
					"""

					pass



				@mainthread
				def move_to_accordion_item( self , acc , tag = None ) :
					"""
					workaround for android nesting bug
					:param acc:
					:return:
					"""

					for child in acc.children :
						if child.title == tag :
							child.collapse = False
							child.canvas.ask_update()

							self.root.ids.desktop.focused = True
							return child
					return None




				def hook_keyboard( self , window, key , *largs ) :
					"""

					:param window:
					:param key:
					:param largs:
					:return:
					"""

					#escape


					if key != 27 :
						self.send_key( key )
						print 'key:%d' % key

					return False




				def _on_back_btn( self ) :
					"""

					:return:
					"""

					send_key( const_back_btn )











# --------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':

				Config.set('graphics','resizable',0 )


				Config.set( 'graphics', 'width', '480' )
				Config.set( 'graphics', 'height', '800' )
				Config.set( 'input', 'mouse', 'mouse,disable_multitouch' )


				#from kivy.core.window import Window

				Window.size = ( 480 , 800 )


				#Window.clearcolor = get_color_from_hex('#95a5a6')

				biminiApp().run()

