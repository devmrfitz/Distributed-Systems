from multiprocessing import Pipe, Process
import time
from server import run as run_server
from client import run as run_client
from registry_server import run as run_registry_server

N = 2


class Server:
    def __init__(self) -> None:
        self.p = Process(target=run_server)
        self.p.start()

    def __del__(self):
        self.p.terminate()


class RegistryServer:
    def __init__(self) -> None:
        self.p = Process(target=run_registry_server)
        self.p.start()

    def __del__(self):
        self.p.terminate()


class Client:
    def __init__(self) -> None:
        self.parent_conn, child_conn = Pipe()
        self.p = Process(target=run_client, args=(child_conn,))
        self.p.start()

    def send(self, msg: str):
        self.parent_conn.send(str(msg))

    def recv(self) -> str:
        time.sleep(0.1)
        res = ""
        while self.parent_conn.poll():
            data: str = self.parent_conn.recv().strip()
            if data.startswith("1. Fetch server list from registry server")\
                    or data.startswith("Enter your choice:"):
                continue
            res += data + "\n"
        return res

    def __del__(self):
        self.p.terminate()

    def fetch_server_list(self):
        self.send("1")
        raw = self.recv()
        print(raw)
        return {"raw": raw}

    def write_file(self, filename: str, content: str, server: str):
        self.send("3")
        self.send(server)
        self.send("")
        self.send(filename)
        self.send(content)
        raw = self.recv()
        print(raw)
        return {
            "raw": raw,
            "uuid": raw.split("uuid: \"")[1].split("\"")[0]
        }

    def read_file(self, uuid: str, server: str):
        self.send("2")
        self.send(server)
        self.send(uuid)
        raw = self.recv()
        print(raw)
        return {
            "raw": raw,
            "content": raw.split("content: \"")[1].split("\"")[0] if "content: \"" in raw else None
        }

    def delete_file(self, uuid: str, server: str):
        self.send("4")
        self.send(server)
        self.send(uuid)
        raw = self.recv()
        print(raw)
        return {
            "raw": raw,
        }


def run():
    registry_server = RegistryServer()
    servers = [Server() for _ in range(N)]
    time.sleep(1*N)
    c1 = Client()
    c1.fetch_server_list()
    uuid1 = c1.write_file("test.txt", "hello world", "1")['uuid']
    for i in range(N):
        print(f"Reading from server {i+1}")
        c1.read_file(uuid1, str(i+1))
    uuid2 = c1.write_file("test2.txt", "hello world2", "1")['uuid']
    for i in range(N):
        print(f"Reading from server {i+1}")
        c1.read_file(uuid2, str(i+1))
    c1.delete_file(uuid1, "1")
    for i in range(N):
        print(f"Reading from server {i+1}")
        c1.read_file(uuid1, str(i+1))


if __name__ == "__main__":
    run()
