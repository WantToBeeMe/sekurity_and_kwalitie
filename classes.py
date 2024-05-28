class Addres:
    def __init__(self, street: str, house_number: str, zip: str, city: str) -> None:
        self.street: str = street
        self.house_number: str = house_number
        self.zip: str = zip
        self.city: str = city


class Member:
    def __init__(self, id: str, first_name: str, last_name: str,
                age: int, gender: str, weight: float,
                addres: Addres, email: str, phone: str) -> None:
        self.id: str = id
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.age: int = age
        self.gender: str = gender
        self.weight: float = weight
        self.addres: Addres = addres
        self.email: str = email
        self.phone: str = phone


global CONSULTANT; CONSULTANT = 0
global ADMIN; ADMIN = 1
global SUPER_ADMIN; SUPER_ADMIN = 2


class User:
    def __init__(self, id: int, username: str, password_hash: str, type: int, first_name: str, last_name: str, registration_date: str) -> None:
        self.id: int = id
        self.username: str = username
        self.password_hash: str = password_hash
        self.type: int = type
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.registration_date: str = registration_date