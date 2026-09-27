(function () {
  var list = document.getElementById("ingredient-rows");
  var addButton = document.getElementById("add-ingredient");
  var form = document.querySelector(".contribute-form");

  function rows() {
    return list.querySelectorAll(".ingredient-row");
  }

  addButton.addEventListener("click", function () {
    var clone = rows()[rows().length - 1].cloneNode(true);
    clone.querySelectorAll("input").forEach(function (input) {
      input.value = "";
    });
    list.appendChild(clone);
    var name = clone.querySelector('input[name="ingredient_name"]');
    if (name) {
      name.focus();
    }
  });

  list.addEventListener("click", function (event) {
    var button = event.target.closest("[data-remove-ingredient]");
    if (!button) {
      return;
    }
    var row = button.closest(".ingredient-row");
    if (rows().length === 1) {
      row.querySelectorAll("input").forEach(function (input) {
        input.value = "";
      });
      return;
    }
    row.remove();
  });

  form.addEventListener("submit", function () {
    var button = form.querySelector('[type="submit"]');
    button.disabled = true;
    button.textContent = "Submitting…";
  });
})();
