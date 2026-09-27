"""Form state and JSON for POST /recipe-submissions.

The API owns validation, Scala generation, and opening the pull request.
"""

TAG_GROUPS = (
    ("Meal", (
        ("Christmas", "Christmas"),
        ("Pudding", "Pudding"),
        ("Lunch", "Lunch"),
        ("Baking", "Baking"),
        ("NonMeal", "Not a Meal"),
        ("Soup", "Soup"),
    )),
    ("Diet", (
        ("Vegan", "Vegan"),
        ("VeganIsh", "Vegan-ish"),
        ("Vegetarian", "Vegetarian"),
        ("VegetarianIsh", "Vegetarian-ish"),
        ("Pescatarian", "Pescatarian"),
    )),
    ("Stephani", (
        ("Stephani", "Stephani"),
        ("StephaniIsh", "Stephani-ish"),
        ("StephaniUnhealthy", "StephaniUnhealthy"),
    )),
    ("Vibe", (
        ("ColdWeather", "Cold Weather"),
        ("HotWeather", "Hot Weather"),
        ("Stodge", "Stodge"),
        ("Spicy", "Spicy"),
    )),
    ("Effort", (
        ("Slow", "Slow"),
        ("Quick", "Quick"),
        ("Scales", "Scales"),
        ("HighEffort", "High Effort"),
        ("LowEffort", "Low Effort"),
    )),
    ("Good to know", (
        ("Freezes", "Freezes"),
        ("BetterNextDay", "Better Next Day"),
    )),
)

DIET_CHECKBOXES = (
    ("GlutenFree", "Gluten-Free"),
)

_BLANK_INGREDIENT = {
    "name": "",
    "quantity": "",
    "prep": "",
    "notes": "",
}

_FALLBACK_ERRORS = {
    401: "Invalid passcode.",
    409: "A recipe with this name already exists.",
    403: "Could not verify this submission.",
    502: "Could not open the pull request. Try again.",
    503: "Recipe submission is not available.",
}


def _clean(value):
    if value is None:
        return ""
    return str(value).strip()


def _or_none(value):
    return _clean(value) or None


def _lines(value):
    return [line.strip() for line in _clean(value).splitlines() if line.strip()]


def ingredient_rows(form):
    names = form.getlist("ingredient_name")
    quantities = form.getlist("ingredient_quantity")
    preps = form.getlist("ingredient_prep")
    notes = form.getlist("ingredient_notes")
    count = max(len(names), len(quantities), len(preps), len(notes))
    if count == 0:
        return [dict(_BLANK_INGREDIENT)]
    return [
        {
            "name": names[i] if i < len(names) else "",
            "quantity": quantities[i] if i < len(quantities) else "",
            "prep": preps[i] if i < len(preps) else "",
            "notes": notes[i] if i < len(notes) else "",
        }
        for i in range(count)
    ]


def page_state(form=None):
    if form is None:
        return {
            "passcode": "",
            "name": "",
            "source": "",
            "description": "",
            "notes": "",
            "method": "",
            "tags": [],
            "ingredients": [dict(_BLANK_INGREDIENT)],
        }
    return {
        "passcode": form.get("passcode", ""),
        "name": form.get("name", ""),
        "source": form.get("source", ""),
        "description": form.get("description", ""),
        "notes": form.get("notes", ""),
        "method": form.get("method", ""),
        "tags": form.getlist("tags"),
        "ingredients": ingredient_rows(form),
    }


def authorization_header(form):
    return "Bearer " + _clean(form.get("passcode"))


def submission_payload(form):
    ingredients = []
    for row in ingredient_rows(form):
        ingredient = {
            "name": _clean(row["name"]),
            "quantity": _or_none(row["quantity"]),
            "prep": _or_none(row["prep"]),
            "notes": _or_none(row["notes"]),
        }
        if any(ingredient.values()):
            ingredients.append(ingredient)
    return {
        "name": _clean(form.get("name")),
        "source": _or_none(form.get("source")),
        "description": _or_none(form.get("description")),
        "notes": _lines(form.get("notes")),
        "tags": [_clean(tag) for tag in form.getlist("tags") if _clean(tag)],
        "ingredients": ingredients,
        "method": _lines(form.get("method")),
        "cf-turnstile-response": _clean(form.get("cf-turnstile-response")),
    }


def pull_request_url(payload):
    if not isinstance(payload, dict):
        return None
    url = payload.get("url")
    if not isinstance(url, str) or any(char.isspace() for char in url):
        return None
    if not url.startswith("https://github.com/"):
        return None
    return url


def failure_message(response):
    text = (getattr(response, "text", None) or "").strip()
    headers = getattr(response, "headers", {}) or {}
    content_type = headers.get("Content-Type", "")
    parsed = None
    if "json" in content_type.lower() or text.startswith("{"):
        try:
            parsed = response.json()
        except ValueError:
            parsed = None
    if isinstance(parsed, dict):
        for key in ("error", "message"):
            value = parsed.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()[:500]
    if text and not text.startswith("<") and not text.startswith("{"):
        return text[:500]
    return _FALLBACK_ERRORS.get(
        getattr(response, "status_code", None),
        "Could not submit the recipe.",
    )
