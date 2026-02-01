import uuid

def generate_user_id() -> str:
    return str(uuid.uuid4())

def is_valid_state(state: str) -> bool:
    return state == "In Progress" or state == "Won" or state == "Lost"
