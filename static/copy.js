const isOmittedQuantity = quantity =>
  !quantity || quantity.endsWith("tsp") || quantity.endsWith("tbsp");

const parseQuantity = raw => {
  if (isOmittedQuantity(raw)) {
    return { type: "none" };
  }

  const match = /^([0-9]+(?:\.[0-9]+)?)( ?[a-zA-Z]+)?$/.exec(raw.trim());
  if (match) {
    return {
      type: "simple",
      amount: parseFloat(match[1]),
      unit: (match[2] || "").trim().toLowerCase(),
      unitRaw: match[2] || "",
    };
  }

  return { type: "opaque", raw };
};

const formatAmount = amount => {
  if (Number.isInteger(amount)) {
    return String(amount);
  }
  return String(parseFloat(amount.toFixed(2)));
};

const formatQuantity = parsed => {
  if (parsed.type === "none") {
    return "";
  }
  if (parsed.type === "opaque") {
    return parsed.raw;
  }
  return `${formatAmount(parsed.amount)}${parsed.unitRaw}`;
};

const sameName = (a, b) => a.name.toLowerCase() === b.name.toLowerCase();

const canMergeParsed = (a, b) => {
  if (a.type === "none") {
    return true;
  }
  if (b.type === "none") {
    return true;
  }
  if (a.type === "simple" && b.type === "simple") {
    return a.unit === b.unit;
  }
  if (a.type === "opaque" && b.type === "opaque") {
    return a.raw === b.raw;
  }
  return false;
};

const combineParsed = (a, b) => {
  if (a.type === "none") {
    return b;
  }
  if (b.type === "none") {
    return a;
  }
  if (a.type === "simple" && b.type === "simple") {
    return {
      type: "simple",
      amount: a.amount + b.amount,
      unit: a.unit,
      unitRaw: a.unitRaw,
    };
  }
  return a;
};

const extractIngredient = ingredientEl => {
  const name = ingredientEl.getAttribute("x-ingredient");
  const quantity = ingredientEl.getAttribute("x-quantity");
  return {
    name,
    parsed: parseQuantity(quantity),
  };
};

const mergeIngredients = ingredients => {
  const merged = [];

  ingredients.forEach(ingredient => {
    const existing = merged.find(
      candidate =>
        sameName(candidate, ingredient) &&
        canMergeParsed(candidate.parsed, ingredient.parsed)
    );

    if (existing) {
      existing.parsed = combineParsed(existing.parsed, ingredient.parsed);
      return;
    }

    merged.push({
      name: ingredient.name,
      parsed: ingredient.parsed,
    });
  });

  return merged;
};

const formatIngredient = ingredient => {
  const quantity = formatQuantity(ingredient.parsed);
  if (!quantity) {
    return ingredient.name;
  }
  return `${quantity} ${ingredient.name}`;
};

const getIngredient = ingredientEl => formatIngredient(extractIngredient(ingredientEl));

const copyIngredientsList = ingredientEls =>
  mergeIngredients(ingredientEls.map(extractIngredient))
    .map(formatIngredient)
    .join("\n");

if (typeof document !== "undefined") {
  const copyButton = document.getElementById("copy");
  if (copyButton) {
    copyButton.addEventListener("click", e => {
      const copyEl = e.currentTarget;
      const ingredientEls = Array.from(document.querySelectorAll(".ingredient"));
      const ingredientList = copyIngredientsList(ingredientEls);

      navigator.clipboard.writeText(ingredientList).then(() => {
        copyEl.classList.remove("is-copied");
        void copyEl.offsetWidth;
        copyEl.classList.add("is-copied");
      });
    });
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    parseQuantity,
    mergeIngredients,
    formatIngredient,
    formatQuantity,
    copyIngredientsList,
    getIngredient,
    extractIngredient,
  };
}
