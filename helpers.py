def toList(newlineSeparated):
    return filter(_notEmpty, newlineSeparated.split('\n'))

def _notEmpty(listItem):
    return len(listItem) != 0

def listRecipes(db):
    recipeList = db.select('recipes', what="name, url", order="name")

    return list(recipeList)
