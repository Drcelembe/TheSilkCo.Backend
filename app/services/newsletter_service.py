# lightweight newsletter list manager (store in DB later)
SUBSCRIBERS = set()

def subscribe(email):
    if not email:
        return False
    SUBSCRIBERS.add(email.lower())
    return True

def unsubscribe(email):
    SUBSCRIBERS.discard(email.lower())
    return True

def list_subscribers():
    return list(SUBSCRIBERS)
