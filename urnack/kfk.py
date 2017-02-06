import threading, logging, time

from kafka import KafkaConsumer


class Consumer(threading.Thread):
    daemon = True

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers='cci-aws-1:9092',
                                 auto_offset_reset='earliest')
        consumer.subscribe( ['jesus'] )

        for message in consumer:
            print (message)

if __name__ == "__main__" :            

        consumer = KafkaConsumer(bootstrap_servers='cci-aws-1:9092',
                                 auto_offset_reset='earliest')
        consumer.subscribe( ['jesus'] )

        for message in consumer:
           print (message)


