from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Subscription(_message.Message):
    __slots__ = ("telegram_user_id", "country_slug", "active", "web_user_id")
    TELEGRAM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_SLUG_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    WEB_USER_ID_FIELD_NUMBER: _ClassVar[int]
    telegram_user_id: str
    country_slug: str
    active: bool
    web_user_id: str
    def __init__(self, telegram_user_id: _Optional[str] = ..., country_slug: _Optional[str] = ..., active: _Optional[bool] = ..., web_user_id: _Optional[str] = ...) -> None: ...

class DeliveryStatus(_message.Message):
    __slots__ = ("event_key", "telegram_user_id", "country_slug", "status", "sent_at", "error")
    EVENT_KEY_FIELD_NUMBER: _ClassVar[int]
    TELEGRAM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_SLUG_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SENT_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    event_key: str
    telegram_user_id: str
    country_slug: str
    status: str
    sent_at: str
    error: str
    def __init__(self, event_key: _Optional[str] = ..., telegram_user_id: _Optional[str] = ..., country_slug: _Optional[str] = ..., status: _Optional[str] = ..., sent_at: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class CreateSubscriptionRequest(_message.Message):
    __slots__ = ("telegram_user_id", "username", "country_slug")
    TELEGRAM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_SLUG_FIELD_NUMBER: _ClassVar[int]
    telegram_user_id: str
    username: str
    country_slug: str
    def __init__(self, telegram_user_id: _Optional[str] = ..., username: _Optional[str] = ..., country_slug: _Optional[str] = ...) -> None: ...

class DeleteSubscriptionRequest(_message.Message):
    __slots__ = ("telegram_user_id", "country_slug")
    TELEGRAM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_SLUG_FIELD_NUMBER: _ClassVar[int]
    telegram_user_id: str
    country_slug: str
    def __init__(self, telegram_user_id: _Optional[str] = ..., country_slug: _Optional[str] = ...) -> None: ...

class ListSubscriptionsRequest(_message.Message):
    __slots__ = ("telegram_user_id",)
    TELEGRAM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    telegram_user_id: str
    def __init__(self, telegram_user_id: _Optional[str] = ...) -> None: ...

class GetDeliveryStatusRequest(_message.Message):
    __slots__ = ("telegram_user_id", "event_key", "country_slug", "limit")
    TELEGRAM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_KEY_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_SLUG_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    telegram_user_id: str
    event_key: str
    country_slug: str
    limit: int
    def __init__(self, telegram_user_id: _Optional[str] = ..., event_key: _Optional[str] = ..., country_slug: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class SubscriptionResponse(_message.Message):
    __slots__ = ("subscription", "error")
    SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    subscription: Subscription
    error: str
    def __init__(self, subscription: _Optional[_Union[Subscription, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class ListSubscriptionsResponse(_message.Message):
    __slots__ = ("subscriptions",)
    SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    subscriptions: _containers.RepeatedCompositeFieldContainer[Subscription]
    def __init__(self, subscriptions: _Optional[_Iterable[_Union[Subscription, _Mapping]]] = ...) -> None: ...

class GetDeliveryStatusResponse(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[DeliveryStatus]
    def __init__(self, entries: _Optional[_Iterable[_Union[DeliveryStatus, _Mapping]]] = ...) -> None: ...

class ConsumeTelegramWebLinkCodeRequest(_message.Message):
    __slots__ = ("code", "web_user_id")
    CODE_FIELD_NUMBER: _ClassVar[int]
    WEB_USER_ID_FIELD_NUMBER: _ClassVar[int]
    code: str
    web_user_id: str
    def __init__(self, code: _Optional[str] = ..., web_user_id: _Optional[str] = ...) -> None: ...

class ConsumeTelegramWebLinkCodeResponse(_message.Message):
    __slots__ = ("ok", "telegram_user_id", "error")
    OK_FIELD_NUMBER: _ClassVar[int]
    TELEGRAM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    telegram_user_id: str
    error: str
    def __init__(self, ok: _Optional[bool] = ..., telegram_user_id: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class GetTelegramIdentityLinkStatusRequest(_message.Message):
    __slots__ = ("telegram_user_id",)
    TELEGRAM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    telegram_user_id: str
    def __init__(self, telegram_user_id: _Optional[str] = ...) -> None: ...

class GetTelegramIdentityLinkStatusResponse(_message.Message):
    __slots__ = ("linked", "web_user_id")
    LINKED_FIELD_NUMBER: _ClassVar[int]
    WEB_USER_ID_FIELD_NUMBER: _ClassVar[int]
    linked: bool
    web_user_id: str
    def __init__(self, linked: _Optional[bool] = ..., web_user_id: _Optional[str] = ...) -> None: ...

class UnlinkTelegramWebUserRequest(_message.Message):
    __slots__ = ("telegram_user_id",)
    TELEGRAM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    telegram_user_id: str
    def __init__(self, telegram_user_id: _Optional[str] = ...) -> None: ...

class UnlinkTelegramWebUserResponse(_message.Message):
    __slots__ = ("ok",)
    OK_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    def __init__(self, ok: _Optional[bool] = ...) -> None: ...
