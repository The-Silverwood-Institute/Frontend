const assert = require("assert");
const {
  parseQuantity,
  mergeIngredients,
  formatIngredient,
  copyIngredientsList,
} = require("./static/copy.js");

const ingredient = (name, quantity) => ({
  name,
  parsed: parseQuantity(quantity),
});

const fakeEl = (name, quantity) => ({
  getAttribute: attr => {
    if (attr === "x-ingredient") return name;
    if (attr === "x-quantity") return quantity;
    return null;
  },
});

assert.deepStrictEqual(parseQuantity(""), { type: "none" });
assert.deepStrictEqual(parseQuantity("1tsp"), { type: "none" });
assert.deepStrictEqual(parseQuantity("2tbsp"), { type: "none" });
assert.deepStrictEqual(parseQuantity("50g"), {
  type: "simple",
  amount: 50,
  unit: "g",
  unitRaw: "g",
});
assert.deepStrictEqual(parseQuantity("150 g"), {
  type: "simple",
  amount: 150,
  unit: "g",
  unitRaw: " g",
});

{
  const merged = mergeIngredients([
    ingredient("Butter", "50g"),
    ingredient("butter", "150g"),
  ]);
  assert.strictEqual(merged.length, 1);
  assert.strictEqual(formatIngredient(merged[0]), "200g Butter");
}

{
  const merged = mergeIngredients([
    ingredient("Onion", "2"),
    ingredient("onion", "3"),
  ]);
  assert.strictEqual(formatIngredient(merged[0]), "5 Onion");
}

{
  const merged = mergeIngredients([
    ingredient("Salt", "1tsp"),
    ingredient("salt", "1/2tsp"),
  ]);
  assert.strictEqual(merged.length, 1);
  assert.strictEqual(formatIngredient(merged[0]), "Salt");
}

{
  const merged = mergeIngredients([
    ingredient("Butter", "50g"),
    ingredient("Butter", "2tbsp"),
  ]);
  assert.strictEqual(merged.length, 1);
  assert.strictEqual(formatIngredient(merged[0]), "50g Butter");
}

{
  const merged = mergeIngredients([
    ingredient("Milk", "100ml"),
    ingredient("Milk", "50g"),
  ]);
  assert.strictEqual(merged.length, 2);
  assert.strictEqual(formatIngredient(merged[0]), "100ml Milk");
  assert.strictEqual(formatIngredient(merged[1]), "50g Milk");
}

{
  const list = copyIngredientsList([
    fakeEl("Butter", "50g"),
    fakeEl("Sugar", "100g"),
    fakeEl("butter", "150g"),
  ]);
  assert.strictEqual(list, "200g Butter\n100g Sugar");
}

console.log("test_copy.js: all assertions passed");
