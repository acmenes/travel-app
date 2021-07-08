const $searchBar = document.getElementById("search-countries")

BASE_URL_COUNTRIES = "https://restcountries.eu/rest/v2/name"

async function processForm(searchterm) {
    alert("you clicked")
    const res = await axios.get(`${BASE_URL_COUNTRIES}/${searchterm}`)
    console.log(res.data[0])
    console.log(`You searched for ${res.data[0].name}`)
}

$("#search-countries").on("submit", processForm);

$("#search-button").on("click", processForm)

function testFunc() {
    console.log("test")
}