from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PermissionRequest(_message.Message):
    __slots__ = ("session_token", "service", "entity", "action", "user_id")
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    session_token: str
    service: str
    entity: str
    action: str
    user_id: str
    def __init__(self, session_token: _Optional[str] = ..., service: _Optional[str] = ..., entity: _Optional[str] = ..., action: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class PermissionResponse(_message.Message):
    __slots__ = ("is_access", "message", "user_id", "code")
    IS_ACCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    is_access: bool
    message: str
    user_id: str
    code: int
    def __init__(self, is_access: bool = ..., message: _Optional[str] = ..., user_id: _Optional[str] = ..., code: _Optional[int] = ...) -> None: ...

class GetUsersRequest(_message.Message):
    __slots__ = ("permission_request", "only_active")
    PERMISSION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ONLY_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    permission_request: PermissionRequest
    only_active: bool
    def __init__(self, permission_request: _Optional[_Union[PermissionRequest, _Mapping]] = ..., only_active: bool = ...) -> None: ...

class UserResponse(_message.Message):
    __slots__ = ("id", "name", "surname")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SURNAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    surname: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., surname: _Optional[str] = ...) -> None: ...

class GetUsersResponse(_message.Message):
    __slots__ = ("users", "message", "code")
    USERS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[UserResponse]
    message: str
    code: int
    def __init__(self, users: _Optional[_Iterable[_Union[UserResponse, _Mapping]]] = ..., message: _Optional[str] = ..., code: _Optional[int] = ...) -> None: ...
