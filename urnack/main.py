

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
from kivy.clock import Clock , mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.settings import SettingsWithSidebar , SettingsWithSpinner
from kivy.uix.screenmanager import ScreenManager, \
	                               Screen ,\
	                               RiseInTransition ,\
								   SwapTransition , \
								   FallOutTransition , \
								   SlideTransition
Window.softinput_mode = 'pan'

# python standard
import os
import copy
import logging
import importlib
from time import gmtime, strftime , sleep
import subprocess as proc
import threading
import requests



#cci
import urnack.cci_mini_elastic as cci_elastic
import urnack.cci_mini_mongo as cci_mongo
from urnack import resource_factory \
	                     as resources , \
						 screen


#from scapy.all import *

kivy.require( '1.9.1' )

# ------------------------------------------------------------------------------------------------
class ConsoleAccordion( Accordion ) :

		btn_text = StringProperty('')
		_orientation = StringProperty('vertical')
		_inner_orientation = StringProperty( 'horizontal' )
		orientation_handler = ObjectProperty(None)
		_selected = ObjectProperty()

		stop = threading.Event()

		def __init__( self, *args, **kwargs):
			super( ConsoleAccordion , self ).__init__( *args, **kwargs)

			# get the original orientation
			self._orientation = 'horizontal' if Window.width > Window.height else 'vertical'
			# inform user
			self.btn_text = self._orientation
			self.orientation = self._orientation
			self._selected = None
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




# ------------------------------------------------------------------------------------------------
class urnackApp( App ) :
				"""
				urnack
				"""


				def __init__( self ) :
					"""

					:return:
					"""

					super( urnackApp , self ).__init__()

					self.settings_cls = SettingsWithSpinner

					#view manager
					self._view_manager = None
					self._console_count = 1
					self._full_screen_lst = list()
					self._is_full_screen = False

					Window.on_rotate = self._on_rotate



				# helpers
				@staticmethod
				def _retr_resource( resource_id ) :
					"""

					:param resource_id:
					:return ui resource:
					"""

					return resources.const_resource_ids[resource_id]



				# settings
				def build_settings( self , settings ) :
					"""

					:param settings:
					:return:
					"""
					settings.add_json_panel( 'cci-urnack contexts',
											  self.config ,
											  data=resources.settings_json )
					settings.add_json_panel( 'cci-urnack environment',
											  self.config ,
											  data=resources.settings_env_json )
					settings.add_json_panel( 'cci-urnack streams',
											 self.config ,
											 data=resources.settings_stream_json )
					self.use_kivy_settings = False



				def build_config( self , config ) :
					"""

					:param config:
					:return:
					"""
					config.setdefaults( 'stream',  {
													'packet_timeout': 3 ,
													'show_stream': 1 ,
													} )
					config.setdefaults( 'network-icmp', {
													'packet_timeout': 1 ,
													'show_stream': 1 ,
													'default_address' : 'www.chromaticuniverse.xyz'
													} )



				def on_start( self ) :
					"""

					:return:
					"""

					"""
					server_param =  [{ 'host' :'search-chromatic-search-p647s4rdqjcgub7tt7neealjn4.us-west-2.es.amazonaws.com' ,
										'port' : 80}]
					elastic_cci = cci_elastic.cci_mini_elastic( server_param , True )
					self.root.current_screen.ids.acc_item_elastic.text = elastic_cci.server_banner

					mongo_cci = cci_mongo.cci_mini_mongo( 'cci-aws-3' )
					self.root.current_screen.ids.acc_item_mongo.text = mongo_cci.device_info

					self.root.current_screen.ids.console_interfaces.text = 'blase'


					content = None
					with open( 'cci_mini_elastic.log-debug.log' ) as f :
						content = f.readlines()
					self.root.current_screen.ids.console_interfaces.text = '\n'.join( content )
					"""
					pass



				def on_pause(self):
					# save data
					return True


				def on_resume(self):
					# something
					pass


				def _on_rotate( self , rotation ) :
					"""

					:param rotation:
					:return:
					"""

					pass




				def accordion_touch_up( self , id = None ) :
					"""
					:return:
					"""

					"""
					acc = self.root.current_screen.ids.cci_accordion
					cci = None
					selected = None
					if not self._is_full_screen :
						self._full_screen_lst = list()
						for item in acc.children :
							self._full_screen_lst.append( item )
							if item.title == 'cci-urnack'  :
								cci = item
							if item.title == id  :
								selected = item
						self._full_screen_lst.remove( cci )
						self._full_screen_lst.remove( selected )
						for item in self._full_screen_lst :
							acc.remove_widget( item )
						self._is_full_screen = True
					else :
					  if id == 'cci-urnack' :
						cci = acc.children[0]
						acc.remove_widget( cci )
						self._full_screen_lst.reverse()
						for item in self._full_screen_lst :
							acc.add_widget( item )
						acc.add_widget( cci )
						self._is_full_screen = False

					"""
					pass



				def _selected_accordion_item( self  ) :
					"""

					:return accordion item selected:
					"""

					"""
					acc = self.root.current_screen.ids.cci_accordion
					cci = None
					selected = None
					for item in acc.children :
						try:
							if not item.collapse :
								if not self._is_full_screen :
									self._full_screen_lst = list()
									for item in acc.children :
										self._full_screen_lst.append( item )
										if item.title == 'cci-urnack'  :
											cci = item
									selected = item
									self._full_screen_lst.remove( cci )
									self._full_screen_lst.remove( selected )
									for item in self._full_screen_lst :
										acc.remove_widget( item )
									self._is_full_screen = True
								else :
								  if item.title  == 'cci-urnack' :
									cci = acc.children[0]
									acc.remove_widget( cci )
									self._full_screen_lst.reverse()
									for item in self._full_screen_lst :
										acc.add_widget( item )
									acc.add_widget( cci )
									self._is_full_screen = False
						except :
							pass
					"""
					pass




# --------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':

         urnackApp().run()
