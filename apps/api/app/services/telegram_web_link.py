from app.core.config import Settings, get_settings
from app.core.errors import api_error
from app.integrations.notifier_grpc.generated import (
    subscriptions_pb2,
    subscriptions_pb2_grpc,
)
from app.repositories import auth as repository
import grpc
from psycopg import Connection
from typing import Any, Protocol


class ConsumeLinkCodeResult:
    def __init__(self, ok: bool, telegram_user_id: str, error: str) -> None:
        self.ok = ok
        self.telegram_user_id = telegram_user_id
        self.error = error


class TelegramLinkClient(Protocol):
    def consume_link_code(
        self, code: str, web_user_id: str
    ) -> ConsumeLinkCodeResult: ...

    def unlink(self, telegram_user_id: str) -> bool: ...


class GrpcTelegramLinkClient:
    def __init__(self, settings: Settings) -> None:
        self._addr = settings.notifier_grpc_addr
        self._token = settings.notifier_internal_auth_token or ""

    def _metadata(self) -> list[tuple[str, str]]:
        return [("authorization", f"Bearer {self._token}")]

    def consume_link_code(self, code: str, web_user_id: str) -> ConsumeLinkCodeResult:
        with grpc.insecure_channel(self._addr) as channel:
            stub = subscriptions_pb2_grpc.SubscriptionServiceStub(channel)  # type: ignore[no-untyped-call]
            response = stub.ConsumeTelegramWebLinkCode(
                subscriptions_pb2.ConsumeTelegramWebLinkCodeRequest(
                    code=code, web_user_id=web_user_id
                ),
                metadata=self._metadata(),
            )
            return ConsumeLinkCodeResult(
                ok=response.ok,
                telegram_user_id=response.telegram_user_id,
                error=response.error,
            )

    def unlink(self, telegram_user_id: str) -> bool:
        with grpc.insecure_channel(self._addr) as channel:
            stub = subscriptions_pb2_grpc.SubscriptionServiceStub(channel)  # type: ignore[no-untyped-call]
            response = stub.UnlinkTelegramWebUser(
                subscriptions_pb2.UnlinkTelegramWebUserRequest(
                    telegram_user_id=telegram_user_id
                ),
                metadata=self._metadata(),
            )
            return bool(response.ok)


def get_telegram_link_client() -> TelegramLinkClient:
    return GrpcTelegramLinkClient(get_settings())


def link_telegram_account(
    connection: Connection[Any], *, user_id: str, code: str
) -> dict[str, Any]:
    existing = repository.get_telegram_link_by_user(connection, user_id)
    if existing is not None:
        raise api_error(
            409,
            "telegram_already_linked",
            "This account already has a linked Telegram identity.",
            {"user_id": user_id},
        )
    client = get_telegram_link_client()
    result = client.consume_link_code(code, user_id)
    if not result.ok:
        error_map = {
            "invalid_code": ("telegram_link_invalid_code", "Link code is invalid."),
            "expired_code": ("telegram_link_expired_code", "Link code has expired."),
            "already_used": (
                "telegram_link_already_used",
                "Link code has already been used.",
            ),
        }
        code_name, message = error_map.get(
            result.error, ("telegram_link_invalid_code", "Link code is invalid.")
        )
        raise api_error(422, code_name, message, {"error": result.error})
    return repository.create_telegram_link(
        connection, user_id=user_id, telegram_user_id=result.telegram_user_id
    )


def unlink_telegram_account(connection: Connection[Any], *, user_id: str) -> None:
    existing = repository.get_telegram_link_by_user(connection, user_id)
    if existing is None:
        return
    client = get_telegram_link_client()
    client.unlink(existing["telegram_user_id"])
    repository.unlink_telegram_user(connection, user_id)


def get_telegram_link_status(
    connection: Connection[Any], *, user_id: str
) -> dict[str, Any] | None:
    return repository.get_telegram_link_by_user(connection, user_id)
