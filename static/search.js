var searchElement = document.getElementById("search");
var searchForm = document.getElementById("searchForm");
var menuItems = Array.from(document.getElementsByClassName("mdl-navigation__link"));
var localSearchTimer;
var apiSearchTimer;

searchElement.addEventListener("input", resetSearchTimer);
searchForm.addEventListener("submit", onSearchSubmit);

searchElement.disabled = false;

function resetSearchTimer() {
  clearTimeout(localSearchTimer);
  clearTimeout(apiSearchTimer);

  localSearchTimer = setTimeout(localFilterRecipes, 20);
  apiSearchTimer = setTimeout(apiFilterRecipes, 100); // Queries an API so shouldn't fire as often
}

function localFilterRecipes() {
  var searchTerm = searchElement.value.toLowerCase();
  menuItems.forEach(function(menuItem) {
    if (menuItem.text.toLowerCase().includes(searchTerm)) {
      menuItem.hidden = false;
    } else {
      menuItem.hidden = true;
    }
  });
}

function apiFilterRecipes() {
  const dispatchEventId = apiSearchTimer;

  const params = new URLSearchParams({
    "hasIngredient": searchElement.value
  });

  return fetch('https://recibase-api.herokuapp.com/recipes/?' + params.toString())
    .then(resp => resp.json())
    .then(json => {
      if (dispatchEventId != apiSearchTimer) {
        console.log('Discarding outdated results');
        return;
      }

      const recipeUrls = new Set(json.map(recipe => recipe['url']));

      menuItems.filter(item => recipeUrls.has(item.getAttribute('href'))).forEach(item => item.hidden = false);
    });
}

function onSearchSubmit(e) {
  e.preventDefault();
  clearTimeout(localSearchTimer);
  clearTimeout(apiSearchTimer);

  localFilterRecipes();
  apiFilterRecipes().finally(() => {
    visibleMenuItems = document.querySelectorAll(".mdl-navigation__link:not([hidden])");

    if (visibleMenuItems.length == 1) {
      window.location.href = visibleMenuItems[0].getAttribute("href");
    }
  });
}
