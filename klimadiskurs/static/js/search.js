// search function for search form
// when the "Suchen" button is clicked, JS saves the form field input and performs and AJAX call
// https://stackoverflow.com/questions/41475945/ajax-request-to-perform-search-in-flask
$(document).on("click", "#btn-search", function (e) {
    e.preventDefault();
    var searchTerm = $('input[name=query]').val().toLowerCase();
    if (!searchTerm) { searchTerm = "None"; }
    makeAjaxCall(searchTerm);
});

// search function for glossary index (alphabet)
// when a letter of the alphabet is clicked, show search results for "klima<letter>"
$(document).on("click", ".alpha", function (e) {
    e.preventDefault();
    // https://stackoverflow.com/a/38887018
    var searchTerm = "Klima" + $(this).text().toLowerCase();
    makeAjaxCall(searchTerm);
});

/** Actual AJAX call:
 * Get search result from /api route in routes.py
 * Replace glossary content with it and display pagination buttons if necessary
 */
function makeAjaxCall (searchTerm) {
    $.ajax({
        type: "GET",
        url: "/api",
        data: {"query": searchTerm},
        success: function (glossary) {
            const resultsCount = Object.keys(glossary).length;

            // replace header content with "Suchergebnisse"
            $("#glossary-header").empty();
            $("#glossary-header").append(`Suchergebnisse (${resultsCount})`)

            // empty all glossary content
            $("#glossary-content").empty();

            const newContent = getGlossaryContent(glossary, resultsCount, searchTerm);
            
            // replace glossary content HTML with newContent
            document.getElementById("glossary-content").innerHTML = newContent;

            // call pagination.js
            if (resultsCount > itemsPerPage) { pagination(resultsCount); }
        }
    });
}

/** Helper function that generates the HTML for the search results */
function getGlossaryContent (glossary, resultsCount, searchTerm) {
    // always show alphabet
    var newContent = `<div id="glossary-alphabet">`;
    for (var char in ["A", "Ä", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "Ö", "P", "Q", "R", "S", "T", "U", "Ü", "V", "W", "X", "Y", "Z"]) {
        newContent += `<span class="alpha">` + char + `</span>`;
    }
    newContent += "</div>";

    // if no search results
    if (!resultsCount) {
        newContent = "<p style='margin-top: 2em'>Die Suche erzielte leider keine Treffer.<p>";
        // insert submit button if submissions are enabled
        if (enableSubmissions) {
            newContent += "<p>Möchten Sie einen Glossareintrag vorschlagen?</p>";
            newContent += "<button id='btn-modal'>Vorschlagen</button>"
        }
        
    // if search results
    } else {
        // this is the javascript version of goecke-glossary.html
        var newContent = "<ul class='list'>";
        for (var i = 0; i < resultsCount; i++) {
            var entry = Object.keys(glossary)[i];
            if (glossary[entry].definition.length ||
                glossary[entry].sources.length ||
                tweetedTerms.includes(entry)) {
                newContent += `<li><a href='/def/${entry}'>${entry}</a></li>`;
            } else {
                newContent += `<li>${entry}</li>`;
            }
        }
        newContent += "</ul>";

        // responsive design version for phone screens
        newContent += "<ul class='glossary-one-list'>";
        for (var i = 0; i < resultsCount; i++) {
            var entry = Object.keys(glossary)[i];
            if (glossary[entry].definition.length ||
                glossary[entry].sources.length ||
                tweetedTerms.includes(entry)) {
                newContent += `<li><a href='/def/${entry}'>${entry}</a></li>`;
            } else {
                newContent += `<li>${entry}</li>`;
            }
        }
        newContent += "</ul>";

        // add pagination if necessary
        // next and previous buttons
        var paginationHtml = `<div class="glossary-pagination"><button id="btn-prev">&#8592;</button><br><button id="btn-next">&#8594;</button><br>`;
        // show results on one page button (actually a link)
        paginationHtml += `<div class="tooltip"><a href="/search/${searchTerm}" class="button" id="btn-one">1</a>`;
        // explanatory tooltip
        paginationHtml += `<span class="tooltip-text">Auf einer Seite<br>anzeigen</span></div></div>`;
        if (resultsCount > itemsPerPage) { newContent += paginationHtml; }
    }

    return newContent;
}
