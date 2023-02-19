import pika
import registry_pb2
import sys
import time
import uuid
from datetime import datetime
# registry server has special binding key named as registry server
unique_id = str(uuid.uuid1())


clientele = set()
MAX_CLIENTS = 10

print(unique_id)
servers = dict()
articles=[]
following=[]
MAXFOLLOWERS=3

SERVER_NAME = input("Enter server name: ")
routing_id='registry_server'
registry_exchange='registry_rpc'
common_2client_ex='clientExchange'
#all servers bind to registry ka exchange for info from it

exchange_name='Generic_RPC'#can add this to 
# and the serverbinds to this one so all messages to server are send via this exchange

#server is client first
common_2serv_exchange='ServerExchange'
# here the exchnage is for one side clear communication between client to servers and all servers bind to it 



connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channelRPC = connection.channel()


# each client declares a queue and a server
# channelRPC.exchange_declare(exchange=exchange_name,exchange_type='direct')#khudka exchange

# server 1 receive queue is same as its uuid
result = channelRPC.queue_declare(queue=SERVER_NAME, exclusive=True)#khudki queue
queue_name = result.method.queue
channelRPC.queue_bind(exchange=common_2serv_exchange, queue=queue_name,routing_key=unique_id)


# def checkupdate():


def request_registration():
    
    channelRPC.queue_bind(exchange='registry_rpc', queue=queue_name,routing_key=unique_id)

    register_request = registry_pb2.Request()
    register_request.type = registry_pb2.Request.RequestType.REGISTER
    register_request.registerRequest.name = SERVER_NAME  # same as exchange name
    register_request.registerRequest.bindingkey = unique_id


    channelRPC.basic_publish(exchange=exchange_name,routing_key=routing_id,body=register_request.SerializeToString())

# print("ARC 2")

    print(' [*] Waiting for Registry Servers Response. To exit press CTRL+C')


    def callback(ch, method, properties, body):
        register_responce=registry_pb2.Response()
        register_responce.ParseFromString(body)
        if(register_responce.success):
            print(" [x] " +" SUCCESS")
        else:
            print(" [x] " +" FAILURE")
        ch.basic_cancel(consumer_tag)
        # print(ch,method,properties)
    consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    #used to register a consumer to a queue
    #also tells queue what fucntion to call when message is received


    channelRPC.start_consuming()

def forwardReq(request):
    response = registry_pb2.Response()
    if(len(following)!=0):
        channelRPC.basic_publish(exchange=common_2serv_exchange,routing_key=following[0],body=request.SerializeToString())


        method_frame, header_frame, body = channelRPC.basic_get(queue=queue_name, auto_ack=True)

        if method_frame is not None:
            # If a message was retrieved, invoke the callback function
            response.ParseFromString(body)
            if(response.success):
                print(" [x] " +" SUCCESS Articles Retrieved")
                
            else:
                print(" [x] " +" FAILURE articles")

            # ch.basic_cancel(consumer_tag)
        
        # consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback2, auto_ack=True)
        print(response)
        return response.getArticlesResponse.articles


        # def callback2(ch, method, properties, body):
            
        #     response.ParseFromString(body)
        #     if(response.success):
        #         print(" [x] " +" SUCCESS Articles Retrieved")
                

        #     else:
        #         print(" [x] " +" FAILURE articles")

        #     ch.basic_cancel(consumer_tag)
        
        # consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback2, auto_ack=True)

        
        # return response.getArticlesResponse.articles
        
        # def callback(ch, method, properties, body):
            
        #     time.sleep(3)
        #     def date_parser(date):
        #         return datetime.strptime(date, "%d/%m/%Y")

        
        #     response.type = registry_pb2.Response.ResponseType.GET_ARTICLES
        #     if request.uuid not in clientele:
        #         response.success = False
        #     else:
        #         response.success = True
        #         article_type = request.getArticlesRequest.articleRequest.type
        #         author = request.getArticlesRequest.articleRequest.author
        #         from_date = request.getArticlesRequest.articleRequest.date

        #         if article_type == registry_pb2.ArticleRequest.ArticleType.UNSPECIFIED and author == "" and from_date == "":
        #             response.success = False
        #         else:
        #             for article in articles:
        #                 if article_type == registry_pb2.ArticleRequest.ArticleType.UNSPECIFIED or article_type == article.articleRequest.type:
        #                     if author == "" or author == article.articleRequest.author:
        #                         if from_date == "" or \
        #                                 date_parser(from_date) <= date_parser(article.articleRequest.date):
        #                             response.getArticlesResponse.articles.append(article)
    
    return response.getArticlesResponse.articles

    


