def notEmpty(listItem):
    return len(listItem) != 0

def listRecipes(db):
    recipeList = db.select('recipes', what="name, url", order="name")

    return recipeList
