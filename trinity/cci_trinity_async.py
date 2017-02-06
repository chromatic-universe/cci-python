# cci_trinity_async.py    william k. johnson  2016



import time
import json
import logging
import signal
import socket
import os
import subprocess as proc
import threading
import importlib
import socket
import signal

from tornado.ioloop import IOLoop
import tornado.gen
import urllib
import sys
import json
from time import sleep
import requests
import tornado.web
import tornado.websocket
import tornado.httpserver
from tornado.queues import Queue
from tornado.ioloop import PeriodicCallback
from tornado.locks import Semaphore
from tornado.process import Subprocess , CalledProcessError
#kafka
from kiel import clients

max_wait_seconds_before_shutdown  = 3


# cci
from application_vulture  import app ,\
	                             mongo_no_resource_exception , \
								 _logger
from streams import tr_utils , \
				    tr_sqlite , \
					tr_mongo_rest

lname = 'king-console-cci-maelstrom'
callback_class_dispatch = { 'document' : 'tr_payload_stalker' ,
							'stream'   :  'tr_stream-stalker' }
stream_mod = importlib.import_module( 'streams.tr_stream_manager'  )
stream_mongo_mod = importlib.import_module( 'streams.tr_mongo_rest'  )

# exclusive
policy_semaphore = Semaphore( 1 )
g_periodic_callbacks = dict()
probe_thred = None
http_tunnel_pid = None
default_stream_proxy_port = 7082
default_document_proxy_port = 7083
const_tunnel_process = 'cci-trinity-tunnel'
stream_bootstrap = None
default_policy_j = None
db_bootstrap = None
kp = None
TEMPLATE_PATH = os.path.join(os.path.join(os.path.dirname(__file__) , 'templates') )

socket_msg = ['app_services' , 'async_services' ,  'tunnel_services']
trinity_push_q = Queue()

trinity_push_clients = []

# ---------------------------------------------------------------------------------------------
def trinity_push_msg( message ) :
    for client in trinity_push_clients :
        client.write_message( message )


# ---------------------------------------------------------------------------------------------
class trinity_push_handler( tornado.websocket.WebSocketHandler ) :
        
        
        def open( self ) :
            """
            open
            """

            self.write_message(  socket_msg[1] +  " :...this is the cci async server speaking from a web socket on port 7082..." ) 
            self.write_message(  socket_msg[0] +  " :...this is the cci app server speaking from a web socket on port  7082..." )
            self.write_message(  socket_msg[2] +  " :...this is cci tunnel services speaking from a web socket on port 7082..." ) 

            trinity_push_clients.append( self )

          


        def on_message( self , message ) :
            """
            on_message
            """

            self.write_message( 'async_services:...ack...' )



        def on_close(self):
            """

            on_close
            """
            
            if self in trinity_push_clients :
                trinity_push_clients.remove( self )
           


        @classmethod
        def broadcast_to_clients( cls ) :
            """
            :class:
            :return:
            """

            for client in trinity_push_clients:
                client.write_message( '...broadcast....' + retr_local_ip_info() )



