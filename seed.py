#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import sqlite3
import os

try:
    os.remove('recipes.db')
    print 'Deleted old recipes'
except OSError:
    print 'No recipes to delete'
    pass

conn = sqlite3.connect('recipes.db')

c = conn.cursor()

# Create table
c.execute('CREATE TABLE recipes (name text, url text, ingredients text, method text)')

# Insert a rows of data
c.execute("INSERT INTO recipes VALUES ('Chilli Con Carne', 'chilli-con-carne', 'Oil\nSalt\nPepper\n1 tsp Chilli Powder\n1 tsp Crushed/whole dried chillies\nPaprika\nTomato Puree\nTinned tomatoes\nItalian Herbs\nBrown Sauce\nBeef stock cube/Bovril\nRice\nOlive Oil\n1 Onion\n1 Garlic Clove\nTin of Kidney Beans\n1 tbsp Honey (optional)\n500g Mince', 'Slice onions, crush garlic then brown in 2 tsp olive oil.\nAdd the mince in batches and brown then stir in chilli powder and paprika.\nAdd the stock cube/Bovril dissolved in a small amount of water and stir.\nThen add 2 inches or so of tomato puree and stir again, followed by the tinned tomatoes.\nSimmer for half an hour then check for taste.\nAdd chilli powder or tomato puree depending on flavour, also salt/pepper if needed.\nA tablespoon of honey can improve the flavour.\nServe with rice (preferably) or pasta.')")
c.execute("INSERT INTO recipes VALUES ('Beef Stroganoff', 'beef-stroganoff', '500g Beef (not casserole, too tough, or fillet, too expensive)\n1 Garlic Clove\n1 Onion\n5-6 Mushrooms\nBeef/Pork Stock Cube OR 1 Tbsp Bovril\nPinch Salt\nPinch Pepper\nPinch Paprika\nWedge Butter', 'Cover meat with Clingfilm and hit with a rolling pin to flatten it.\nCut into thin strips and sprinkle with salt/pepper/paprika.\nSlice mushrooms and place to one ride.\nSlice the onions and crush the garlic then brown in melted butter.\nOnce softened take out and put on plate to the side.\nBrown the meat in batches then add the mushrooms and the Bovril or stock cube, diluted in a cup of hot water.\nPut the onions back and add the soured cream then bring the mixture to just under boiling.\nSimmer for 40 minutes then serve with rice or pasta, ideally rice.')")
c.execute("INSERT INTO recipes VALUES ('Easy Soup', 'easy-soup', 'Knob Butter\n1 Onion\n1 Red Pepper\n1 Apple\n1 Carrot\n600ml Water\nStock Cube\nMixed Herbs\nExtra vegetables (Optional)', 'Chop up everything and place everything but the onions in a bowl.\nBoil the water and add the stock cube and stir it in.\nMelt the butter then add the onions and soften then under a low heat for a minute or so. \nAdd all the vegetables then the water and herbs.\nTurn up the heat and boil for a minute then turn down the heat and simmer it for 30 minutes. Wait until cool and blend.')")
c.execute("INSERT INTO recipes VALUES ('Mushroom and parsnip rösti pie', 'mushroom-parsnip-pie', 'olive oil\n750g/1lb 10oz mixed mushrooms, roughly chopped into chunks\n3 garlic cloves, sliced\nsmall bunch thyme, leaves picked\n2 red onions, sliced\n2 carrots, finely chopped\n250g/9oz swede, finely chopped\n200ml/7fl oz white wine or vegetable stock\n1 tbsp vegetarian Worcestershire sauce\n1 tbsp Dijon mustard\n2 tbsp wholegrain mustard\nsmall bunch fresh flat leaf parsley, roughly chopped\n2-4 tbsp crème fraîche (optional)\n3 small parsnips, grated\nsea salt and freshly ground black pepper', 'Place a large ovenproof frying pan over a high heat and add a good glug of oil. Add enough mushrooms to cover the base of the pan, season with salt and pepper, and sauté until nicely brown and beginning to crisp at the edges. Transfer to a bowl and fry the remaining mushrooms in batches.\nPut the pan back on the heat and add another glug of oil. Add the garlic, thyme, onions, carrots and swede, season with a good pinch of salt and pepper and cook over a medium heat for 10 minutes, until softened and starting to brown.\nPreheat the oven to 200C/180C Fan/Gas 6.\nAdd the mushrooms and the wine or stock, and simmer until almost all the liquid has evaporated. Add the Worcestershire sauce, mustards, parsley and crème fraîche, if using, and cook gently for a few more minutes, until you have a rich gravy. Taste and add more salt and pepper if needed.\nSeason the parsnips with salt and pepper and pile on top of the mushroom mixture, leaving a little gap around the edge. Drizzle generously with oil and bake for 40 minutes, until golden brown and crisp.')")

# c.execute("INSERT INTO recipes VALUES ('', '', '', '')")

# Save (commit) the changes
conn.commit()

recipeCount = c.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
print "Saved {} recipes to the database".format(recipeCount)

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
