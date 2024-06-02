from enum import Enum


class Address:
    def __init__(self, street: str, house_number: str, zip: str, city: str) -> None:
        self.street: str = street
        self.house_number: str = house_number
        self.zip: str = zip
        self.city: str = city


class Member:
    def __init__(self, id: str, first_name: str, last_name: str, age: int, gender: str,
                 weight: float, address: Address, email: str, phone: str) -> None:
        self.id: str = id
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.age: int = age
        self.gender: str = gender
        self.weight: float = weight
        self.address: Address = address
        self.email: str = email
        self.phone: str = phone


class UserType(Enum):
    CONSULTANT = 0
    ADMIN = 1
    SUPER_ADMIN = 2


class User:
    def __init__(self, id: int, username: str, password_hash: str, type: int,
                 first_name: str, last_name: str, registration_date: str) -> None:
        self.id: int = id
        self.username: str = username
        self.password_hash: str = password_hash
        self.type: UserType = UserType(type)
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.registration_date: str = registration_date

    def get_role_name(self) -> str:
        if self.type == UserType.CONSULTANT:
            return 'Consultant'
        elif self.type == UserType.ADMIN:
            return 'Admin'
        elif self.type == UserType.SUPER_ADMIN:
            return 'Super Admin'
        else:
            return 'Unknown'
