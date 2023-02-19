# create a program which is a server that uses grpc to communicate with a client and registry server
# the server should be able to register itself with the registry server
# the server should be able to receive a request from the client and return a response
# the server should be able to unregister itself with the registry server
# the server should be able to handle multiple clients at the same time
# the server should be able to handle multiple requests from the same client at the same time
from concurrent import futures
from datetime import datetime
from constants import REGISTRY_SERVER_PORT
import grpc
import time
import sys
import threading
import concurrent.futures
import registry_pb2
import registry_pb2_grpc
from random import randint

# create a class for the server

# context = grpc.RpcContext()
SERVER_PORT = str(randint(10000, 60000))
SERVER_NAME = input("Enter server name: ")
MAX_CLIENTS = 10
clientele = set()
articles = []


class Server(registry_pb2_grpc.ServerServicer):
    def JoinServer(self, request, context):
        assert request.type == registry_pb2.Request.RequestType.JOIN_SERVER
        print("JOIN REQUEST FROM ", request.uuid)
        print("Request: ", str(request))
        response = registry_pb2.Response()
        response.type = registry_pb2.Response.ResponseType.JOIN_SERVER
        if len(clientele) < MAX_CLIENTS:
            clientele.add(request.uuid)

            response.success = True
        else:
            response.success = False
        print("Clientele: ", clientele)
        return response

    def LeaveServer(self, request, context):
        assert request.type == registry_pb2.Request.RequestType.LEAVE_SERVER
        print(f"LEAVE REQUEST FROM {request.uuid}")
        response = registry_pb2.Response()
        response.type = registry_pb2.Response.ResponseType.LEAVE_SERVER
        if request.uuid in clientele:
            clientele.remove(request.uuid)
            response.success = True
        else:
            response.success = False
        print("----------------------------------------")
        return response

    def GetArticles(self, request, context):
        assert request.type == registry_pb2.Request.RequestType.GET_ARTICLES
        print(f"ARTICLES REQUEST FROM {request.uuid}")
        print("Request: ", str(request))
        response = registry_pb2.Response()
        response.type = registry_pb2.Response.ResponseType.GET_ARTICLES
        if request.uuid in clientele:
            article_type = request.getArticlesRequest.articleRequest.type
            article_date = request.getArticlesRequest.articleRequest.date
            article_author = request.getArticlesRequest.articleRequest.author
            response.success = True
            if article_type == registry_pb2.ArticleRequest.ArticleType.UNSPECIFIED and article_date == "" and article_author == "":
                response.success = False
            else:
                for article in articles:
                    article = article.article
                    if article_type == registry_pb2.ArticleRequest.ArticleType.UNSPECIFIED or article_type == article.articleRequest.type:
                        if article_author == "" or article_author == article.articleRequest.author:
                            if article_date == "" or (datetime.strptime(article_date, "%d/%m/%Y") <= datetime.strptime(article.articleRequest.date, "%d/%m/%Y")):
                                response.getArticlesResponse.articles.append(article)
        else:
            response.success = False
        print("----------------------------------------")
        return response

    def PublishArticle(self, request, context):
        assert request.type == registry_pb2.Request.RequestType.PUBLISH_ARTICLE
        print(f"PUBLISH ARTICLE REQUEST FROM {request.uuid}")
        response = registry_pb2.Response()
        response.type = registry_pb2.Response.ResponseType.PUBLISH_ARTICLE
        if request.uuid in clientele:
            articles.append(request.publishArticleRequest)
            response.success = True
        else:
            article = request.publishArticleRequest.article
            article.articleRequest.date = datetime.now().strftime("%d/%m/%Y")
            articles.append(article)
            response.success = False
        print("----------------------------------------")
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    registry_pb2_grpc.add_ServerServicer_to_server(Server(), server)
    server.add_insecure_port(f"localhost:{SERVER_PORT}")
    while True:
        help_text = """
        1. Send Register request
        2. Run Primary server
        3. Follow another server
        4. Exit
        """
        print(help_text)
        choice = int(input("Enter your choice: "))
        if choice == 1:
            with grpc.insecure_channel(f"localhost:{REGISTRY_SERVER_PORT}", options=(('grpc.enable_http_proxy', 0),)) as channel:
                registry_stub = registry_pb2_grpc.RegistryServerStub(channel)
                response = registry_stub.Register(registry_pb2.Request(
                    type=registry_pb2.Request.RequestType.REGISTER,
                    registerRequest=registry_pb2.Request.RegisterRequest(name=SERVER_NAME,
                                                                         address=f"localhost:{SERVER_PORT}")))
            print("Registration request: SUCCESS" if response.success else "Registration request: FAIL")
        elif choice == 2:
            primary_server = threading.Thread(target=server.start)
            primary_server.start()
            print("Primary server started")
        elif choice == 3:
            pass
        elif choice == 4:
            server.stop(0)
            sys.exit(0)


if __name__ == '__main__':
    serve()