def runserver():

    while(True):
        print(' [*] Waiting for REQUESTs. To exit press CTRL+C')

        request = registry_pb2.Request()
        response = registry_pb2.Response()

        def callback(ch, method, properties, body):
            
            request.ParseFromString(body)
            

            if(request.type==request.RequestType.JOIN_SERVER):
                print("[x] JOIN REQUEST FROM: "+request.uuid)
                if(len(clientele)<MAX_CLIENTS):
                    response.type = registry_pb2.Response.ResponseType.JOIN_SERVER #FETCH_SERVER_LIST
                    response.serverListResponse.servers.extend(servers.values())
                    response.success = True
                    clientele.add(request.uuid)

                    #adds the clients id to exchange khudka
                else:
                    response.type = registry_pb2.Response.ResponseType.JOIN_SERVER
                    response.success = False

            elif(request.type==request.RequestType.LEAVE_SERVER):
                print("[x] LEAVE REQUEST FROM: "+request.uuid)
                if(len(clientele)>=0):
                    response.type = registry_pb2.Response.ResponseType.LEAVE_SERVER#FETCH_SERVER_LIST
                    response.success = True
                    clientele.remove(request.uuid)
                    #removes the clients id to exchange khudka

                elif(request.uuid not in clientele):
                    response.type = registry_pb2.Response.ResponseType.LEAVE_SERVER#FETCH_SERVER_LIST
                    response.success = False
                    
                # print("[x] JOIN REQUEST FROM LOCALHOST: "+request.registerRequest.bindingkey)


            elif(request.type==request.RequestType.GET_ARTICLES):
                print("[x] ARTICLE REQUEST FROM: "+request.uuid)
                retresp=forwardReq(request)
                time.sleep(3)
                def date_parser(date):
                    return datetime.strptime(date, "%d/%m/%Y")

            
                response.type = registry_pb2.Response.ResponseType.GET_ARTICLES
                if request.uuid not in clientele:
                    response.success = False
                else:
                    response.success = True
                    article_type = request.getArticlesRequest.articleRequest.type
                    author = request.getArticlesRequest.articleRequest.author
                    from_date = request.getArticlesRequest.articleRequest.date

                    if article_type == registry_pb2.ArticleRequest.ArticleType.UNSPECIFIED and author == "" and from_date == "":
                        response.success = False
                    else:
                        for article in articles:
                            if article_type == registry_pb2.ArticleRequest.ArticleType.UNSPECIFIED or article_type == article.articleRequest.type:
                                if author == "" or author == article.articleRequest.author:
                                    if from_date == "" or \
                                            date_parser(from_date) <= date_parser(article.articleRequest.date):
                                        response.getArticlesResponse.articles.append(article)
                response.getArticlesResponse.articles.extend(retresp)


            elif(request.type==request.RequestType.PUBLISH_ARTICLE):
                
                print("[x] ARTICLE PUBLISH REQUEST FROM: "+request.uuid)
                
                response.type = registry_pb2.Response.ResponseType.PUBLISH_ARTICLE
                if request.uuid not in clientele:
                    response.success = False
                else:
                    article = request.publishArticleRequest.article
                    article.articleRequest.date = datetime.now().strftime("%d/%m/%Y")
                    articles.append(article)
                    response.success = True
            
            elif(request.type==request.RequestType.FOLLOW):
                
                print("[x] FOLLOW REQUEST FROM SERVER: "+request.uuid)

                
                response.type = registry_pb2.Response.ResponseType.FOLLOW
                

                if (len(followers)<MAXFOLLOWERS):
                    response.success = True
                    followers.append(request.uuid)
                else:
                    response.success = False
            

                
                
                
                # if(len(servers)<MAXSERVERS):
                #     # print("Registered Successfully")
                #     servers[request.registerRequest.name] = response.ServerListResponse.Server()
                #     servers[request.registerRequest.name].name = request.registerRequest.name
                #     servers[request.registerRequest.name].bindingkey = request.registerRequest.bindingkey

                #     response.type = registry_pb2.Response.ResponseType.REGISTER
                    # response.success=True

                # else:
                #     # print("Failed to register!")

                #     response.type = registry_pb2.Response.ResponseType.REGISTER
                #     response.success=False

            ch.basic_cancel(consumer_tag)
            
            # print(ch,method,properties)
        consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

        channelRPC.start_consuming()

        # if(request.type==request.RequestType.JOIN_SERVER or request.type==request.RequestType.LEAVE_SERVER or request.type==request.RequestType.GET_ARTICLES or ):
        route_back=request.uuid
        channelRPC.basic_publish(exchange=common_2client_ex,routing_key=route_back,body=response.SerializeToString())

def follow():
    serv_bkey=input("Enter bindingkey for Server to Follow: ")
    following.append(serv_bkey)
    # channelRPC.queue_bind(exchange=common_2client_ex, queue=queue_name,routing_key=unique_id)#cos receive will be from there
    # register_request = registry_pb2.Request()
    # register_request.type = registry_pb2.Request.RequestType.FOLLOW
    # register_request.uuid = unique_id

    # channelRPC.basic_publish(exchange=common_2serv_exchange,routing_key=serv_bkey,body=register_request.SerializeToString())

    # print(' [*] Waiting for Follow Server Responce. To exit press CTRL+C')

    # def callback(ch, method, properties, body):
    #     responce=registry_pb2.Response()
    #     responce.ParseFromString(body)
    #     if(responce.success):
    #         print(" [x] " +" SUCCESS")
    #     else:
    #         print(" [x] " +" FAILURE")
    #     ch.basic_cancel(consumer_tag)
    #     # print(ch,method,properties)
    # consumer_tag=channelRPC.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    # #used to register a consumer to a queue
    # channelRPC.start_consuming()


request_registration()
print("######[[[[[   SERVER INITIALIZATION    ]]]]]######")
print("----|   1.                  Start Server    |---- ")
print("----|   2.                  Follow Server   |---- ")
x=input("How would you like to proceed [ 1 | 2 ] : ")
if(x=='1'):
    runserver()

elif(x=='2'):
    follow()
    print("Server Starting . . .")
    runserver()


connection.close()