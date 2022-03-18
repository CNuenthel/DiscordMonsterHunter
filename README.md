# DiscordMonsterHunter
Discord server based monster hunting RPG


Discord Monster Hunter is a command bot designed to be run in a discord server that allows for the creation of heroes, with individual classes, to combat elevating tiers of monsters. DMH Bot offers items, equipment, a leveling system, class abilities, and endless fun. 

I built this Bot to practice various aspects of Python while I studied the language. DMG Bot is currently operational in this discord server:

https://discord.gg/gzsv8emEak 

Anyone is welcome to contribute, take, or review the code. 

## **Setup**

To create a bot you must go to the discord developer portal: https://discord.com/developers/docs/intro

Build your bot following the documentation

1. Keep track of your bot TOKEN
2. Keep track of your bot APP ID

## In **config.json**:
```json
{
  "bot_prefix": ".",
  "token": "DISCORD BOT TOKEN GOES HERE",
  "application_id": "DISCORD APP ID GOES HERE",
  "owners": [
    "OWNER NAME GOES HERE"
  ]
}
```
Put in your bot token and app id. We are all done here. 

## **Bot Specifics**
There are a lot of actions that a player can do, so much so that it is unsavory to combine shopping activities, with monster battling activities in the same channel, or else you will be in slow mode for time in memoriam. Activities must be individually channeled. Here is a list of required channels:

- welcome = Intro channel where player training begins 
- beyond_the_gates = Monster fighting channel 1 
- beyond_the_battlefield = Monster fighting channel 2 
- heart_of_the_maw = Monster fighting channel 3 
- the_meadow = Location to fight very powerful secret boss 
- general_chat = general chat... obviously 
- the_shop = Item purchasing, selling 
- raid_1 = Raid channel 1 
- raid_2 = Raid channel 2 
- raid_3 = Raid channel 3 
- mixed_leaderboard = Leaderboard for raid stats across all classes 
- class_leaderboard = Leaderboard for raid stats across individual classes
- classes = Channel to describe in-game classes

## **Setting Channels/Admin**
File: main.py
lines: 70-90

Place discord channel id's for the channels specified in **Bot Specifics**, and set the admin variable to your discord id. There are a few channels left in the list, but they are not required to run the bot unless they are found in **Bot Specifics**.

## **Filling The Basics**
To fill your classes channel, just go into the channel in discord and use the command *.classes*. This will fill the channel with embeds describing all the character classes. 

- Now you are ready to play!
If you need any other help, come into https://discord.gg/gzsv8emEak and send a message to @Voodoo
