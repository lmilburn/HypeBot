from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
import random
import discord
import os
from discord.ext import commands
import math


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


@daily_item.error
async def bot_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    timeInHours = (error.retry_after / 60)/60
    timeInMinutes = (timeInHours-int(timeInHours))*60 
    msg = 'You have already claimed today, please try again in {} hours and {} minutes'.format(int(timeInHours), int(timeInMinutes))
    await ctx.send(msg)

async def get_bank_data():
  with open("mainbank.json", "r") as bank:
    users = json.load(bank)
  return users

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

bot.run(TOKEN)

