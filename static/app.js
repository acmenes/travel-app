const $searchBar = document.getElementById("search-countries")

BASE_URL_COUNTRIES = "https://restcountries.eu/rest/v2/name"
BASE_URL_AMADEUS = "https://test.api.amadeus.com/v1"

AMADEUS_ACCESS_TOKEN = "AItrr8OmqIAw811pYPEB4qK6GAs4"

function handleClick(e) {
    e.preventDefault()
    processForm()
}

async function processForm(searchterm) {
    countrySearched = document.getElementById("country-search").value
    console.log(countrySearched)
    const res = await axios.get(`${BASE_URL_COUNTRIES}/${countrySearched}`)
    country = res.data[0]
    console.log(res.data[0])
    console.log(`You searched for ${country.name}`)
    console.log(country.borders)
    console.log(`The capital of ${country.name} is ${country.capital}`)
    console.log(`Languages spoken are ${country.languages[0]}`)
    console.log(`${country.name} is in this timezone: ${country.timezones}`)
    console.log(country.flag)
}

/// I need to serialize this data into JSON so I can feed it to the app and then use jinja

$("#search-countries").on("submit", handleClick);

// $("#search-button").on("click", processForm)

function testFunc(searchTerm) {
    const res = await axios.get(`${BASE_URL_COUNTRIES}/${searchTerm}`)
    country = res.data[0]
    console.log(res.data[0])
    console.log(`You searched for ${country.name}`)
    console.log(country.borders)
    console.log(`The capital of ${country.name} is ${country.capital}`)
    console.log(`Languages spoken are ${country.languages[0]}`)
    console.log(`${country.name} is in this timezone: ${country.timezones}`)
    console.log(country.flag)
}