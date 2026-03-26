from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    clerk = "clerk"
    dispatcher = "dispatcher"
    resident = "resident"
