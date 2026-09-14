"""Internal, one-use write authorization; never exposed in tool schemas."""
from contextvars import ContextVar
from contextlib import contextmanager

_permission = ContextVar("ticket_write_permission", default=None)


@contextmanager
def authorize_ticket(payload):
    token = _permission.set(dict(payload))
    try:
        yield
    finally:
        _permission.reset(token)


def consume_ticket_permission(payload):
    allowed = _permission.get()
    _permission.set(None)
    return allowed is not None and allowed == payload
