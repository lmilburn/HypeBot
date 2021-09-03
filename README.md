# README
## General
Created by Luc Milburn

HypeBot is a Discord bot intended to create a virtual economy for users to buy, sell, and trade rare clothing items obtained via webscraping. The bot was created using Python, Scrapy, and the Discord API. 

I am planning on further developing the bot to price compare across multiple sites, so it can act as either a means of practicality or entertainment.

## Changelog + To-Do
Version 0.1 - Bot scrapes a single website and users can obtain a "daily" item by invoking "!daily". Items which are out of stock on the website cannot be obtained, adding a sense of rarity to certain items

Version 0.11 - Inventory system fixed, bug was preventing item from being properly stored in json file in user's inventory.

Version 0.2 - Users have inventory systems which keep track of their items they've earned. They also have an overall monetary balance from items they have sold. Users can quicksell the items they get for 70% of the listed price. Items will randomly drop for users in the server.

Version 0.3 (in development) - Users can search the price of an item. They can price compare across multiple sites. Image of the item is displayed when randomly dropped or searched.

Future features I would like to implement:

 - Expand web scraping to include multiple sites as opposed to one source
 - Price comparisons and item lookup; high/low of a specified item
 - Include image of the item in question
