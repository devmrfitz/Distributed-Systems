# create a program which is a client that uses grpc to communicate with a server and registry server
# the client should be able to send a request to the server and receive a response from the server
# the client should be able to register itself with the registry server
# the client should be able to unregister itself with the registry server
# the client should be able to handle multiple requests at the same time
# the client should be able to handle multiple servers at the same time
# the client should be able to handle multiple requests to the same server at the same time
# the client should be able to handle multiple requests to different servers at the same time
# the client should be able to handle multiple requests to the same server and different servers at the same time
import datetime

import grpc
import time
import sys
import threading
import concurrent.futures

import uuid as uuid

import registry_pb2
import registry_pb2_grpc
from constants import REGISTRY_SERVER_PORT

servers = []
uuid = str(uuid.uuid4())
def client(servers):
    while True:
        help_text = """
            1. Fetch server list from registry server
            2. Join server
            3. Leave server
            4. Get articles
            5. Publish article
            6. Exit
            """
        print(help_text)
        choice = int(input("Enter your choice: "))
        if choice == 1:
            with grpc.insecure_channel(f"localhost:{REGISTRY_SERVER_PORT}") as channel:
                stub = registry_pb2_grpc.RegistryServerStub(channel)
                request = registry_pb2.Request()
                request.type = registry_pb2.Request.RequestType.FETCH_SERVER_LIST
                response = stub.FetchServerList(request)
                servers = response.getServerListResponse.servers
                print(servers)

        elif choice == 2:
            if len(servers) == 0:
                print("No servers available")
            else:
                print("Available servers: ")
                for i in range(len(servers)):
                    print(f"{i+1}. {servers[i].name}({servers[i].address})")
                server_choice = int(input("Enter server number: "))
                with grpc.insecure_channel(f"{servers[server_choice-1].address}", options=(('grpc.enable_http_proxy', 0),)) as channel:
                    stub = registry_pb2_grpc.ServerStub(channel)
                    request = registry_pb2.Request()
                    request.type = registry_pb2.Request.RequestType.JOIN_SERVER
                    request.uuid = uuid
                    response = stub.JoinServer(request)
                    print("SUCCESS" if response.success else "FAIL")
        elif choice == 3:
            if len(servers) == 0:
                print("No servers available")
            else:
                print("Available servers: ")
                for i in range(len(servers)):
                    print(f"{i+1}. {servers[i].name}({servers[i].address})")
                server_choice = int(input("Enter server number: "))
                with grpc.insecure_channel(f"{servers[server_choice-1].address}") as channel:
                    stub = registry_pb2_grpc.ServerStub(channel)
                    request = registry_pb2.Request()
                    request.type = registry_pb2.Request.RequestType.LEAVE_SERVER
                    request.uuid = uuid
                    response = stub.LeaveServer(request)
                    print("SUCCESS" if response.success else "FAIL")
        elif choice == 4:
            if len(servers) == 0:
                print("No servers available")
            else:
                print("Available servers: ")
                for i in range(len(servers)):
                    print(f"{i+1}. {servers[i].name}({servers[i].address})")
                server_choice = int(input("Enter server number: "))
                with grpc.insecure_channel(f"{servers[server_choice-1].address}", options=(('grpc.enable_http_proxy', 0),)) as channel:
                    stub = registry_pb2_grpc.ServerStub(channel)
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
                    request.uuid = uuid
                    request.type = registry_pb2.Request.RequestType.GET_ARTICLES
                    request.getArticlesRequest.articleRequest.type = article_type
                    request.getArticlesRequest.articleRequest.author = author
                    request.getArticlesRequest.articleRequest.date = date
                    response = stub.GetArticles(request)
                    assert response.type == registry_pb2.Response.ResponseType.GET_ARTICLES
                    if response.success:
                        print("Get articles request: SUCCESS")
                        print("Articles:")
                        for article in response.getArticlesResponse.articles:
                            print(str(article))
                    else:
                        print("Get articles request: FAIL")
        elif choice == 5:
            if len(servers) == 0:
                print("No servers available")
            else:
                print("Available servers: ")
                for i in range(len(servers)):
                    print(f"{i+1}. {servers[i].name}({servers[i].address})")
                server_choice = int(input("Enter server number: "))
                with grpc.insecure_channel(f"{servers[server_choice-1].address}") as channel:
                    stub = registry_pb2_grpc.ServerStub(channel)
                    request = registry_pb2.Request()
                    request.type = registry_pb2.Request.RequestType.PUBLISH_ARTICLE
                    request.uuid = uuid
                    # request.publishArticleRequest.article = registry_pb2.Article()
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
                    request.publishArticleRequest.article.articleRequest.type = article_type
                    request.publishArticleRequest.article.articleRequest.author = author
                    request.publishArticleRequest.article.content = content
                    request.publishArticleRequest.article.articleRequest.date = datetime.datetime.now().strftime("%d/%m/%Y")
                    response = stub.PublishArticle(request)
                    assert response.type == registry_pb2.Response.ResponseType.PUBLISH_ARTICLE
                    if response.success:
                        print("Publish article request: SUCCESS")
                    else:
                        print("Publish article request: FAIL")

        elif choice == 6:
            break


if __name__ == "__main__":
    client(servers)