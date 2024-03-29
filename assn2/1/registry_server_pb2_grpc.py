# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import registry_server_pb2 as registry__server__pb2


class RegistryServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/grpc.RegistryServer/Register',
                request_serializer=registry__server__pb2.RegisterRequest.SerializeToString,
                response_deserializer=registry__server__pb2.RegisterResponse.FromString,
                )
        self.FetchServerList = channel.unary_unary(
                '/grpc.RegistryServer/FetchServerList',
                request_serializer=registry__server__pb2.DummyRequest.SerializeToString,
                response_deserializer=registry__server__pb2.FetchServerListResponse.FromString,
                )


class RegistryServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FetchServerList(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RegistryServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=registry__server__pb2.RegisterRequest.FromString,
                    response_serializer=registry__server__pb2.RegisterResponse.SerializeToString,
            ),
            'FetchServerList': grpc.unary_unary_rpc_method_handler(
                    servicer.FetchServerList,
                    request_deserializer=registry__server__pb2.DummyRequest.FromString,
                    response_serializer=registry__server__pb2.FetchServerListResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grpc.RegistryServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RegistryServer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.RegistryServer/Register',
            registry__server__pb2.RegisterRequest.SerializeToString,
            registry__server__pb2.RegisterResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def FetchServerList(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.RegistryServer/FetchServerList',
            registry__server__pb2.DummyRequest.SerializeToString,
            registry__server__pb2.FetchServerListResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
