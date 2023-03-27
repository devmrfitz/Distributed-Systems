
from datetime import datetime
from random import randint
from signal import SIGKILL, pthread_kill
import zmq

from constants import REGISTRY_SERVER_PORT
import registry_pb2
import threading

context = zmq.Context()


SERVER_PORT = str(randint(10000, 60000))


SERVER_NAME = input("Enter server name: ")

MAX_CLIENTS = 10
clientele = set()
articles = []

pending_requests = set()
followed_servers = set()


def send_register_request():
    registry_socket = context.socket(zmq.REQ)
    registry_socket.connect(f"tcp://localhost:{REGISTRY_SERVER_PORT}")

    register_request = registry_pb2.Request()
    register_request.type = registry_pb2.Request.RequestType.REGISTER
    register_request.registerRequest.name = SERVER_NAME
    register_request.registerRequest.address = f"tcp://localhost:{SERVER_PORT}"

    registry_socket.send(register_request.SerializeToString())

    #  Get the reply
    message = registry_socket.recv()
    response = registry_pb2.Response()
    response.ParseFromString(message)

    assert response.type == registry_pb2.Response.ResponseType.REGISTER

    if response.success:
        print("Registration request: SUCCESS")
    else:
        print("Registration request: FAIL")

    registry_socket.close()


def handle_join_server(request):
    assert request.type == registry_pb2.Request.RequestType.JOIN_SERVER
    print("Join server request received")
    print(str(request))
    response = registry_pb2.Response()
    response.type = registry_pb2.Response.ResponseType.JOIN_SERVER
    if len(clientele) >= MAX_CLIENTS:
        response.success = False
    else:
        clientele.add(request.uuid)
        response.success = True

    return response.SerializeToString()


def handle_leave_server(request):
    assert request.type == registry_pb2.Request.RequestType.LEAVE_SERVER
    print("Leave server request received")
    print(str(request))
    response = registry_pb2.Response()
    response.type = registry_pb2.Response.ResponseType.LEAVE_SERVER
    if request.uuid not in clientele:
        response.success = False
    else:
        clientele.remove(request.uuid)
        response.success = True

    return response.SerializeToString()


def handle_publish_article(request):
    assert request.type == registry_pb2.Request.RequestType.PUBLISH_ARTICLE
    print("Publish article request received")
    print(str(request))
    response = registry_pb2.Response()
    response.type = registry_pb2.Response.ResponseType.PUBLISH_ARTICLE
    if request.uuid not in clientele:
        response.success = False
    else:
        article = request.publishArticleRequest.article
        article.articleRequest.date = datetime.now().strftime("%d/%m/%Y")
        articles.append(article)
        response.success = True

    return response.SerializeToString()


def handle_get_articles(request):
    if request.nonce in pending_requests:
        response = registry_pb2.Response()
        response.type = registry_pb2.Response.ResponseType.GET_ARTICLES
        response.success = True
        return response.SerializeToString()
    pending_requests.add(request.nonce)

    def date_parser(date):
        return datetime.strptime(date, "%d/%m/%Y")
    assert request.type == registry_pb2.Request.RequestType.GET_ARTICLES
    print("Get articles request received")
    print(str(request))
    response = registry_pb2.Response()
    response.type = registry_pb2.Response.ResponseType.GET_ARTICLES
    if request.uuid not in clientele and not request.getArticlesRequest.isSibling:
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
                            response.getArticlesResponse.articles.append(
                                article)
            for server in followed_servers:
                socket = context.socket(zmq.REQ)
                socket.connect(server)
                request.getArticlesRequest.isSibling = True
                socket.send(request.SerializeToString())
                message = socket.recv()
                response_recvd = registry_pb2.Response()
                response_recvd.ParseFromString(message)

                assert response_recvd.type == registry_pb2.Response.ResponseType.GET_ARTICLES

                response.getArticlesResponse.articles.extend(
                    response_recvd.getArticlesResponse.articles)

    pending_requests.remove(request.nonce)
    return response.SerializeToString()


request_handlers = {
    registry_pb2.Request.RequestType.JOIN_SERVER: handle_join_server,
    registry_pb2.Request.RequestType.LEAVE_SERVER: handle_leave_server,
    registry_pb2.Request.RequestType.PUBLISH_ARTICLE: handle_publish_article,
    registry_pb2.Request.RequestType.GET_ARTICLES: handle_get_articles,
}


def follow_server():
    def fetch_server_list():
        servers = []
        registry_socket = context.socket(zmq.REQ)
        registry_socket.connect(f"tcp://localhost:{REGISTRY_SERVER_PORT}")

        request = registry_pb2.Request()
        request.type = registry_pb2.Request.RequestType.FETCH_SERVER_LIST

        registry_socket.send(request.SerializeToString())

        #  Get the reply
        message = registry_socket.recv()
        response = registry_pb2.Response()
        response.ParseFromString(message)

        assert response.type == registry_pb2.Response.ResponseType.FETCH_SERVER_LIST

        if response.success:
            print("Fetch server list request: SUCCESS")
            print("Server list:")
            for server in response.serverListResponse.servers:
                if server.address == f"tcp://localhost:{SERVER_PORT}":
                    continue
                print(server.name, server.address)
                servers.append(server)
        else:
            print("Fetch server list request: FAIL")

        registry_socket.close()
        return servers

    servers = fetch_server_list()
    print("Available servers:")
    for i, server in enumerate(servers):
        print(f"{i+1}. {server.name}({server.address})")
    choice = int(input("Enter your choice: "))
    server = servers[choice-1]
    followed_servers.add(server.address)
    print(f"Following {server.name}({server.address})")


def request_coordinator(message, address, primary_socket):
    request = registry_pb2.Request()
    request.ParseFromString(message)
    if request.type in request_handlers:
        response = request_handlers[request.type](request)
    else:
        raise Exception("Unknown request type")
    primary_socket.send_multipart([address, b'', response])


def run_primary_server(primary_socket):
    print("Running primary server")
    while True:
        #  Wait for next request from client
        address, _, message = primary_socket.recv_multipart()

        threading.Thread(target=request_coordinator, args=(
            message, address, primary_socket)).start()


primary_socket = context.socket(zmq.ROUTER)
primary_socket.bind(f"tcp://*:{SERVER_PORT}")

send_register_request()


primary_server = None


def trigger_primary_server(primary_server):
    if primary_server is not None and primary_server.ident is not None and primary_server.is_alive():
        print("Killing old primary server")
        pthread_kill(primary_server.ident, SIGKILL)
    primary_server = threading.Thread(
        target=run_primary_server, args=(primary_socket,))
    primary_server.start()
    return primary_server


primary_server = trigger_primary_server(primary_server)

while True:
    help_text = """
    1. Send Register request
    2. Run Primary server
    3. Follow another server
    4. Exit
    """
    print(help_text)
    choice = input("Enter your choice: ")
    if choice == "1":
        send_register_request()
    elif choice == "2":
        primary_server = trigger_primary_server(primary_server)
    elif choice == "3":
        follow_server()
    elif choice == "4":
        if primary_server is not None and primary_server.ident is not None:
            pthread_kill(primary_server.ident, SIGKILL)
        break
