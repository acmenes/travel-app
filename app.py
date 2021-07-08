from flask import Flask, render_template, request, jsonify, flash

from restcountries import RestCountryApiV2 as rapi

app = Flask(__name__)

app.config['SECRET_KEY'] = "MissMillieIsGood"

# use rapi.get_countries_by_name(countryname)

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/country')
def country_page():
    country_search = request.args["country-search"]
    country = rapi.get_countries_by_name(country_search, 
                                        filters=["name", 
                                        "capital", 
                                        "flag", 
                                        "currencies",
                                        "languages"])
    return render_template('country.html', country=country[0])