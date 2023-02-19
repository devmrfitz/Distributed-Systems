#!/usr/bin/env python
import pika
import sys
import registry_pb2
from datetime import datetime
import uuid

servers = dict()
exchange_name='Generic_RPC'

MAXSERVERS=10
routing_id='registry_server'

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channelRPC = connection.channel()
registry_exchange='registry_rpc'
common_2serv_exchange='ServerExchange'
common_2client_ex='clientExchange'
channelRPC.exchange_declare(exchange=common_2client_ex,exchange_type='direct')
channelRPC.exchange_declare(exchange=common_2serv_exchange,exchange_type='direct')
channelRPC.exchange_declare(exchange=exchange_name,exchange_type='direct')
channelRPC.exchange_declare(exchange=registry_exchange,exchange_type='direct')

result = channelRPC.queue_declare(queue='registry_queue', exclusive=True)

queue_name = result.method.queue
channelRPC.queue_bind(exchange=exchange_name, queue=queue_name,routing_key=routing_id)
while(True):
    print(' [*] Waiting for REQUESTs. To exit press CTRL+C')

    request = registry_pb2.Request()
    response = registry_pb2.Response()

    def callback(ch, method, properties, body):
        
        request.ParseFromString(body)
        
        if(request.type==request.RequestType.FETCH_SERVER_LIST):
            print("[x] FETCH LIST REQUEST FROM LOCALHOST: ")
            response.type = registry_pb2.Response.ResponseType.REGISTER#FETCH_SERVER_LIST
            response.serverListResponse.servers.extend(servers.values())
            response.success = True

        elif(request.type==request.RequestType.REGISTER):
            print("[x] JOIN REQUEST FROM LOCALHOST: "+request.registerRequest.bindingkey)
            
            if(len(servers)<MAXSERVERS):
                # print("Registered Successfully")
                servers[request.registerRequest.name] = response.ServerListResponse.Server()
                servers[request.registerRequest.name].name = request.registerRequest.name
                servers[request.registerRequest.name].bindingkey = request.registerRequest.bindingkey

                response.type = registry_pb2.Response.ResponseType.REGISTER
                response.success=True

            else:
                # print("Failed to register!")

                response.type = registry_pb2.Response.ResponseType.REGISTER
                response.success=False

        ch.basic_cancel(consumer_tag)
        
        # print(ch,method,properties)
    consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channelRPC.start_consuming()

    if(request.type==request.RequestType.FETCH_SERVER_LIST):
        route_back=request.uuid
        channelRPC.basic_publish(exchange=registry_exchange,routing_key=route_back,body=response.SerializeToString())

    elif(request.type==request.RequestType.REGISTER):
        route_back=request.registerRequest.bindingkey
        channelRPC.basic_publish(exchange=registry_exchange,routing_key=route_back,body=response.SerializeToString())
    
    

connection.close()