import paramiko
import signal
from sshtunnel import SSHTunnelForwarder
from time import sleep
import os
import sys
import threading

server = None


# --------------------------------------------------------------------------------------
def sig_handler( sig , frame ) :


				os.kill( os.getpid() , signal.SIGTERM )




if __name__ == '__main__':

				#signal.signal( signal.SIGTERM , sig_handler )
				signal.signal( signal.SIGINT , sig_handler )

				server = SSHTunnelForwarder(
											('localhost', 8765),
											ssh_username="ubuntu",
											ssh_pkey='./cci-develop.pem' ,
											local_bind_address=('127.0.0.1' , 3128 ) ,
											remote_bind_address=('127.0.0.1', 8888 )
											)

				server.start()

				print(server.local_bind_port)

				while True :
					sleep( 1 )



