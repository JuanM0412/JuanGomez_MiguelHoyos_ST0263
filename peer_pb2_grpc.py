# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import peer_pb2 as peer__pb2

GRPC_GENERATED_VERSION = '1.66.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in peer_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class PeerServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/peer.PeerService/Register',
                request_serializer=peer__pb2.RegisterRequest.SerializeToString,
                response_deserializer=peer__pb2.RegisterResponse.FromString,
                _registered_method=True)
        self.Unregister = channel.unary_unary(
                '/peer.PeerService/Unregister',
                request_serializer=peer__pb2.UnregisterRequest.SerializeToString,
                response_deserializer=peer__pb2.UnregisterResponse.FromString,
                _registered_method=True)
        self.GetInternalTable = channel.unary_unary(
                '/peer.PeerService/GetInternalTable',
                request_serializer=peer__pb2.InternalTableRequest.SerializeToString,
                response_deserializer=peer__pb2.InternalTableResponse.FromString,
                _registered_method=True)
        self.GetInterval = channel.unary_unary(
                '/peer.PeerService/GetInterval',
                request_serializer=peer__pb2.InternalTableRequest.SerializeToString,
                response_deserializer=peer__pb2.InternalTableResponse.FromString,
                _registered_method=True)
        self.ReceiveOwnFile = channel.unary_unary(
                '/peer.PeerService/ReceiveOwnFile',
                request_serializer=peer__pb2.File.SerializeToString,
                response_deserializer=peer__pb2.FileResponse.FromString,
                _registered_method=True)
        self.ReceiveExternalFile = channel.unary_unary(
                '/peer.PeerService/ReceiveExternalFile',
                request_serializer=peer__pb2.File.SerializeToString,
                response_deserializer=peer__pb2.FileResponse.FromString,
                _registered_method=True)
        self.SendFile = channel.unary_unary(
                '/peer.PeerService/SendFile',
                request_serializer=peer__pb2.File.SerializeToString,
                response_deserializer=peer__pb2.FileResponse.FromString,
                _registered_method=True)


class PeerServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Unregister(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetInternalTable(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetInterval(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReceiveOwnFile(self, request, context):
        """Servicios para manejar archivos
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReceiveExternalFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PeerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=peer__pb2.RegisterRequest.FromString,
                    response_serializer=peer__pb2.RegisterResponse.SerializeToString,
            ),
            'Unregister': grpc.unary_unary_rpc_method_handler(
                    servicer.Unregister,
                    request_deserializer=peer__pb2.UnregisterRequest.FromString,
                    response_serializer=peer__pb2.UnregisterResponse.SerializeToString,
            ),
            'GetInternalTable': grpc.unary_unary_rpc_method_handler(
                    servicer.GetInternalTable,
                    request_deserializer=peer__pb2.InternalTableRequest.FromString,
                    response_serializer=peer__pb2.InternalTableResponse.SerializeToString,
            ),
            'GetInterval': grpc.unary_unary_rpc_method_handler(
                    servicer.GetInterval,
                    request_deserializer=peer__pb2.InternalTableRequest.FromString,
                    response_serializer=peer__pb2.InternalTableResponse.SerializeToString,
            ),
            'ReceiveOwnFile': grpc.unary_unary_rpc_method_handler(
                    servicer.ReceiveOwnFile,
                    request_deserializer=peer__pb2.File.FromString,
                    response_serializer=peer__pb2.FileResponse.SerializeToString,
            ),
            'ReceiveExternalFile': grpc.unary_unary_rpc_method_handler(
                    servicer.ReceiveExternalFile,
                    request_deserializer=peer__pb2.File.FromString,
                    response_serializer=peer__pb2.FileResponse.SerializeToString,
            ),
            'SendFile': grpc.unary_unary_rpc_method_handler(
                    servicer.SendFile,
                    request_deserializer=peer__pb2.File.FromString,
                    response_serializer=peer__pb2.FileResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'peer.PeerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('peer.PeerService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class PeerService(object):
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
        return grpc.experimental.unary_unary(
            request,
            target,
            '/peer.PeerService/Register',
            peer__pb2.RegisterRequest.SerializeToString,
            peer__pb2.RegisterResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Unregister(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/peer.PeerService/Unregister',
            peer__pb2.UnregisterRequest.SerializeToString,
            peer__pb2.UnregisterResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetInternalTable(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/peer.PeerService/GetInternalTable',
            peer__pb2.InternalTableRequest.SerializeToString,
            peer__pb2.InternalTableResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetInterval(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/peer.PeerService/GetInterval',
            peer__pb2.InternalTableRequest.SerializeToString,
            peer__pb2.InternalTableResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReceiveOwnFile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/peer.PeerService/ReceiveOwnFile',
            peer__pb2.File.SerializeToString,
            peer__pb2.FileResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReceiveExternalFile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/peer.PeerService/ReceiveExternalFile',
            peer__pb2.File.SerializeToString,
            peer__pb2.FileResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SendFile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/peer.PeerService/SendFile',
            peer__pb2.File.SerializeToString,
            peer__pb2.FileResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
