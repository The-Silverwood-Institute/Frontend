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

# Save (commit) the changes
conn.commit()

print 'Saved 1 recipe to the database'

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
