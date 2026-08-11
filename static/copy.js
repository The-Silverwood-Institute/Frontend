const copyButton = document.getElementById("copy");
if (copyButton) {
  copyButton.addEventListener("click", e => {
    const copyEl = e.currentTarget;
    const ingredientList = JSON.parse(copyEl.getAttribute("data-ingredients"));

    navigator.clipboard.writeText(ingredientList).then(() => {
      copyEl.classList.remove("is-copied");
      void copyEl.offsetWidth;
      copyEl.classList.add("is-copied");
    });
  });
}
