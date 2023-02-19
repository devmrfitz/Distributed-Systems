import pika
import registry_pb2
import sys
from datetime import datetime

import uuid
# registry server has special binding key named as registry server
unique_id = str(uuid.uuid1())

print(unique_id)

servers=[]

CLIENT_NAME = input("Enter Client Name: ")
routing_id='registry_server'
registry_exchange='registry_rpc'
registry_queue_name='registry_server_queue'
exchange_name='Generic_RPC'
common_2serv_exchange='ServerExchange'# all servers their queues bind to it
common_2client_ex='clientExchange'

#server is client first

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channelRPC = connection.channel()

# client_queues are not exclusive
# each client declares a queue and a server
# channelRPC.exchange_declare(exchange=exchange_name,exchange_type='direct')#khudka exchange

# server 1 receive queue is same as its uuid
result = channelRPC.queue_declare(queue=CLIENT_NAME, exclusive=True)#khudki queue
queue_name = result.method.queue
channelRPC.queue_bind(exchange=common_2client_ex, queue=queue_name, routing_key=unique_id)

def GetArticles():
    print("\nAvailable servers:")
    for i, server in enumerate(servers):
        print(f"{i+1}. {server.name}({server.bindingkey})")
    choice = int(input("Enter your choice: "))
    server = servers[choice-1]
    print("""Choose an Article Type or select 0 to apply no type filter:
    0. No filter
    1. Sports
    2. Fashion
    3. Politics""")
    choice = int(input("Enter your choice: "))
    if choice == 0:
        article_type = registry_pb2.ArticleRequest.ArticleType.UNSPECIFIED
    elif choice == 1:
        article_type = registry_pb2.ArticleRequest.ArticleType.SPORTS
    elif choice == 2:
        article_type = registry_pb2.ArticleRequest.ArticleType.FASHION
    elif choice == 3:
        article_type = registry_pb2.ArticleRequest.ArticleType.POLITICS
    author = input("Enter author name or leave blank: ")

    date = input("Enter date in DD/MM/YYYY format or leave blank: ")

    request = registry_pb2.Request()
    request.uuid = unique_id
    request.type = registry_pb2.Request.RequestType.GET_ARTICLES
    request.getArticlesRequest.articleRequest.type = article_type
    request.getArticlesRequest.articleRequest.author = author
    request.getArticlesRequest.articleRequest.date = date
    channelRPC.basic_publish(exchange=common_2serv_exchange,routing_key=server.bindingkey,body=request.SerializeToString())

    print(' [*] Waiting for Servers Response. To exit press CTRL+C')

    def callback2(ch, method, properties, body):
        response=registry_pb2.Response()
        response.ParseFromString(body)
        if(response.success):
            print(" [x] " +" SUCCESS Articles")
            print("Articles:")
            for article in response.getArticlesResponse.articles:
                print(str(article))

        else:
            print(" [x] " +" FAILURE articles")
        ch.basic_cancel(consumer_tag)
        
    consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback2, auto_ack=True)

    channelRPC.start_consuming()

def LeaveServer(choice):

    server = servers[choice-1]
    
    request = registry_pb2.Request()
    request.uuid = unique_id
    request.type = registry_pb2.Request.RequestType.LEAVE_SERVER
    channelRPC.basic_publish(exchange=common_2serv_exchange,routing_key=server.bindingkey,body=request.SerializeToString())
    # print(str(request)+" "+server.bindingkey)

    print(' [*] Waiting for Servers Leave Response. To exit press CTRL+C')

    def callback2(ch, method, properties, body):
        response=registry_pb2.Response()
        response.ParseFromString(body)
        if(response.success):
            print(" [x] " +" SUCCESS")
        else:
            print(" [x] " +" FAILURE")
        ch.basic_cancel(consumer_tag)
        
    consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback2, auto_ack=True)

    channelRPC.start_consuming()

