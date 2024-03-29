from concurrent import futures
import os
import uuid
from constants import REGISTRY_SERVER_PORT
import grpc
import time
import sys
import threading
import registry_server_pb2
import registry_server_pb2_grpc
import server_pb2
import server_pb2_grpc
from random import randint

SERVER_PORT = str(randint(10000, 60000))
SERVER_UUID = str(uuid.uuid4())

pipe_conn = None

og_input = input
og_print = print


def proxy_input(msg=""):
    if pipe_conn is None:
        return og_input(msg)
    else:
        if msg:
            print(msg, end="")
        result = pipe_conn.recv()
        return result


def proxy_print(*args):
    if pipe_conn is None:
        return og_print(*args)
    else:
        return pipe_conn.send(" ".join(map(str, args)))


input = proxy_input
print = proxy_print


class Server(server_pb2_grpc.ServerServicer):

    def __init__(self) -> None:
        super().__init__()
        self.my_data_store = {}
        self.primary_server = None
        self.replica_servers = set()

    def set_primary_server(self, primary_server):
        self.primary_server = primary_server

    def add_replica_server(self, replica_server):
        self.replica_servers.add(replica_server)

    def Write(self, request, context):
        print("[INFO] Write called")
        uuid = request.uuid
        name = request.name
        response = server_pb2.WriteResponse()
        if uuid in self.my_data_store and self.my_data_store[uuid][0] != name:
            response.success = False
            response.status = "FILE NAME CANNOT BE CHANGED"
        elif uuid in self.my_data_store and not os.path.isfile(f"serverData/{SERVER_UUID}/{name}"):
            response.success = False
            response.status = "DELETED FILE CANNOT BE UPDATED"
        elif uuid not in self.my_data_store and os.path.isfile(f"serverData/{SERVER_UUID}/{request.name}"):
            response.success = False
            response.status = "FILE WITH THE SAME NAME ALREADY EXISTS"
        else:
            with grpc.insecure_channel(self.primary_server, options=(('grpc.enable_http_proxy', 0),)) as channel:
                server_stub = server_pb2_grpc.ServerStub(
                    channel)
                response = server_stub.PrimaryWrite(request)
        return response

    def Read(self, request, context):
        print("[INFO] Read called")
        uuid = request.uuid
        response = server_pb2.ReadResponse()
        if uuid not in self.my_data_store:
            response.success = False
            response.status = "FILE DOES NOT EXIST"
        elif not os.path.isfile(f"serverData/{SERVER_UUID}/{self.my_data_store[uuid][0]}"):
            response.success = False
            response.status = "FILE ALREADY DELETED"
            response.version = self.my_data_store[uuid][1]
        else:
            response.success = True
            with open(f"serverData/{SERVER_UUID}/{self.my_data_store[uuid][0]}", "r") as f:
                response.content = f.read()
            response.version = self.my_data_store[uuid][1]
            response.name = self.my_data_store[uuid][0]
        return response

    def Delete(self, request, context):
        print("[INFO] Delete called")
        uuid = request.uuid
        response = server_pb2.SimpleResponse()
        if uuid not in self.my_data_store:
            response.success = False
            response.status = "FILE DOES NOT EXIST"
        elif not os.path.isfile(f"serverData/{SERVER_UUID}/{self.my_data_store[uuid][0]}"):
            response.success = False
            response.status = "FILE ALREADY DELETED"
        else:
            with grpc.insecure_channel(self.primary_server, options=(('grpc.enable_http_proxy', 0),)) as channel:
                server_stub = server_pb2_grpc.ServerStub(
                    channel)
                response = server_stub.PrimaryDelete(request)
        return response

    def ReplicateWrite(self, request, context):
        print("[INFO] ReplicaWrite called")
        self.my_data_store[request.uuid] = (request.name, request.version)
        with open(f"serverData/{SERVER_UUID}/{request.name}", "w") as f:
            f.write(request.content)
        return server_pb2.SimpleResponse(success=True)

    def PrimaryWrite(self, request, context):
        print("[INFO] PrimaryWrite called")
        print(f"[DEBUG] {self.replica_servers}")
        version = str(time.time())
        self.my_data_store[request.uuid] = (request.name, version)
        with open(f"serverData/{SERVER_UUID}/{request.name}", "w") as f:
            f.write(request.content)
        for replica_server in self.replica_servers:
            with grpc.insecure_channel(replica_server, options=(('grpc.enable_http_proxy', 0),)) as channel:
                server_stub = server_pb2_grpc.ServerStub(
                    channel)
                # TODO: Make this parallel
                server_stub.ReplicateWrite(server_pb2.ReplicateWriteRequest(
                    uuid=request.uuid, name=request.name, content=request.content, version=version))

        return server_pb2.WriteResponse(
            success=True, status="SUCCESS", version=version,
            uuid=request.uuid
        )

    def ReplicateDelete(self, request, context):
        print("[INFO] ReplicaDelete called")
        os.remove(
            f"serverData/{SERVER_UUID}/{self.my_data_store[request.uuid][0]}")
        self.my_data_store[request.uuid] = (
            "", request.version)
        return server_pb2.SimpleResponse(success=True, status="SUCCESS")

    def PrimaryDelete(self, request, context):
        print("[INFO] PrimaryDelete called")
        version = str(time.time())
        os.remove(
            f"serverData/{SERVER_UUID}/{self.my_data_store[request.uuid][0]}")
        self.my_data_store[request.uuid] = (
            "", version)
        for replica_server in self.replica_servers:
            with grpc.insecure_channel(replica_server, options=(('grpc.enable_http_proxy', 0),)) as channel:
                server_stub = server_pb2_grpc.ServerStub(
                    channel)
                server_stub.ReplicateDelete(server_pb2.ReplicateDeleteRequest(
                    uuid=request.uuid, version=version))
        return server_pb2.SimpleResponse(success=True, status="SUCCESS")

    def AddReplicaServer(self, request, context):
        print("[INFO] AddReplicaServer called")
        self.add_replica_server(f"{request.ip}:{request.port}")
        return server_pb2.SimpleResponse(success=True)


primary_server = None


def trigger_primary_server(primary_server, grpc_server):
    if primary_server is not None and primary_server.ident is not None and primary_server.is_alive():
        return
    primary_server = threading.Thread(
        target=grpc_server.start)
    primary_server.start()
    print("Primary server started")
    return primary_server


def send_register_request(server_obj):
    with grpc.insecure_channel(f"localhost:{REGISTRY_SERVER_PORT}", options=(('grpc.enable_http_proxy', 0),)) as channel:
        registry_stub = registry_server_pb2_grpc.RegistryServerStub(
            channel)
        response = registry_stub.Register(registry_server_pb2.RegisterRequest(
            ip="localhost",
            port=int(SERVER_PORT)))
        server_obj.set_primary_server(
            f"{response.primaryIp}:{response.primaryPort}")
    print(
        "Registration request: SUCCESS" if response.success else "Registration request: FAIL")


def run(_pipe_conn=None):
    global primary_server
    global pipe_conn

    pipe_conn = _pipe_conn
    os.mkdir(f"serverData/{SERVER_UUID}")
    server_obj = Server()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_pb2_grpc.add_ServerServicer_to_server(server_obj, server)
    server.add_insecure_port(f"localhost:{SERVER_PORT}")

    primary_server = trigger_primary_server(primary_server, server)
    send_register_request(server_obj)

    while True:
        time.sleep(100)


if __name__ == '__main__':
    run()
