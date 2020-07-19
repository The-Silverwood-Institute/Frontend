const searchElement = document.getElementById("search");
const searchForm = document.getElementById("searchForm");
const menuItems = Array.from(document.getElementsByClassName("mdl-navigation__link"));
let searchTimer;
let apiUrl;

searchElement.addEventListener("input", resetSearchTimer);
searchForm.addEventListener("submit", onSearchSubmit);

fetch('/manifest.json')
  .then(resp => resp.json())
  .then(json => {
    apiUrl = json['apiUrl'];

    searchElement.disabled = false;
  });

function resetSearchTimer() {
  clearTimeout(searchTimer);

  localSearchTimer = setTimeout(searchRecipes, 40);
}

function searchRecipes() {
  const searchTerm = searchElement.value;

  const dispatchEventId = searchTimer;
  const params = new URLSearchParams({
    "hasIngredient": searchTerm
  });

  return fetch(apiUrl + '/recipes/?' + params.toString())
    .then(resp => resp.json())
    .then(json => {
      if (dispatchEventId != searchTimer) {
        console.log('Discarding outdated results');
        return;
      }

      return new Set(json.map(recipe => recipe['url']));
    })
    .then(
      urls => filterRecipes(searchTerm, urls),
      () => filterRecipes(searchTerm)
    );
}

function filterRecipes(searchTerm, urls) {
  urls = (typeof urls !== 'undefined') ? urls : new Set([]);

  menuItems.forEach(menuItem => {
    const match = menuItem.text.toLowerCase().includes(searchTerm.toLowerCase())
                    || urls.has(menuItem.getAttribute('href'));

    if (match) {
      menuItem.hidden = false;
    } else {
      menuItem.hidden = true;
    }
  });
}

function onSearchSubmit(e) {
  e.preventDefault();
  clearTimeout(searchTimer);

  searchRecipes().finally(() => {
    visibleMenuItems = document.querySelectorAll(".mdl-navigation__link:not([hidden])");

    if (visibleMenuItems.length == 1) {
      window.location.href = visibleMenuItems[0].getAttribute("href");
    }
  });
}
