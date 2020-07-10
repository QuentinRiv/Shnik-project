

var allWords = [];



async function getUserAsync(path) {
    let response = await fetch(path, {
        // fetch(`https://retry-unige.herokuapp.com/addDB`, {
        method: "GET",
        credentials: "include",
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json",
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': true
        })
    })
    let data = await response.json();
    return data;
}

async function prepareWords(path) {
    var fin = await getUserAsync(path);
    var allWords = fin['words'];
    $('#container').append(`<table>`)
    for (var value of allWords) {
        $('#container').append(`<tr>`)
        $('#container').append(`<td><input type="checkbox" id="${value}" name="interest" value="${value}"></td>`)    // Rajoute checkbox
        $('#container').append(`<td><label for="${value}">${value}</label></td>`)                              // Associe le nom
        $('#container').append(`<td><button class="flag" value="${value}"><i class="fa fa-flag"></i></button></td>`) // Met le bouton principal
        // $('#container').append(`<br>`);
        $('#container').append(`</tr>`)
    }
    $('#container').append(`</table>`)
    $('#imElem').attr("src", fin["path"]);          // Source de l'image a affiché
    flaggedWords = [];
    return fin
}


id = `2`
path = `https://retry-unige.herokuapp.com/test/` + id;
// path = `test/` + id;

prepareWords(path);



// Fonction qui, quand on appuie sur le drapeau, rajoute le mot flaggé dans une liste
$(document).on("click", ".flag", function () {
    flaggedWords.push($(this).attr("value"));
});


// Pour quand on confirme les choix de mots sélectionnés
async function submit_message() {
    console.debug("In Submit");
    var result = await getUserAsync(path);
    allWords = result["words"];
    var selectedWords = [];
    for (var value of allWords) {
        var button = document.getElementById(value);
        if (button.checked) {
            selectedWords.push(button.value)
        }
    }
    var textfield = document.getElementById("autre_valeur");

    var entry = {
        id: id,
        selwords: selectedWords,
        flagwords: flaggedWords,
        newwords : textfield.value
    };


    // fetch(`${window.origin}/addDB`, {
    fetch(`https://retry-unige.herokuapp.com/addDB`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
        .then(function (response) {
            if (response.status !== 200) {
                console.log(`Looks like there was a problem. Status code: ${response.status}`);
                return;
            }
            response.json().then(function (data) {
                console.log(data);
            });
        })
        .catch(function (error) {
            console.log("Fetch error: " + error);
        });

}


async function delete_message() {
    var result = await getUserAsync(path);

    allWords = result["words"];
    var selectedWords = [];

    for (var value of allWords) {
        var button = document.getElementById(value);
        if (button.checked) {
            selectedWords.push(button.value)
        }
    }

    var entry = {
        id: id,
        selwords: selectedWords,
    };

    // fetch(`${window.origin}/delete`, {
    fetch(`https://retry-unige.herokuapp.com/delete`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
        .then(function (response) {
            console.log('Response:', response)
            if (response.status !== 200) {
                console.log(`Looks like there was a problem. Status code: ${response.status}`);
                return;
            }
            response.json().then(function (data) {
                console.log(data);
            });
        })
        .catch(function (error) {
            console.log("Fetch error: " + error);
        });

}





