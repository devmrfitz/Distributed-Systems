
import threading
import zmq

from constants import REGISTRY_SERVER_PORT
import registry_pb2

MAX_SERVERS = 10

servers = dict()

context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind(f"tcp://*:{REGISTRY_SERVER_PORT}")


def handle_register_request(request):
    assert request.type == registry_pb2.Request.RequestType.REGISTER
    print("Register request received")
    print(str(request))
    response = registry_pb2.Response()
    response.type = registry_pb2.Response.ResponseType.REGISTER
    if len(servers) >= MAX_SERVERS:
        response.success = False
    else:
        servers[request.registerRequest.name] = registry_pb2.Response.ServerListResponse.Server()
        servers[request.registerRequest.name].name = request.registerRequest.name
        servers[request.registerRequest.name].address = request.registerRequest.address
        response.success = True

    return response.SerializeToString()


def handle_get_server_list_request(request):
    assert request.type == registry_pb2.Request.RequestType.FETCH_SERVER_LIST
    print("Get server list request received")
    print(str(request))
    response = registry_pb2.Response()
    response.type = registry_pb2.Response.ResponseType.FETCH_SERVER_LIST
    response.serverListResponse.servers.extend(servers.values())
    response.success = True
    return response.SerializeToString()


request_handlers = {
    registry_pb2.Request.RequestType.REGISTER: handle_register_request,
    registry_pb2.Request.RequestType.FETCH_SERVER_LIST: handle_get_server_list_request,
}


def request_coordinator(message, address, primary_socket):
    request = registry_pb2.Request()
    request.ParseFromString(message)
    if request.type in request_handlers:
        response = request_handlers[request.type](request)
    else:
        raise Exception("Unknown request type")
    primary_socket.send_multipart([address, b'', response])


while True:
    #  Wait for next request from client
    address, _, message = socket.recv_multipart()

    threading.Thread(target=request_coordinator, args=(
        message, address, socket)).start()
