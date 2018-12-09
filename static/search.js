var searchElement = document.getElementById("search");
var searchForm = document.getElementById("searchForm");
var menuItems = Array.from(document.getElementsByClassName("mdl-navigation__link"));
var searchTimer;

searchElement.addEventListener("input", resetSearchTimer);
searchForm.addEventListener("submit", onSearchSubmit);

searchElement.disabled = false;

function resetSearchTimer() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(filterRecipes, 20);
}

function filterRecipes() {
  var searchTerm = searchElement.value.toLowerCase();
  menuItems.forEach(function(menuItem) {
    if (menuItem.text.toLowerCase().includes(searchTerm)) {
      menuItem.hidden = false;
    } else {
      menuItem.hidden = true;
    }
  });
}

function onSearchSubmit(e) {
  e.preventDefault();
  clearTimeout(searchTimer);
  filterRecipes();

  visibleMenuItems = document.querySelectorAll(".mdl-navigation__link:not([hidden])");

  if (visibleMenuItems.length == 1) {
    window.location.href = visibleMenuItems[0].getAttribute("href");
  }
}
