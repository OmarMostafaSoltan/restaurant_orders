class DomainError(Exception):
    pass

class InvalidOrderState(DomainError):
    pass

class ItemNotAvailable(DomainError):
    pass

class OrderNotFound(DomainError):
    pass

class EmptyOrder(DomainError):
    pass

class SizeNotAvailable(DomainError):
    pass