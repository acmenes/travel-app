'''Seed the database, including the countries from the All Countries CSV file'''

from csv import DictReader
from app import db 
from models import User, Country

db.drop_all()
db.create_all()

with open('generator/country_database.csv') as countries:
    db.session.bulk_insert_mappings(Country, DictReader(countries))

# u1 = User(username="Alyssa", password="MillieIsGood", bio="Musician and Coder", img_url="https://picsum.photos/200")

# db.session.add(u1)

db.session.commit()