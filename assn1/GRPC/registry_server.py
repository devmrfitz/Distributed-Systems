# write a registry server that can register and unregister servers with the registry server
# and write a client that can send a request to the server and receive a response from the server
# Path: registry_server.py

import concurrent.futures
import grpc
import registry_pb2
import registry_pb2_grpc
import sys
import time
import threading
from constants import REGISTRY_SERVER_PORT


MAX_SERVERS = 10
class RegistryServer(registry_pb2_grpc.RegistryServerServicer):
    def __init__(self):
        self.server_list = dict()

    def Register(self, request, context):
        print("Register request received")
        print(str(request))
        response = registry_pb2.Response()
        # response.type = registry_pb2.Response.descriptor.fields_by_name['type'].enum_type.values_by_name['REGISTER'].number
        response.type = registry_pb2.Response.ResponseType.REGISTER
        # if request.type == registry_pb2.Request.descriptor.fields_by_name['type'].enum_type.values_by_name['REGISTER'].number:
        if request.type == registry_pb2.Request.RequestType.REGISTER:
            if request.registerRequest.name in self.server_list:
                response.success = True
            else:
                if len(self.server_list) < MAX_SERVERS:
                    self.server_list[request.registerRequest.name] = registry_pb2.Response.GetServerListResponse.Server()
                    self.server_list[request.registerRequest.name].name = request.registerRequest.name
                    self.server_list[request.registerRequest.name].address = request.registerRequest.address
                    response.success = True
                else:
                    response.success = False
        else:
            response.success = False
        print("JOIN REQUEST FROM ", request.registerRequest.address)
        # print("Register response sent: ", response)
        return response

    def FetchServerList(self, request, context):
        print("List request received")
        print("Request from client: ", str(request))
        response = registry_pb2.Response()
        response.type = registry_pb2.Response.ResponseType.FETCH_SERVER_LIST
        if request.type == registry_pb2.Request.RequestType.FETCH_SERVER_LIST:
            response.success = True
            for server in self.server_list:
                response.getServerListResponse.servers.append(self.server_list[server])
        else:
            response.success = False
        return response


def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    registry_pb2_grpc.add_RegistryServerServicer_to_server(RegistryServer(), server)
    server.add_insecure_port('localhost:' + str(REGISTRY_SERVER_PORT))
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
