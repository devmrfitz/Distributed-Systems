# write a registry server that can register and unregister servers with the registry server
# and write a client that can send a request to the server and receive a response from the server
# Path: registry_server.py

import concurrent.futures
import grpc
import registry_server_pb2
import server_pb2
import registry_server_pb2_grpc
import server_pb2_grpc
import time
from constants import REGISTRY_SERVER_PORT


class RegistryServer(registry_server_pb2_grpc.RegistryServerServicer):
    def __init__(self):
        self.server_list = set()
        self.primary = None

    def Register(self, request, context):
        print("Register request received")
        print(str(request))
        response = registry_server_pb2.RegisterResponse()
        name = request.ip + ":" + str(request.port)
        self.server_list.add(name)
        if self.primary is None:
            self.primary = name
        else:
            with grpc.insecure_channel(self.primary, options=(('grpc.enable_http_proxy', 0),)) as channel:
                server_stub = server_pb2_grpc.ServerStub(
                    channel)
                server_stub.AddReplicaServer(
                    server_pb2.AddReplicaServerRequest(ip=request.ip, port=request.port))
        response.primaryIp = self.primary.split(":")[0]
        response.primaryPort = int(self.primary.split(":")[1])
        print("JOIN REQUEST FROM ", name)
        response.success = True
        return response

    def FetchServerList(self, request, context):
        print("List request received")
        response = registry_server_pb2.FetchServerListResponse()
        response.success = True
        for server in self.server_list:
            response.serverList.append(
                server)
        return response


def run():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    registry_server_pb2_grpc.add_RegistryServerServicer_to_server(
        RegistryServer(), server)
    server.add_insecure_port('localhost:' + str(REGISTRY_SERVER_PORT))
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    run()
