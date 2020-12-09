

function displayMap(data) {
    var map = L.map('mapid').setView([46, 2], 6);
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoiYnJpenppbzEzMDEyIiwiYSI6ImNraGV4OHhtYzA2NGUyenFwaWthMjkyc2wifQ.i8Wv7Lku06XxDOtoUBskqw'
    }).addTo(map);
    var idx = 0
    if (Object.keys(data).length != 0) {
        for (var key in data) {
            console.log(data[key]["points"])
            L.polyline(data[key]["points"], {color: data[key]["color"]}).addTo(map)
            idx = key
        }
        L.marker(data[0]["points"][0]).addTo(map).bindPopup("<b>Départ<b>").openPopup()
        L.marker(data[idx]["points"].slice(-1)[0]).addTo(map).bindPopup("<b>Arrivée<b>")
    }
}


function matchNames(id) {
    var dropdown = ""
    if (id == "search-from") {
        dropdown = "dropdown-from"
    }
    else {
        dropdown = "dropdown-to"
    }
    var elem = document.getElementById(id)
    var request = new XMLHttpRequest()
    var url = "https://api-adresse.data.gouv.fr/search/?q=".concat(encodeURI(elem.value).concat("&type=&autocomplete=1")) 
    console.log(url)
    request.open('GET', url, true)

    request.onload = function() {
        var data = JSON.parse(this.response)
        var list = document.getElementById(dropdown)
        list.innerHTML = ""
        list.classList.remove("show")
        data["features"].forEach(item => {
            console.log(item["properties"]["label"])
            var elem = document.createElement("a")
            elem.classList.add("dropdown-item")
            elem.appendChild(document.createTextNode(item["properties"]["label"]))

            if (id == "search-from") {
                elem.addEventListener("click", selectItemFrom)
            }
            else {
                elem.addEventListener("click", selectItemTo)
            }
            list.appendChild(elem)
        });

        showDropDown(dropdown)
    }
    request.send()
}


function showDropDown(dropdown_name) {
    document.getElementById(dropdown_name).classList.toggle("show")
}

function selectItemFrom() {
    document.getElementById("search-from").value = this.text
    showDropDown("dropdown-from")
}

function selectItemTo() {
    document.getElementById("search-to").value = this.text
    showDropDown("dropdown-to")
}

function init() {
}


window.onload = init