def JoinServer(choice):

    server = servers[choice-1]
    
    request = registry_pb2.Request()
    request.uuid = unique_id
    request.type = registry_pb2.Request.RequestType.JOIN_SERVER
    channelRPC.basic_publish(exchange=common_2serv_exchange,routing_key=server.bindingkey,body=request.SerializeToString())
    # print(str(request)+" "+server.bindingkey)

    print(' [*] Waiting for Servers Acceptance Response. To exit press CTRL+C')

    def callback2(ch, method, properties, body):
        response=registry_pb2.Response()
        response.ParseFromString(body)
        if(response.success):
            print(" [x] " +" SUCCESS")
        else:
            print(" [x] " +" FAILURE")
        ch.basic_cancel(consumer_tag)
        
    consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback2, auto_ack=True)

    channelRPC.start_consuming()

def GetServerList():
# channelRPC.queue_bind(exchange=exchange_name, queue=registry_queue_name,routing_key=routing_id)
    channelRPC.queue_bind(exchange='registry_rpc', queue=queue_name, routing_key=unique_id)

    register_request = registry_pb2.Request()
    register_request.type = registry_pb2.Request.RequestType.FETCH_SERVER_LIST
    register_request.uuid= unique_id# same as exchange name

    channelRPC.basic_publish(exchange=exchange_name,routing_key=routing_id,body=register_request.SerializeToString())

    print(' [*] Waiting for Registry Server Response. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        response=registry_pb2.Response()
        response.ParseFromString(body)
        if(response.success):
            print(" [x] " +" SUCCESS")
            for server in response.serverListResponse.servers:
                # print(server.name, server.bindingkey)
                servers.append(server)
        else:
            print(" [x] " +" FAILURE")
        ch.basic_cancel(consumer_tag)
        
    consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channelRPC.start_consuming()

def publish_article():

    print("Available servers:")
    for i, server in enumerate(servers):
        print(f"{i+1}. {server.name}({server.bindingkey})")
    choice = int(input("Enter your choice: "))
    server = servers[choice-1]

    print("""Choose an Article Type:
    1. Sports
    2. Fashion
    3. Politics""")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        article_type = registry_pb2.ArticleRequest.ArticleType.SPORTS
    elif choice == 2:
        article_type = registry_pb2.ArticleRequest.ArticleType.FASHION
    elif choice == 3:
        article_type = registry_pb2.ArticleRequest.ArticleType.POLITICS
    author = input("Enter author name or leave blank: ")
    content = input("Enter article content: ")

    request = registry_pb2.Request()
    request.uuid = unique_id
    request.type = registry_pb2.Request.RequestType.PUBLISH_ARTICLE
    request.publishArticleRequest.article.articleRequest.type = article_type
    request.publishArticleRequest.article.content = content
    request.publishArticleRequest.article.articleRequest.author = author

    channelRPC.basic_publish(exchange=common_2serv_exchange,routing_key=server.bindingkey,body=request.SerializeToString())

    print(' [*] Waiting for Servers Publication Status. To exit press CTRL+C')

    def callback2(ch, method, properties, body):
        response=registry_pb2.Response()
        response.ParseFromString(body)
        assert response.type == registry_pb2.Response.ResponseType.PUBLISH_ARTICLE
        if(response.success):
            print(" [x] " +" SUCCESS ARTICLE PUBLISHED ")
        else:
            print(" [x] " +" FAILURE")
        ch.basic_cancel(consumer_tag)
        
    consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback2, auto_ack=True)

    channelRPC.start_consuming()



def avail():
    print("Available servers:")
    for i, server in enumerate(servers):
        print(f"{i+1}. {server.name}({server.bindingkey})")

while(True):
    print("######[[[[[   CLIENT DASHBOARD    ]]]]]######")
    print("1. GetServerList ")
    print("2. Publish Article")
    print("3. Available Servers")
    print("4. Join Server")
    print("5. Leave Server")
    print("6. Get Articles")

    x=int(input("Proceed with :"))
    if(x==1):
        GetServerList()
        
    elif(x==2):
        publish_article()
    elif(x==3):
        avail()
    elif(x==4):
        i=int(input("Input Server Number to Join: "))
        JoinServer(i)
    elif(x==5):
        i=int(input("Input Server Number to Leave: "))
        LeaveServer(i)
    elif(x==6):
        GetArticles()

connection.close()


