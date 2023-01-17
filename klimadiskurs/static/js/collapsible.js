// collapse all open collapsibles when opening another one
// https://stackoverflow.com/a/61218186

// toggle collapse of specified content
function toggleContent(content) {
    if (content.style.maxHeight) {
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + 'px';
    }
}
  
// collapse all open content
function collapseAllOpenContent(colls) {
    for (const coll of colls) {
        if (coll.classList.contains('active')) {
            coll.classList.remove('active');
            toggleContent(coll.nextElementSibling);
        }
    }
}
  
//   
const colls = document.getElementsByClassName('collapsible');
for (const coll of colls) {
    coll.addEventListener('click', function() {
      if (!this.classList.contains('active')) {
        collapseAllOpenContent(colls);
      }
      this.classList.toggle('active');
      toggleContent(this.nextElementSibling);
    });
}
