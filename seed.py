'''Seed the database, including the countries from the All Countries CSV file'''

from csv import DictReader
from app import db 
from models import User, Country, Unesco, Destination, VisitedCountry

db.drop_all()
db.create_all()

with open('generator/countries.csv') as countries:
    db.session.bulk_insert_mappings(Country, DictReader(countries))

# having trouble getting this to work

# with open('generator/whc-sites-2019.csv') as usites:
#     db.session.bulk_insert_mappings(Unesco, DictReader(usites))

u1 = User(username="Alyssa", password="MillieIsGood", bio="Musician and Coder", img_url="https://picsum.photos/200")

db.session.add(u1)
db.session.commit()

# d1 = Destination(user="Alyssa", country_name="Kyrgyzstan")
# d2 = Destination(user="Alyssa", country_name="Azerbaijan")
# d3 = Destination(user="Alyssa", country_name="Japan")
# v1 = VisitedCountry(user="Alyssa", country_name="United States of America")
# v2 = VisitedCountry(user="Alyssa", country_name="Panama")

# db.session.add_all([d1, d2, d3, v2])

# db.session.commit()