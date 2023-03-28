
import grpc

import uuid as uuid

import registry_server_pb2
import registry_server_pb2_grpc
from constants import REGISTRY_SERVER_PORT
import server_pb2
import server_pb2_grpc

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


def proxy_print(*args, **kwargs):
    if pipe_conn is None:
        return og_print(*args, **kwargs)
    else:
        return pipe_conn.send(" ".join(map(str, args)))


input = proxy_input
print = proxy_print


class Client:
    def __init__(self) -> None:
        super().__init__()
        self.servers = []

    def run(self):
        while True:
            help_text = """
                1. Fetch server list from registry server
                2. Read file
                3. Create/Update file
                4. Delete file
                5. Exit
                """
            print(help_text)
            choice = int(input("Enter your choice: "))
            if choice == 1:
                with grpc.insecure_channel(f"localhost:{REGISTRY_SERVER_PORT}") as channel:
                    stub = registry_server_pb2_grpc.RegistryServerStub(channel)
                    request = registry_server_pb2.DummyRequest()
                    response = stub.FetchServerList(request)
                    self.servers = list(response.serverList)
                    print(self.servers)

            # elif choice == 2:
            #     if len(self.servers) == 0:
            #         print("No servers available")
            #     else:
            #         print("Available servers: ")
            #         for index, server in enumerate(self.servers):
            #             print(
            #                 f"{index+1}. {server}")
            #         server_choice = int(input("Enter server number: "))
            #         filename = input("Enter filename: ")
            #         content = input("Enter content: ")
            #         request = server_pb2.WriteRequest(
            #             name=filename, content=content,
            #             uuid=str(uuid.uuid4()))
            #         with grpc.insecure_channel(f"{self.servers[server_choice-1]}", options=(('grpc.enable_http_proxy', 0),)) as channel:
            #             stub = server_pb2_grpc.ServerStub(channel)
            #             response = stub.Write(request)
            #             print("SUCCESS" if response.success else "FAIL")
            #             print(f"[DEBUG] {response}")
            elif choice == 2:
                # READ
                if len(self.servers) == 0:
                    print("No servers available")
                else:
                    print("Available servers: ")
                    for index, server in enumerate(self.servers):
                        print(
                            f"{index+1}. {server}")
                    server_choice = int(input("Enter server number: "))
                    file_uuid = input("Enter UUID of file to be read: ")
                    request = server_pb2.ReadRequest(
                        uuid=file_uuid)
                    with grpc.insecure_channel(f"{self.servers[server_choice-1]}", options=(('grpc.enable_http_proxy', 0),)) as channel:
                        stub = server_pb2_grpc.ServerStub(channel)
                        response = stub.Read(request)
                        print("SUCCESS" if response.success else "FAIL")
                        print(f"[DEBUG] {response}")
            elif choice == 3:
                # UPDATE or CREATE
                if len(self.servers) == 0:
                    print("No servers available")
                else:
                    print("Available servers: ")
                    for index, server in enumerate(self.servers):
                        print(
                            f"{index+1}. {server}")
                    server_choice = int(input("Enter server number: "))
                    file_uuid = input(
                        "Enter UUID of file to be updated or leave blank for new file creation: ")
                    if not file_uuid:
                        file_uuid = str(uuid.uuid4())
                    filename = input(
                        "Enter filename (should be same as previous for updation): ")
                    content = input("Enter content: ")
                    request = server_pb2.WriteRequest(
                        name=filename, content=content,
                        uuid=file_uuid)
                    with grpc.insecure_channel(f"{self.servers[server_choice-1]}", options=(('grpc.enable_http_proxy', 0),)) as channel:
                        stub = server_pb2_grpc.ServerStub(channel)
                        response = stub.Write(request)
                        print("SUCCESS" if response.success else "FAIL")
                        print(f"[DEBUG] {response}")
            elif choice == 4:
                # DELETE
                if len(self.servers) == 0:
                    print("No servers available")
                else:
                    print("Available servers: ")
                    for index, server in enumerate(self.servers):
                        print(
                            f"{index+1}. {server}")
                    server_choice = int(input("Enter server number: "))
                    file_uuid = input("Enter UUID of file to be deleted: ")
                    request = server_pb2.DeleteRequest(
                        uuid=file_uuid)
                    with grpc.insecure_channel(f"{self.servers[server_choice-1]}", options=(('grpc.enable_http_proxy', 0),)) as channel:
                        stub = server_pb2_grpc.ServerStub(channel)
                        response = stub.Delete(request)
                        print("SUCCESS" if response.success else "FAIL")
                        print(f"[DEBUG] {response}")
            elif choice == 5:
                break


def run(_pipe_conn=None):
    global pipe_conn

    pipe_conn = _pipe_conn
    client = Client()
    client.run()


if __name__ == "__main__":
    run()
