const $searchBar = document.getElementById("search-countries")

const BASE_URL_COUNTRIES = "https://restcountries.eu/rest/v2/name"
const BASE_URL_AMADEUS = "http://api.amadeus.com"

const AMADEUS_ACCESS_TOKEN = "xASzeerH5RXb2vb0ZJKdTCngmK6mI0Ur"

const $addDreamDest = document.getElementById("add-dream-dest")
const $addBeenThere = document.getElementById("add-been-there")

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

$("#add-dream-fest").on("submit", handleDreamDest)

function handleDreamDest() {
    e.preventDefault()
}

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

async function testAmadeus() {
    const res = await axios.get(`${BASE_URL_AMADEUS}`)
    console.log(res)
}