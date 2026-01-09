import os
from typing import Any, Optional


try:
    from langfuse import Langfuse  # type: ignore
except Exception:
    Langfuse = None


class DummyTrace:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.input: Any = kwargs.get("input")
        self.output: Any = None
        self.error: Optional[str] = None

    def end(self) -> None:
        pass


class DummyLangfuse:
    def trace(self, *args: Any, **kwargs: Any) -> DummyTrace:
        return DummyTrace(*args, **kwargs)


def get_langfuse_client() -> Any:
    """
    Возвращает реальный клиент Langfuse, если есть ключи и установлен SDK,
    иначе — dummy-клиент, который ничего не делает.
    """
    if Langfuse is None:
        return DummyLangfuse()

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        return DummyLangfuse()

    return Langfuse(public_key=public_key, secret_key=secret_key, host=host)
