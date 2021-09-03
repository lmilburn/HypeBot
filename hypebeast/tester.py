from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
import random
import discord
import os
from discord.ext import commands
import math
import random

# select_random_item
# choose random item from the webscraped items
def select_random_item(itemList):
    x = random.choice(list(itemList.keys()))
    if itemList[x] is None:
        return (x, "None")
    return (x, itemList[x])


TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    process = CrawlerProcess(get_project_settings())
    process.crawl('hypebeastbot', domain='hbx.com')
    process.start()

#on_message
# Allows for items to be randomly dropped when users send messages
@bot.event
async def on_message(message):
  if random.random() > 0.95 and message.author != bot.user:
    with open('sample.json') as json_file:
      itemDict = json.load(json_file)
      itemTup = select_random_item(itemDict)
      if itemTup[1] != "None":
        response = "**{0}** received a random drop! It's a **{1}** with a value of **{2}**.".format(message.author, itemTup[0], itemTup[1])
        await open_account_random(message.author.id)
        users = await get_bank_data()
        users[str(message.author.id)]["items"][itemTup[0]] = itemTup[1]
        with open("mainbank.json", "w") as f:
            json.dump(users, f)
        await message.channel.send(response)
  await bot.process_commands(message)

#daily_item
# Stores randomly selected item inside of user's inventory and records info into json
@bot.command(name='daily', help='Once every 24 hours, roll for a free item')
@commands.cooldown(1.0, 86400.0, commands.BucketType.user)
async def daily_item(ctx):
    with open('sample.json') as json_file:
        itemDict = json.load(json_file)
    itemTup = select_random_item(itemDict)
    if itemTup[1] != "None":
        response = "You received **{0}** with a value of **{1}**.".format(itemTup[0], itemTup[1])
        await open_account(ctx.author)
        users = await get_bank_data()
        users[str(ctx.author.id)]["items"][itemTup[0]] = itemTup[1]
        with open("mainbank.json", "w") as f:
            json.dump(users, f)
        await ctx.send(response)
    else:
        response = "You tried to acquire **{0}** but it was sold out. Tough luck!".format(itemTup[0])
        await ctx.send(response)

#bot_error
# Called if user tries to access command before cooldown period expires
@daily_item.error
async def bot_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        timeInHours = (error.retry_after / 60) / 60
        timeInMinutes = (timeInHours - int(timeInHours)) * 60
        msg = 'You have already claimed today, please try again in {} hours and {} minutes'.format(int(timeInHours),
                                                                                                   int(timeInMinutes))
        await ctx.send(msg)

# get_bank_data()
# load the current table of users and their respective items
async def get_bank_data():
    with open("mainbank.json", "r") as bank:
        users = json.load(bank)
    return users

# open_account
# open the account information of a specific user. if no result, create a new account
async def open_account(user):
    users = await get_bank_data()
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["usd_balance"] = 0
        users[str(user.id)]["items"] = {}

    with open("mainbank.json", "w") as bank:
        json.dump(users, bank)
    return True

# open_account_random
# opens account info of specific user, but handling of the parameter is slightly different
async def open_account_random(user):
  users = await get_bank_data()
  if str(user) in users:
    return False
  else:
    users[str(user)] = {}
    users[str(user)]["usd_balance"] = 0
    users[str(user)]["items"] = {}
    with open("mainbank.json", "w") as bank:
        json.dump(users, bank)
    return True

# sell_item
# sell a specified item for 70% of its market value, remove from json, and add to usd_balance
@bot.command(name='sell', help='Sell an item for 70% of market value')
async def sell_item(ctx, *, arg):
    await open_account(ctx.author)
    users = await get_bank_data()
    if arg in users[str(ctx.author.id)]["items"]:
        temp_price = users[str(ctx.author.id)]["items"][arg]
        temp_price = temp_price.replace('USD ', '')
        temp_price = float(temp_price)
        del users[str(ctx.author.id)]["items"][arg]
        p = temp_price * 0.7
        p = round(p, 2)
        users[str(ctx.author.id)]["usd_balance"] += p
        response = "Item was sold successfully for **{0}**".format(users[str(ctx.author.id)]["usd_balance"])
        with open("mainbank.json", "w") as f:
            json.dump(users, f)
        await ctx.send(response)
    else:
        response = "You don't own that item!"
        await ctx.send(response)

#view_inventory
#displays inventory in an embedded message
@bot.command(name='inv', help='View your currently owned items')
async def view_inventory(ctx):
  await open_account(ctx.author)
  users = await get_bank_data()
  itemList = users[str(ctx.author.id)]["items"].keys()
  newline='\n'
  embed = discord.Embed(title="Inventory", description=f"{newline.join([x for x in itemList])}")
  await ctx.send(embed=embed)

#view_balance
# displays balance in a formatted message
@bot.command(name='balance', help='View your current monetary balance')
async def view_balance(ctx):
  await open_account(ctx.author)
  users = await get_bank_data()
  curr_balance = users[str(ctx.author.id)]["usd_balance"]
  curr_balance = '{:.2f}'.format(round(curr_balance, 2))
  response = "Your current balance is **${0}**".format(curr_balance)
  await ctx.send(response)

#give_money
# allows user to send money to another individual and updates json files
@bot.command(name='givemoney', help='Give money to another user in the server')
async def give_money(ctx, member: discord.Member = None, arg = 0):
  if member == None:
    await ctx.send("Please specify a user!")
  elif str(member.id) == str(ctx.author.id):
    await ctx.send("You cannot send yourself money.")
  elif int(arg) < 0:
    await ctx.send("Please select an amount greater than 0.")
  else:
    await open_account(ctx.author)
    users = await get_bank_data()
    temp_bal = users[str(ctx.author.id)]["usd_balance"]
    temp_bal -= int(arg)
    if temp_bal < 0:
      await ctx.send("Sorry, you don't have enough money for this transaction")
    else:
      users[str(ctx.author.id)]["usd_balance"] = temp_bal
      await open_account_random(member.id)
      users[str(member.id)]["usd_balance"] += int(arg)
      with open("mainbank.json", "w") as bank:
        json.dump(users, bank)
      await ctx.send("Transaction success!")

#give_item
# Same idea as give_money, but with clothing items
@bot.command(name='giveitem', help='View your current monetary balance')
async def give_item(ctx, member: discord.Member = None, *, arg):
  if member == None:
    await ctx.send("Please specify a user!")
  elif str(member.id) == str(ctx.author.id):
    await ctx.send("You cannot send yourself an item.")
  else:
    await open_account(ctx.author)
    users = await get_bank_data()
    temp_list = users[str(ctx.author.id)]["items"]
    if arg not in temp_list.keys():
      await ctx.send("You do not own that item!")
    else:
      temp_val = users[str(ctx.author.id)]["items"][arg]
      del users[str(ctx.author.id)]["items"][arg]
      await open_account_random(member.id)
      users[str(member.id)]["items"][arg] = temp_val
      with open("mainbank.json", "w") as bank:
        json.dump(users, bank)
      await ctx.send("Item trade successful!")

bot.run(TOKEN)


