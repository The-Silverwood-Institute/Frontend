const getIngredient = ingredientEl => {
  const name = ingredientEl.getAttribute("x-ingredient");
  const quantity = ingredientEl.getAttribute("x-quantity");

  if (!quantity || quantity.endsWith("tsp") || quantity.endsWith("tbsp")) {
    return name;
  } else {
    return `${quantity} ${name}`;
  }
};

document.getElementById('copy').addEventListener('click', e => {
    const ingredientEls = Array.from(document.querySelectorAll('.ingredient'));
    const ingredients = ingredientEls.map(getIngredient);

    const ingredientList = ingredients.join('\n');

    navigator.clipboard.writeText(ingredientList);
});
