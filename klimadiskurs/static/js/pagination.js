// this script displays the glossary content as a paginated list using List.js

function pagination (maxItems=glossaryLength) {
    // instantiate List.js List object
    // use paginate: true to show page numbers (enable display in CSS!)
    const options = {
        page: itemsPerPage
    };
    var listObj = new List("glossary-content", options);

    // previous and next buttons behavior
    // https://stackoverflow.com/a/34502656
    var nextBtn = document.getElementById("btn-next");
    var prevBtn = document.getElementById("btn-prev");
    prevBtn.disabled = true;
    var i = 1;

    // what happens when clicking the "next" button
    function showNextPage () {
        i += itemsPerPage;
        // show next page
        listObj.show(i, itemsPerPage); 
        // enable prev button (since we can't be on the first page now)
        prevBtn.disabled = false;
        // disable next button on last page
        if (i+itemsPerPage > maxItems) {
            nextBtn.disabled = true;
        }
    }

    // what happens when clicking the "previous" button
    function showPrevPage () {
        i -= itemsPerPage;
        // show previous page
        listObj.show(i, itemsPerPage); 
        // enable next button (since we can't be on the last page now)
        nextBtn.disabled = false;
        // disable prev button on first page
        if (i < itemsPerPage) {
            prevBtn.disabled = true;
        }
    }

    nextBtn.addEventListener("click", showNextPage);
    prevBtn.addEventListener("click", showPrevPage);

    // enable keyboard shortcuts
    // https://stackoverflow.com/a/31625525
    $(document).keydown(function(e) {
        switch(e.which) {
            // left arrow key shows previous page
            case 37:
                if (!prevBtn.disabled) { showPrevPage(); }
                break;
            // right arrow key shows next page
            case 39:
                if (!nextBtn.disabled) { showNextPage(); }
                break;
            default: return;
        }
    });
}

pagination();
