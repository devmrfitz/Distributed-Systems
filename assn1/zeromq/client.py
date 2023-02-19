
import zmq

from constants import REGISTRY_SERVER_PORT
import registry_pb2
import uuid
context = zmq.Context()


servers = []

client_uuid = str(uuid.uuid4())
print(f"UUID: {client_uuid}")


def fetch_server_list():
    registry_socket = context.socket(zmq.REQ)
    registry_socket.connect(f"tcp://localhost:{REGISTRY_SERVER_PORT}")

    request = registry_pb2.Request()
    request.uuid = client_uuid
    request.type = registry_pb2.Request.RequestType.FETCH_SERVER_LIST

    registry_socket.send(request.SerializeToString())

    #  Get the reply
    message = registry_socket.recv()
    response = registry_pb2.Response()
    response.ParseFromString(message)

    assert response.type == registry_pb2.Response.ResponseType.FETCH_SERVER_LIST

    if response.success:
        global servers
        print("Fetch server list request: SUCCESS")
        print("Server list:")
        servers = []
        for server in response.serverListResponse.servers:
            print(server.name, server.address)
            servers.append(server)
        print(servers)
    else:
        print("Fetch server list request: FAIL")

    registry_socket.close()


def join_server():
    if len(servers) == 0:
        print("No servers available. Try fetching server list.")
        return
    print("Available servers:")
    for i, server in enumerate(servers):
        print(f"{i+1}. {server.name}({server.address})")
    choice = int(input("Enter your choice: "))
    server = servers[choice-1]
    socket = context.socket(zmq.REQ)
    socket.connect(server.address)

    request = registry_pb2.Request()
    request.uuid = client_uuid
    request.type = registry_pb2.Request.RequestType.JOIN_SERVER

    socket.send(request.SerializeToString())

    #  Get the reply
    message = socket.recv()
    response = registry_pb2.Response()
    response.ParseFromString(message)

    assert response.type == registry_pb2.Response.ResponseType.JOIN_SERVER

    if response.success:
        print("Join server request: SUCCESS")
    else:
        print("Join server request: FAIL")


def leave_server():
    if len(servers) == 0:
        print("No servers available. Try fetching server list.")
        return
    print("Available servers:")
    for i, server in enumerate(servers):
        print(f"{i+1}. {server.name}({server.address})")
    choice = int(input("Enter your choice: "))
    server = servers[choice-1]
    socket = context.socket(zmq.REQ)
    socket.connect(server.address)

    request = registry_pb2.Request()
    request.uuid = client_uuid
    request.type = registry_pb2.Request.RequestType.LEAVE_SERVER

    socket.send(request.SerializeToString())

    #  Get the reply
    message = socket.recv()
    response = registry_pb2.Response()
    response.ParseFromString(message)

    assert response.type == registry_pb2.Response.ResponseType.LEAVE_SERVER

    if response.success:
        print("Leave server request: SUCCESS")
    else:
        print("Leave server request: FAIL")


def get_articles():
    if len(servers) == 0:
        print("No servers available. Try fetching server list.")
        return
    print("Available servers:")
    for i, server in enumerate(servers):
        print(f"{i+1}. {server.name}({server.address})")
    choice = int(input("Enter your choice: "))
    server = servers[choice-1]
    socket = context.socket(zmq.REQ)
    socket.connect(server.address)

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
    request.uuid = client_uuid
    request.type = registry_pb2.Request.RequestType.GET_ARTICLES
    request.getArticlesRequest.articleRequest.type = article_type
    request.getArticlesRequest.articleRequest.author = author
    request.getArticlesRequest.articleRequest.date = date

    request.nonce = str(uuid.uuid4())

    socket.send(request.SerializeToString())

    #  Get the reply
    message = socket.recv()
    response = registry_pb2.Response()
    response.ParseFromString(message)

    assert response.type == registry_pb2.Response.ResponseType.GET_ARTICLES

    if response.success:
        print("Get articles request: SUCCESS")
        print("Articles:")
        for article in response.getArticlesResponse.articles:
            print(str(article))
    else:
        print("Get articles request: FAIL")


def publish_article():
    if len(servers) == 0:
        print("No servers available. Try fetching server list.")
        return
    print("Available servers:")
    for i, server in enumerate(servers):
        print(f"{i+1}. {server.name}({server.address})")
    choice = int(input("Enter your choice: "))
    server = servers[choice-1]
    socket = context.socket(zmq.REQ)
    socket.connect(server.address)

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
    request.uuid = client_uuid
    request.type = registry_pb2.Request.RequestType.PUBLISH_ARTICLE
    request.publishArticleRequest.article.articleRequest.type = article_type
    request.publishArticleRequest.article.content = content
    request.publishArticleRequest.article.articleRequest.author = author

    socket.send(request.SerializeToString())

    #  Get the reply
    message = socket.recv()
    response = registry_pb2.Response()
    response.ParseFromString(message)

    assert response.type == registry_pb2.Response.ResponseType.PUBLISH_ARTICLE

    if response.success:
        print("Publish article request: SUCCESS")
    else:
        print("Publish article request: FAIL")


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
        fetch_server_list()
    elif choice == 2:
        join_server()
    elif choice == 3:
        leave_server()
    elif choice == 4:
        get_articles()
    elif choice == 5:
        publish_article()
    elif choice == 6:
        break
