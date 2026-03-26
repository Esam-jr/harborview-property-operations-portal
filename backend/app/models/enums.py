from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    clerk = "clerk"
    dispatcher = "dispatcher"
    resident = "resident"


class ListingStatus(str, Enum):
    draft = "draft"
    published = "published"
    unpublished = "unpublished"


class ListingMediaType(str, Enum):
    image = "image"
    video = "video"


class ServiceOrderStatus(str, Enum):
    submitted = "submitted"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class BillingStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    refunded = "refunded"


class PaymentMethod(str, Enum):
    check = "check"
    money_order = "money_order"


class EvidenceType(str, Enum):
    payment = "payment"
    refund_request = "refund_request"
