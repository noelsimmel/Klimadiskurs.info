// source: https://www.w3schools.com/howto/howto_css_modals.asp
var modal = document.getElementById("submit-modal");

// show modal when button is clicked
$(document).on("click", "#btn-modal", function() {
    modal.style.display = "block";
    $("input#term").focus();    // autofocus "term" field
});

// hide modal when clicking outside it
$(document).on("click", window, function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
});

// reopen the modal after submit if there is an error
// https://stackoverflow.com/a/56991433
$(document).ready(function() {
  // checks if the form-error class is present in the HTML and reopens the modal
  if ($('.form-error').length) {
    modal.style.display = "block";
  }
});
