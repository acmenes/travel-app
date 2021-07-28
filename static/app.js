const $searchBar = document.getElementById("search-countries")

function handleClick(e) {
    e.preventDefault()
    console.log("clicked")
    search()
}

function search(){
    const countrySearched = $("input[name=all-countries]").val()
    console.log(countrySearched)
    window.location.href = `/countries/${countrySearched}`
    console.log("click click")
}

$("#search-countries").on("submit", handleClick);

