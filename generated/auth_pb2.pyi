from typing import ClassVar as _ClassVar
from typing import Optional as _Optional

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class PermissionRequest(_message.Message):
    __slots__ = ("session_token", "service", "entity", "action")
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    session_token: str
    service: str
    entity: str
    action: str
    def __init__(
        self,
        session_token: _Optional[str] = ...,
        service: _Optional[str] = ...,
        entity: _Optional[str] = ...,
        action: _Optional[str] = ...,
    ) -> None: ...

class PermissionResponse(_message.Message):
    __slots__ = ("is_access", "message", "code")
    IS_ACCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    is_access: bool
    message: str
    code: int
    def __init__(
        self, is_access: bool = ..., message: _Optional[str] = ..., code: _Optional[int] = ...
    ) -> None: ...
