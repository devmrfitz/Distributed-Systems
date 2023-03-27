from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DummyRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class FetchServerListResponse(_message.Message):
    __slots__ = ["serverList", "success"]
    SERVERLIST_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    serverList: _containers.RepeatedScalarFieldContainer[str]
    success: bool
    def __init__(self, serverList: _Optional[_Iterable[str]] = ..., success: bool = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ["ip", "port"]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: int
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class RegisterResponse(_message.Message):
    __slots__ = ["primaryIp", "primaryPort", "success"]
    PRIMARYIP_FIELD_NUMBER: _ClassVar[int]
    PRIMARYPORT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    primaryIp: str
    primaryPort: int
    success: bool
    def __init__(self, success: bool = ..., primaryIp: _Optional[str] = ..., primaryPort: _Optional[int] = ...) -> None: ...
