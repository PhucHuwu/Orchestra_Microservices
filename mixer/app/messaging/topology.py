EXCHANGE_TYPE = "topic"


def dead_letter_queue_name(queue_name: str) -> str:
    return f"{queue_name}.dlq"


def dead_letter_routing_key(queue_name: str) -> str:
    return dead_letter_queue_name(queue_name)
