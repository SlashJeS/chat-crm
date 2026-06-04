DEFAULT_MESSAGE_LIMIT = 30
MAX_MESSAGE_LIMIT = 100


def parse_message_limit(value, default=DEFAULT_MESSAGE_LIMIT):
    try:
        limit = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(limit, MAX_MESSAGE_LIMIT))
