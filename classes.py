from enum import Enum

# IMPORTANT!
#   Note that every data in the database must be saved as a string 
#   (except the id, since that is generated by the db itself)
#   That's because we encrypt and decrypt, which only works on strings


class Member:
    def __init__(self, id: int, first_name: str, last_name: str, age: str, gender: str,
                 weight: str, street_name: str, house_number: str, zip_code: str,
                 city: str, email: str, phone: str) -> None:
        self.id: int = id
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.age: int = int(age)
        self.gender: str = gender
        self.weight: float = float(weight)
        self.street_name: str = street_name
        self.house_number: str = house_number
        self.zip_code: str = zip_code
        self.city: str = city
        self.email: str = email
        self.phone: str = phone


class UserType(Enum):
    CONSULTANT = 0
    ADMIN = 1
    SUPER_ADMIN = 2


class User:
    def __init__(self, id: int, username: str, password_hash: str, type: str,
                 first_name: str, last_name: str, registration_date: str) -> None:
        self.id: int = id
        self.username: str = username
        self.password_hash: str = password_hash
        self.type: UserType = UserType(int(type))
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
