import pytest

import contribute


def _tag(name, category, superset=None, description=None, entry_name=None):
    return {
        "name": name,
        "entry_name": name if entry_name is None else entry_name,
        "description": description,
        "category": category,
        "superset": superset,
        "implied_tags": [],
    }


def test_tag_controls_groups_catalog_and_hides_computed_tags():
    groups, diet_checkboxes = contribute.tag_controls({
        "tags": [
            _tag("Soup", "meal"),
            _tag("Vegan", "diet", superset="Vegetarian", description="No animal products"),
            _tag("Vegetarian", "diet"),
            _tag("Gluten-Free", "diet"),
            _tag("Stephani", "stephani"),
            _tag("Spicy", "vibe", description="Hot, rather than just aromatic"),
            _tag("Slow", "making"),
            _tag("Freezes", "practical"),
            _tag("AI", "practical", description="Drafted with AI"),
            _tag("Popular", "usage"),
            _tag("Shown", "seasonal", entry_name="Shown entry", description="A new category"),
            "not a tag",
        ],
    })

    assert [heading for heading, _tags in groups] == [
        "Meal",
        "Diet",
        "Stephani",
        "Vibe",
        "Effort",
        "Good to know",
        "seasonal",
    ]
    assert groups[1][1] == [
        {"entry_name": "Vegan", "name": "Vegan", "description": "No animal products"},
        {"entry_name": "Vegetarian", "name": "Vegetarian", "description": None},
    ]
    assert diet_checkboxes == [
        {"entry_name": "Gluten-Free", "name": "Gluten-Free", "description": None},
    ]
    assert groups[3][1][0]["description"] == "Hot, rather than just aromatic"
    assert groups[-1][1] == [
        {"entry_name": "Shown entry", "name": "Shown", "description": "A new category"},
    ]
    posted = [
        tag["entry_name"]
        for _heading, tags in groups
        for tag in tags
    ] + [tag["entry_name"] for tag in diet_checkboxes]
    assert "AI" not in posted
    assert "Popular" not in posted


def test_tag_controls_rejects_a_catalog_without_tags():
    with pytest.raises(ValueError):
        contribute.tag_controls({})
