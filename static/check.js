const checkEl = document.getElementById("check");
const ingredientsEl = document.getElementById("ingredients");

if (checkEl && ingredientsEl) {
  checkEl.addEventListener("click", () => {
    ingredientsEl.classList.toggle("is-checking");
  });
}
