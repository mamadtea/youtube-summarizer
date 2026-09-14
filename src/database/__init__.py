from .history import History
from .payments import PaymentManager
from .subscriptions import SubscriptionManager
from .users import UserSettings

users = UserSettings()
history = History()
subscriptions = SubscriptionManager()
payments = PaymentManager()


__all__ = [
    "history",
    "payments",
    "subscriptions",
    "users",
]