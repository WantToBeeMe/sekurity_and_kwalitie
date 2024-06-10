from database import (setup_database, close_database, Database)
from user_validation import CITY_LIST, GENDER_LIST
import random

if __name__ != '__main__':
    raise SystemExit("This file is not meant to be imported. "
                     "Please run this script directly so load a bunch of testing data into the database")


# note that this script is only for us to make testing easier.
# you can also consider it some kind of hacking approach that someone is skipping our cool frontend UI
# and is directly talking to the backend. So, yea, feel free to break the backend like this

def r_gender() -> str:
    return random.choice(GENDER_LIST)


def r_city() -> str:
    return random.choice(CITY_LIST)


try:
    # setting up the database
    setup_database()
    db = Database()

    # logging in as super admin to get all the privileges
    # NOTE: This will fail if you previously change the super_admin's name or password. if so,
    # then the rest will also fail
    db.login_user('super_admin', 'Admin_123?')

    # now we generate a bunch of users
    # (note that all phonenumbers are 8 long, since we assume that all have 06 in front of it)
    existing_members = db.get_all_members()
    existing_emails = [member.email for member in existing_members]

    def add_member(*args):
        if not args[9] in existing_emails:
            db.create_member(*args)

    add_member('John', 'doe', '25', 'Male', '80', 'Main street', '1', '1234AB', 'Amsterdam',
               'john.doe@gmail.com', '12345678')
    add_member('Jane', 'doe', '20', 'Female', '60', 'Other street', '2', '1234AB', 'Rotterdam',
               'doe.jane@outlook.com', '87654321')

    add_member('Alice', 'Smith', '30', r_gender(), '65', 'Elm street', '5', '5678CD', r_city(),
               'alice234smith@example.com', '12341111')
    add_member('Bob', 'Johnson', '40', r_gender(), '85', 'Pine Lane', '10', '2345EF', r_city(),
               'bob.johnson96@example.com', '12342222')
    add_member('Charlie', 'Brown', '35', r_gender(), '75', 'Maple', '15', '3456GH', r_city(),
               'charlie.brown@example.com', '12343333')
    add_member('Diana', 'Evans', '28', r_gender(), '68', 'Cedar', '20', '4567IJ', r_city(),
               'diana12evans@example.com', '12344444')
    add_member('Edward', 'Wilson', '50', r_gender(), '90', 'Oak street', '25', '5678KL', r_city(),
               'edward.wilson32@example.com', '12345555')
    add_member('Fiona', 'Garcia', '22', r_gender(), '58',  'Birch Lane', '30', '6789MN', r_city(),
               'fiona.garcia@example.com', '12346666')

    add_member('George', 'Harrison', '45', r_gender(), '78', 'Fir street', '35', '7890OP', r_city(),
               'george.harrison@example.com', '12347777')
    add_member('Helen', 'Martinez', '33', r_gender(), '70', 'Spruce Avenue', '40', '8901QR', r_city(),
               'helen.martinez@example.com', '12348888')
    add_member('Irene', 'Lopez', '27', r_gender(), '55', 'Ash street', '45', '9012ST', r_city(),
               'irene.lopez@example.com', '12349999')
    add_member('Jack', 'Davis', '38', r_gender(), '82', 'Willow Lane', '50', '0123UV', r_city(),
               'jack.davis@example.com', '12340000')
    add_member('Karen', 'Miller', '29', r_gender(), '62', 'Poplar street', '55', '1234WX', r_city(),
               'karen.miller@example.com', '12341111')
    add_member('Liam', 'Taylor', '31', r_gender(), '72', 'Palm street', '60', '2345YZ', r_city(),
               'liam.taylor@example.com', '12342222')

    db.create_consultant('consultant', 'Consultant_123?', 'Consultant', 'User')
    db.create_admin('sir_admin1', 'AdminAdmin_123?', 'Admin', 'User')
    db.create_consultant('consult_2', 'Consultant_321?', 'Consultant', 'User')
    db.create_admin('sir_admin2', 'AdminAdmin_321?', 'Admin', 'User')

    print("errors:")
    all_errors = db.get_errors()
    for error in all_errors:
        print(error)
    if not all_errors:
        print("No errors found")

finally:
    close_database()
