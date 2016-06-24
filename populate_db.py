from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine(
'sqlite:///itemcatalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

user1 = User(name = "User1", email="user1@email.com", picture="")
session.add(user1)
session.commit()

#Category 1
category1 = Category(name = "Category 1")
session.add(category1)
session.commit()

item1 = Item(name = "Item 1", description = "This is the first item.", category = category1, user = user1)
session.add(item1)
session.commit()

item2 = Item(name = "Item 2", description = "This is the second item.", category = category1, user = user1)
session.add(item2)
session.commit()

item3 = Item(name = "Item 3", description = "This is the third item.", category = category1, user = user1)
session.add(item3)
session.commit()

item4 = Item(name = "Item 4", description = "This is the fourth item.", category = category1, user = user1)
session.add(item4)
session.commit()

item5 = Item(name = "Item 5", description = "This is the fifth item.", category = category1, user = user1)
session.add(item5)
session.commit()

item6 = Item(name = "Item 6", description = "This is the sixth item.", category = category1, user = user1)
session.add(item6)
session.commit()

#Category 2
category2 = Category(name = "Category 2")
session.add(category2)
session.commit()

item7 = Item(name = "Item 7", description = "This is the seventh item.", category = category2, user = user1)
session.add(item7)
session.commit()

item8 = Item(name = "Item 8", description = "This is the eigth item.", category = category2, user = user1)
session.add(item8)
session.commit()

item9 = Item(name = "Item 9", description = "This is the nineth item.", category = category2, user = user1)
session.add(item9)
session.commit()

item10 = Item(name = "Item 10", description = "This is the tenth item.", category = category2, user = user1)
session.add(item10)
session.commit()

item11 = Item(name = "Item 11", description = "This is the eleventh item.", category = category2, user = user1)
session.add(item11)
session.commit()

item12 = Item(name = "Item 12", description = "This is the twelfth item.", category = category2, user = user1)
session.add(item12)
session.commit()

#Category 3
category3 = Category(name = "Category 3")
session.add(category3)
session.commit()

item13 = Item(name = "Item 13", description = "This is the thirteenth item.", category = category3, user = user1)
session.add(item13)
session.commit()

item14 = Item(name = "Item 14", description = "This is the fourteenth item.", category = category3, user = user1)
session.add(item14)
session.commit()

item15 = Item(name = "Item 15", description = "This is the fifteenth item.", category = category3, user = user1)
session.add(item15)
session.commit()

item16 = Item(name = "Item 16", description = "This is the sixteenth item.", category = category3, user = user1)
session.add(item16)
session.commit()

item17 = Item(name = "Item 17", description = "This is the seventeenth item.", category = category3, user = user1)
session.add(item17)
session.commit()

item18 = Item(name = "Item 18", description = "This is the eighteenth item.", category = category3, user = user1)
session.add(item18)
session.commit()

print "Items added to the db!"