# ---------------------------------------------------------------------------------------------
def retr_local_ip_info() :
		"""

		:return lovsl ip:
		"""

		# local
		local_ip = '0.0.0.0'

		s = socket.socket( socket.AF_INET , socket.SOCK_DGRAM )
		try:

				local_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1],
								   [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
								   socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
				return local_ip

		except :
			# give it up for a lost cause
			pass

		finally:
			s.close()


		return local_ip


# --------------------------------------------------------------------------------------
class vulture_index(  tornado.web.RequestHandler ) :


			@tornado.gen.coroutine
			def get( self ) :

				try :
					s = 'http://%s:7080/trinity-vulture' % retr_local_ip_info()
					self.redirect( s )
				except :

					self.write( '..redirect failed..' )




# --------------------------------------------------------------------------------------
class queue_client() :

			def __init__(self):
				self.queued_items = Queue()


			@tornado.gen.coroutine
			def watch_queue(self):

				try :

					while True:
						items = yield self.queued_items.get()
						if items['moniker'] in g_periodic_callbacks :
							_logger.info( '..%s policy %s already in effect' % ( items['provider_type'] ,
																				 items['moniker']  ) )
							continue
						pc = PeriodicCallback( lambda: policy_callback( items['provider_type'] ,
																		items['moniker'] ,
																		items['db_bootstrap']) , int( items['interval'] ) * 1000 )
						_logger.info( '..started periodic callback with params%s' % json.dumps( items ) )
						pc.start()
						with ( yield policy_semaphore.acquire() ) :
							id = '%s-%s' % ( items['moniker'] , items['provider_type'] )
							g_periodic_callbacks[id] = pc

				except Exception as e :
					_logger.error( 'watch_queue: %s' % e.message )
				finally :
					policy_semaphore.release()



# --------------------------------------------------------------------------------------
class queue_session_client() :

			def __init__(self):
				self.queued_items = Queue()


			@tornado.gen.coroutine
			def watch_session_queue(self) :
				r = None
				try :
					while True:
						items = yield self.queued_items.get()
						r = requests.post('http://localhost:7080/mongo/update_device_status',
										  data =  json.dumps( items  ) )
				except Exception as e :
					_logger.error( 'session_watch_queue: %s' % e.message )




# --------------------------------------------------------------------------------------
class queue_stream_client() :

			def __init__(self):
				self.queued_items = Queue()


			@tornado.gen.coroutine
			def watch_stream_queue(self) :
				try :

					while True:
						items = yield self.queued_items.get()
						print ( items )
						#kp.send( lname , json.dumps( items ) )
				except Exception as e :
					_logger.error( 'watch_stream_queue: %s' % e.message )




# --------------------------------------------------------------------------------------
class stream_queue_handler_post_msg( tornado.web.RequestHandler ) :


			@tornado.gen.coroutine
			def post( self ) :
				"""

				:return:
				"""

				try :

					json_data = json.loads( self.request.body )
					print ( json_data )
					yield stream_client.queued_items.put( json_data )

				except Exception as e :
					_logger.error( 'stream_queue_handler_post_msg: %s' % e.message )




# --------------------------------------------------------------------------------------
class session_queue_handler_session_update( tornado.web.RequestHandler ) :


			@tornado.gen.coroutine
			def post( self ) :
				"""

				:return:
				"""

				try :

					json_data = json.loads( self.request.body )

					print ( json_data )
					yield session_client.queued_items.put( json_data )
					_logger.info( 'session queued a new item: %s' % self.request.body )
					self.write( 'queued a new item: %s' % self.request.body )
				except Exception as e :
					_logger.error( 'session_queue_handler_update_session: %s' % e.message )





# --------------------------------------------------------------------------------------
class queue_handler_start_policy( tornado.web.RequestHandler ) :


			@tornado.gen.coroutine
			def post( self ) :
				"""

				:return:
				"""

				try :

					json_data = json.loads( self.request.body )
					print ( json_data )
					yield client.queued_items.put( json_data )
					_logger.info( 'queued a new item: %s' % self.request.body )
					self.write( 'queued a new item: %s' % self.request.body )
				except Exception as e :
					_logger.error( 'queue_handler_start_policy: %s' % e.message )





# --------------------------------------------------------------------------------------
class queue_handler_stop_policy( tornado.web.RequestHandler ) :


			@tornado.gen.coroutine
			def post( self ) :
				"""

				:return:
				"""


				json_data = json.loads( self.request.body )
				moniker = json_data['moniker']
				id = '%s-%s' % ( json_data['moniker'] , json_data['provider_type'] )
				if id in g_periodic_callbacks :
					g_periodic_callbacks[id].stop()
					_logger.info( '...stopped...: %s' % id )
					self.write( '...stopped...: %s' % id  )
				else :
					_logger.warning( '...could not stop...policy not started: %s' % id )
					self.write( '...could not stop...policy not started: %s' % moniker )





# --------------------------------------------------------------------------------------
def create_ssh_tunnel_callback() :

			"""

			:return:
			"""


			pass




# --------------------------------------------------------------------------------------
def init_update_callback() :
            """

            :return:
            """

            try :
                trinity_push_msg( socket_msg[1] +  " :...async server ok..." ) 
                trinity_push_msg( socket_msg[0] +  " :...app server ok..." )
                trinity_push_msg( socket_msg[2] +  " :...tunnel services ok..." ) 
            except Exception as e :
                _logger.error( e )




# --------------------------------------------------------------------------------------
def start_policy_local() :
            """
            :param json policy global:
            :return:

            """
            try :


                if default_policy_j['moniker'] in g_periodic_callbacks :
                    _logger.info( '..%s policy %s already in effect' % ( items['provider_type'] ,
                                                                         items['moniker']  ) )
                    return
                pc = PeriodicCallback( lambda: policy_callback( default_policy_j['provider_type'] ,
                                                                default_policy_j['moniker'] ,
                                                                db_bootstrap ) ,
                                                                int( default_policy_j['run_interval'] ) * 1000 )
                _logger.info( '..started periodic callback local cal with params%s' % json.dumps( default_policy_j ) )
                pc.start()
                g_periodic_callbacks[id] = pc
                

            except Exception as e :
                _logger.error( 'start policy local: %s' % e.message )







# --------------------------------------------------------------------------------------
def start_heartbeat_callback() :

			"""

			:return:
			"""

			# hearbeat
			try :

				j = json.loads( tr_sqlite.retrieve_config_atom( 'trinity-update-interval' )['map'] )
				heartbeat_interval = j['update_interval']
				r = requests.get( 'http://localhost:7080/mongo/retr_device/%s' % tr_utils.local_mac_addr())
				device_info = r.json()['result']
				auth_http_id = device_info['auth_http_id']

				# start hearbeat
				pc = PeriodicCallback( lambda: update_status_callback( auth_http_id ) ,
																	   int( heartbeat_interval )  * 1000 )
				_logger.info( '..started periodic heartbeat callback with interval of %d...' % int( heartbeat_interval ) )
				pc.start()

			except :
				# non-critical ; move on
				pass







# --------------------------------------------------------------------------------------
class cci_sibling_probe( tornado.web.RequestHandler )  :
			"""
			:return sibling device id
			"""


			pass




# --------------------------------------------------------------------------------------
def probe_siblings_thred() :
			"""

			:return:
			"""

			ip = tr_utils.retr_local_ip_info()

			sleep( 3 )



# --------------------------------------------------------------------------------------
def sig_handler( sig , frame ) :
			"""

			:param sig:
			:param frame:
			:return:
			"""
			_logger.warning('...caught signal: %s', sig )
			tornado.ioloop.IOLoop.instance().add_callback( shutdown )





# --------------------------------------------------------------------------------------
def shutdown() :
			"""
			:return:
			"""


			_logger.info( '....will shutdown in %s seconds ...' , max_wait_seconds_before_shutdown )
			io_loop = IOLoop.instance()

			deadline = time.time() + max_wait_seconds_before_shutdown

			for key , value in g_periodic_callbacks.iteritems() :
				if value.is_running() :
					_logger.info( '...shutting down policy %s ' %  key )
					value.stop()


			def stop_loop():
				now = time.time()
				if now < deadline and ( io_loop._callbacks or io_loop._timeouts ) :
					io_loop.add_timeout( now + 0.5 , stop_loop )
					io_loop.add_timeout( now + 0.5 , stop_loop )
				else:
					io_loop.stop()

			stop_loop()
			_logger.info( '...shutdown....' )



# -----------------------------------------------------------------------------------------
def update_status_callback( http_id  ) :

			"""

			`:param http record ibject id:
			:return:
			"""

			try :

				r = requests.post( 'http://localhost:7080/mongo/update_http_server_status' ,
								   data = json.dumps( { "_id" : http_id ,
													     "active" : "true" ,
														 "last_known_ip" : retr_local_ip_info() ,
													     "last_known_real_ip" : "0.0.0.0"
								  					   }
								   					)
								 )


			except Exception as e :
				_logger.error( e.message )





# -----------------------------------------------------------------------------------------
def policy_callback( provider_type , moniker , db  ) :
            """

            :param items : json
            :return:
            """


            live_stalker = None
            try :
                print ( "instantiating {:s} policy->{:s}  db={:s}".format( provider_type ,  moniker  , db  ) ) 
                stalker = getattr( stream_mod , callback_class_dispatch['document'] )
                live_stalker = stalker( db_connect_str = db )
                live_stalker.prepare()
                live_stalker.stalk()
            except Exception as e :
                print ( e.message )
            finally :
                # explicit delete; callbacks are reentrant and objects
                # do not go out of scope
                del live_stalker





# --------------------------------------------------------------------------------------
if __name__ == "__main__":

                          
                # stream
                try :                             
                        j = json.loads( tr_sqlite.retrieve_config_atom( 'trinity-stream-toggle' )['map'] )
                        if j['status'] == 'on' :
                                stream_bootstrap = json.loads( tr_sqlite.retrieve_config_atom( 'trinity-kafka-bootstrap' )['map'] )
                                _logger.info( '...starting stream tunneler ....' )
                                s = str( stream_bootstrap['bootstrap_servers'] )
                                kp = clients.Producer( brokers= [s] )
                                kp.connect()
                                _logger.info( '...streaming bootstrap initialized...%s' % s )
                except Exception as e :
                    _logger.error( '...broken streaming..%s' % e.message )
                
                # default policies
                try :
                    default_policy_j = tr_sqlite.retrieve_policy( 'default' , 'document' )
                    _logger.info( j )
                except Exception as e :
                    _logger.error( '..could not retrieve document policy...%s' % e.message  )
                         

                # queue vulture
                client = queue_client()
                session_client = queue_session_client()
                stream_client = queue_stream_client()
                is_running = False

                pid = None
                try :
                    with open( 'cci-trinity-vulture-pid' , 'r' ) as pidfile :
                        pid = pidfile.read().strip()
                    with open( 'bootstrap_db' , 'r' ) as boot :
                        db_bootstrap = boot.readline().split( '=' )[1].strip()
                     
                except :
                     pass

                # check if process is running
                if pid :
                    try :
                    # throws exception if process doesn't exist
                        os.kill( int( pid ) , 0 )
                        is_running = True
                    except :
                        # pid not running
                        pass

                if not is_running :
                    # Watch the queue for when new items show up
                    _logger.info( '...initializing queue vulture....' )
                    # policies
                    tornado.ioloop.IOLoop.instance().add_callback( client.watch_queue )
                    # session status
                    tornado.ioloop.IOLoop.instance().add_callback( session_client.watch_session_queue )
                    # stream data
                    tornado.ioloop.IOLoop.instance().add_callback( stream_client.watch_stream_queue )


                    settings = {
                                "static_path": os.path.join(os.path.dirname(__file__), "static"),
                               }
                    # create the web server with async coroutines
                    _logger.info( '...initializing http services....' )
                    application = tornado.web.Application([	( r'/trinity-vulture/start', queue_handler_start_policy ) ,
                                                            ( r'/trinity-vulture/stop' ,  queue_handler_stop_policy ) ,
                                                            ( r'/trinity-vulture' ,  vulture_index ) ,
                                                            ( r'/trinity-vulture/post_stream_msg' ,  stream_queue_handler_post_msg ) ,
                                                            ( r'/trinity-vulture/session_update' ,  session_queue_handler_session_update ) ,
                                                            ( r'/trinity-vulture/sibling' ,  cci_sibling_probe ) ,
                                                            ] , Debug=True ,  **settings )

                    _logger.info( '...starting listener on port 7081....' )
                    application.listen( 7081 )

                    # start siblings probe
                    probe_thred = threading.Thread( target = probe_siblings_thred ).start()
                    # start http tunnel for local passthrough(all traffic is tnneled , even local)


                    # signal handlers
                    _logger.info( '...setting system signal handlers....' )
                    signal.signal( signal.SIGTERM , sig_handler )
                    signal.signal( signal.SIGINT , sig_handler )

                     # write pid
                    with open( 'cci-trinity-vulture-pid' , 'w' ) as pidfile :
                         pidfile.write( str( os.getpid() ) + '\n'  )


                    # start heartbeat in 30 seconds
                    _logger.info( '...scheduling hearbeat ....' )
                    tornado.ioloop.IOLoop.instance().call_later( 30 , start_heartbeat_callback )

                    # start default document policy in 60 seconds
                    _logger.info( '...scheduling default document policy ....' )
                    tornado.ioloop.IOLoop.instance().call_later( 60 , start_policy_local )

                    # start web socket push
                    push_application = tornado.web.Application([ (r'/trinity-stream', trinity_push_handler ) ,
                                                                    ])    
                    _logger.info( '...starting web socket push server on port 7082 ....' )
                    http_server = tornado.httpserver.HTTPServer( push_application ) 
                    http_server.listen( 7082 )
                    
                    # set final callback for 10 seconds to signal init successs
                    _logger.info( '...scheduling fanfare ....' )
                    tornado.ioloop.IOLoop.instance().call_later( 15 , init_update_callback )

                    
                    # run main io
                    _logger.info( '...starting main io loop ....' )
                    tornado.ioloop.IOLoop.instance().start()

                else :
                    _logger.info( '...server already running... pid %s....'  % pid )
                    sys.exit( 1 )
