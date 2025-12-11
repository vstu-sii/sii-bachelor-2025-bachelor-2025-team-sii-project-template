from __future__ import annotations

from typing import Any, Optional

try:
    from langfuse import Langfuse  # type: ignore
except Exception:  # SDK не установлен или другая проблема
    Langfuse = None  # type: ignore


class _DummyTrace:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def __getattr__(self, name: str) -> Any:
        # Любые обращения к полям/методам просто игнорируются
        def _noop(*args: Any, **kwargs: Any) -> None:
            return None

        return _noop


class _DummyLangfuse:
    def trace(self, *args: Any, **kwargs: Any) -> _DummyTrace:
        return _DummyTrace()


_langfuse_client: Optional[Any] = None


def get_langfuse_client() -> Any:
    """
    Возвращает экземпляр Langfuse или dummy, если SDK не настроен.
    Langfuse читает ключи из переменных окружения:
    LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST.
    """
    global _langfuse_client

    if _langfuse_client is not None:
        return _langfuse_client

    if Langfuse is None:
        _langfuse_client = _DummyLangfuse()
        return _langfuse_client

    try:
        _langfuse_client = Langfuse()
    except Exception:
        _langfuse_client = _DummyLangfuse()

    return _langfuse_client
