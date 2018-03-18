var searchElement = document.getElementById("search");
var searchForm = document.getElementById("searchForm");
var menuItems = Array.from(document.getElementsByClassName("mdl-navigation__link"));
var searchTimer;

searchElement.addEventListener("keyup", startSearchTimer);
searchElement.addEventListener("keydown", cancelSearchTimer);
searchForm.addEventListener("submit", onSearchSubmit);

searchElement.disabled = false;

function startSearchTimer() {
  searchTimer = setTimeout(filterRecipes, 20);
}

function cancelSearchTimer() {
  clearTimeout(searchTimer);
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
  cancelSearchTimer();
  filterRecipes();

  visibleMenuItems = document.querySelectorAll(".mdl-navigation__link:not([hidden])");

  if (visibleMenuItems.length == 1) {
    window.location.href = visibleMenuItems[0].getAttribute("href");
  }
}
