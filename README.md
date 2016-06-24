To create the database, use the command
	python database_setup.py

To populate the database, use the command
	python populate_db.py
This script will populate the database with 1 user, 3 categories, each category having 6 items linked to the user. 


To run the project, use the command
	python project.py

To access the site use http://localhost:8080
(this link must be used for the authorization to work)

Links

http://localhost:8080/categories -> Will show the categories stored in the database

http://localhost:8080/category/category_id/items -> Will show the items stored in a category
If you are logged in, you will see the option to add a new item to this category.
If you are not logged in, you will se the items in the category.


http://localhost:8080/category/category_id/new -> Will show the form to add a new item in the category
If you are not logged in, it will redirect you to the login page.

http://localhost:8080/category/category_id/item_id -> Will show the item name and item description
If you are logged in and you are the creator of the item, you will see the options to edit and delete the item.
Else you will see only the item name and the description.

http://localhost:8080/category/category_id/item_id/edit -> Will show the form to edit the item
If you are not logged in, it will redirect you to the login page.
If you are not the creator of the item, it will notice you through a message that you are not authorized.

http://localhost:8080/category/category_id/item_id/delete -> Will show a page to delete the item
If you are not logged in, it will redirect you to the login page.
If you are not the creator of the item, it will notice you through a message that you are not authorized.

http://localhost:8080/login -> Page to login
http://localhost:8080/gdisconnect -> Page to disconnect

JSON Links:

http://localhost:8080/categories/JSON -> Will give a JSON representation of the categories

http://localhost:8080/category/category_id/items/JSON -> Will give a JSON representation of the items of a category

http://localhost:8080/category/category_id/item_id/JSON -> Will give a JSON representation of the chosen item from the chosen category
