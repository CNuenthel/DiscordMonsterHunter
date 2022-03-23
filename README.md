# DiscordMonsterHunter
Discord server based monster hunting RPG


Discord Monster Hunter is a command bot designed to be run in a discord server that allows for the creation of heroes, with individual classes, to combat elevating tiers of monsters. DMH Bot offers items, equipment, a leveling system, class abilities, and endless fun. 

I built this Bot to practice various aspects of Python while I studied the language. DMG Bot is currently operational in this discord server:

https://discord.gg/gzsv8emEak 

Anyone is welcome to contribute, take, or review the code, or just come play the game!

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
There are a lot of actions that a player can do, so much so that it is unsavory to combine shopping activities, with monster battling activities in the same channel, or else you will be in slow mode for time in memoriam. Activities must be individually channeled. You **MUST** assign your desired channel ID to each of these channels. For example, you need a channel to use monster fighting commands such as .fight; so copy the ID of your "fight monsters" discord channel and set beyond_the_gates equal to that ID. Repeat for additional channels. Here is a list of required channels:

- welcome = Intro channel where player training begins 
- beyond_the_gates = Monster fighting channel 1 
- the_meadow = Location to fight very powerful secret boss 
- general_chat = general chat... obviously 
- the_shop = Item purchasing, selling 
- raid_1 = Raid channel 1 
- mixed_leaderboard = Leaderboard for raid stats across all classes 
- class_leaderboard = Leaderboard for raid stats across individual classes
- classes = Channel to describe in-game classes (helpful information for players)

The following listed channels are available to add if you would like additional channels for people to fight monsters. These are pretty good at reducing channel speeds when multiple players are fighting monsters in a single channel. They are not required to be active but are available if you'd like to use them.

- beyond_the_battlefield = Monster fighting channel 2 
- heart_of_the_maw = Monster fighting channel 3 
- raid_2 = Raid channel 2 
- raid_3 = Raid channel 3 

## **Setting Channels/Admin**
File: main.py
lines: 70-90

Place discord channel id's for the channels specified in **Bot Specifics**, and set the admin variable to your discord id. There are a few channels left in the list, but they are not required to run the bot unless they are found in **Bot Specifics**.

## **Filling The Basics**
To fill your classes channel, just go into the channel in discord and use the command *.classes*. This will fill the channel with embeds describing all the character classes. You must have admin set to your discord ID or this will not work.

- Now you are ready to play!
If you need any other help, come into https://discord.gg/gzsv8emEak and send a message to @Voodoo

p.s. I could move the code around to make it a lot more organized, but honestly I've rewritten the entire program 3 times, and every time I learn 20 new things. I'll do it just one more time, but at this point the time/reward ratio is just not there.
