import random
import json
import math
from shop import Shop
import discord
from items import Items
from staticfunctions import inventory_capped

# Create monster shortcut dict
with open("shortcuts/monster_shortcuts_swapped.json", "r") as f:
    mns = json.load(f) # Monster Name Shortcut

def fake_fight_embed(hero):
    base = discord.Embed(
        title=f"__{hero.name} v. Imp__",
        colour=discord.Colour.green()
    )
    base.set_thumbnail(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/d42d897e-b8d5-"
                     "4d47-b722-e41cf8c28943/d5o0hx4-1e29b37a-1da9-44a3-b5c9-4108415d46d4.jpg?"
                     "token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxO"
                     "Dg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyM"
                     "jY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2Q0MmQ4OTdlLW"
                     "I4ZDUtNGQ0Ny1iNzIyLWU0MWNmOGMyODk0M1wvZDVvMGh4NC0xZTI5YjM3YS0xZGE5LTQ0YT"
                     "MtYjVjOS00MTA4NDE1ZDQ2ZDQuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG9"
                     "3bmxvYWQiXX0.XsTK8IktCvaC8RWtlNC-6K42Lvw4s4OABxHRp3Jri2U")
    base.set_author(name="Fight Complete!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-"
                             "id1159980027")
    base.add_field(name=f'{hero.name} Combat Results',
                   value=
                   f"\n*{hero.current_hp}/{hero.max_hp + hero.bonus_hp}* HP\n"
                   f"**Damage Roll:** 22\n"
                   f"**Status** {', '.join(hero.status)}\n\n"
                   f"**__Fight Effects__**\nNone",
                   inline=True)

    base.add_field(name=f'Imp Combat Results',
                   value=
                   f"\n*18/40* HP\n"
                   f"**Damage Roll:** 3\n"
                   f"**Status:** Normal\n\n"
                   f"**__Fight Effects__**\nNone",
                   inline=True)

    return base


def fake_fight_embed2(hero):
    base = discord.Embed(
        title=f"__{hero.name} v. Imp__",
        colour=discord.Colour.gold()
    )
    base.set_thumbnail(url="https://i.pinimg.com/originals/ab/17/e9/ab17e99bb2c9581d727143ed2acfe7c4.jpg")
    base.set_author(name="Fight Complete!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-"
                             "id1159980027")
    base.add_field(name=f'{hero.name} Combat Results',
                   value=
                   f"\n*{hero.current_hp}/{hero.max_hp + hero.bonus_hp}* HP\n"
                   f"**Damage Roll:** 34\n"
                   f"**Status** {', '.join(hero.status)}\n\n"
                   f"**Fight Effects**\nHero Crit...Damage x1.5",
                   inline=True)

    base.add_field(name=f'Imp Combat Results',
                   value=
                   f"\n*0/40* HP\n"
                   f"**Damage Roll:** 22\n"
                   f"**Status:** Normal\n\n"
                   f"**Fight Effects**\nNone",
                   inline=True)

    base.add_field(name=f"__{hero.name}__",
                   value=f"+55XP\nHealing Potion Received",
                   inline=False)
    return base


def fight_embed(fight, hero, monster):
    def set_embed_color_fight(hero_dmg, mtr_dmg):
        if hero_dmg < mtr_dmg:
            return "lose"
        elif hero_dmg > mtr_dmg:
            return "win"
        else:
            return "draw"

    hero_effects = [f"{status[0]}...{status[1]}" for status in fight.hero_status_in_play]
    string_hero_effects = '\n'.join(hero_effects)
    if not string_hero_effects:
        string_hero_effects = "None"

    monster_effects = [f"{status[0]}...{status[1]}" for status in fight.monster_status_in_play]
    string_monster_effects = '\n'.join(monster_effects)
    if not string_monster_effects:
        string_monster_effects = "None"

    colors = {
        "win": discord.Colour.green,
        "lose": discord.Colour.red,
        "draw": discord.Colour.blue
    }

    color_select = set_embed_color_fight(fight.hero_damage, fight.monster_damage)

    if fight.monster_status_damage > 0:
        mon_status_damage = f"+ {fight.monster_status_damage}"
    else:
        mon_status_damage = ""
    if fight.hero_status_damage > 0:
        hero_status_damage = f"+ {fight.hero_status_damage}"
    else:
        hero_status_damage = ""

    if hero.class_ == "Dark Druid":
        temp_status = [status for status in hero.status if status not in ["AotP", "AotB", "AotL", "AotA"]]
    else:
        temp_status = hero.status

    base = discord.Embed(
        title=f"__{hero.name} v. {monster.name}__",
        colour=colors[color_select]()
    )
    base.set_thumbnail(url=monster.link)
    base.set_author(name="Fight Complete!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-"
                             "id1159980027")
    base.add_field(name=f'{hero.name} Combat Results',
                   value=
                   f"\n*{hero.current_hp}/{hero.max_hp + hero.bonus_hp}* HP\n"
                   f"**Damage:** {fight.hero_damage} {mon_status_damage}\n"
                   f"**Status** {', '.join(temp_status)}\n\n"
                   f"**__Fight Effects__**\n{string_hero_effects}",
                   inline=True)

    base.add_field(name=f'{monster.name} Combat Results',
                   value=
                   f"\n*{monster.current_hp}/{monster.max_hp}* HP\n"
                   f"**Damage:** {fight.monster_damage} {hero_status_damage}\n"
                   f"**Status:** {', '.join(monster.status)}\n\n"
                   f"**__Fight Effects__**\n{string_monster_effects}",
                   inline=True)

    return base


def fight_kill_embed(fight, hero, monster, divided_gp, divided_xp, xp_boosted_heroes):

    hero_effects = [f"{status[0]}...{status[1]}" for status in fight.hero_status_in_play]
    string_hero_effects = '\n'.join(hero_effects)
    if not string_hero_effects:
        string_hero_effects = "None"

    monster_effects = [f"{status[0]}...{status[1]}" for status in fight.monster_status_in_play]
    string_monster_effects = '\n'.join(monster_effects)
    if not string_monster_effects:
        string_monster_effects = "None"

    reward_list = []
    for char in monster.attacked_by:
        if char in xp_boosted_heroes:
            reward_list.append([char, f"XP Boosted!\n+{divided_xp*2}XP\n{divided_gp} Gold"])
        elif char == hero.name:
            if monster.item is None or inventory_capped(hero):
                reward_list.append([char, f"+{divided_xp}XP\n{divided_gp} Gold"])
            else:
                reward_list.append([char, f"+{divided_xp}XP\n{monster.item} Received"])
        else:
            reward_list.append([char, f"+{divided_xp}XP\n{divided_gp} Gold"])

    if fight.monster_status_damage > 0:
        mon_status_damage = f"+ {fight.monster_status_damage}"
    else:
        mon_status_damage = ""
    if fight.hero_status_damage > 0:
        hero_status_damage = f"+ {fight.hero_status_damage}"
    else:
        hero_status_damage = ""

    base = discord.Embed(
        title=f"__{hero.name} v. {monster.name}__",
        colour=discord.Colour.gold()
    )
    base.set_thumbnail(url="https://i.pinimg.com/originals/ab/17/e9/ab17e99bb2c9581d727143ed2acfe7c4.jpg")
    base.set_author(name="Fight Complete!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-"
                             "id1159980027")
    base.add_field(name=f'{hero.name} Combat Results',
                   value=
                   f"\n*{hero.current_hp}/{hero.max_hp + hero.bonus_hp}* HP\n"
                   f"**Damage Roll:** {fight.hero_damage} {mon_status_damage}\n"
                   f"**Status** {', '.join(hero.status)}\n\n"
                   f"**Fight Effects**\n{string_hero_effects}",
                   inline=True)

    base.add_field(name=f'{monster.name} Combat Results',
                   value=
                   f"\n*{monster.current_hp}/{monster.max_hp}* HP\n"
                   f"**Damage Roll:** {fight.monster_damage} {hero_status_damage}\n"
                   f"**Status:** {', '.join(monster.status)}\n\n"
                   f"**Fight Effects**\n{string_monster_effects}",
                   inline=True)

    for reward in reward_list:
        base.add_field(name=f"__{reward[0]}__",
                       value=reward[1],
                       inline=False)

    return base


def give_item_embed(hero, item, target):
    base = discord.Embed(
        title=f"{hero} gave {target} their {item}!",
        description=f"{item} has been added to {target}'s inventory",
        colour=discord.Colour.darker_gray(),
    )
    base.set_thumbnail(url="https://i.pinimg.com/originals/57/a7/8a/57a78a4fce184139be02836a1c6fd0c4.jpg")

    return base

def standard_embed(title, text, footer=""):
    base = discord.Embed(
        title=title,
        description=text,
        colour=discord.Colour.random()
    )
    base.set_author(name="The Maw", icon_url="https://64.media.tumblr.com/d304e7c08da55e86200eb6dfd715c579/792ef4b7e833ddef-7e/s500x750/3a0f98dd7e7ed403346bd85f0e59fe4c0762de52.gifv")
    base.set_footer(text=footer)
    return base


def show_hero_embed(hero_object):
    hero = hero_object

    ascended_final = "slave"
    if hero.ascended:
        ascension_emotes = {
            "Fighter": "🗡",
            "Cleric": "🌿",
            "Tank": "🛡",
            "Artificer": "⚙",
            "Mage": "🌪",
            "Assassin": "🦂",
            "Necromancer": "💀",
            "Dark Druid": "🦖",
            "Monk": "👊"
        }
        ascended_string = []
        for ascension in hero.ascended_classes:
            ascended_string.append(ascension_emotes[ascension])
        ascended_final = "".join(ascended_string)
        if not ascended_final:
            ascended_final = "None"

    skills = []
    descrips = []
    for skill in hero.sp_atk:
        skills.append(hero.sp_atk[skill]["name"])
        descrips.append(hero.sp_atk[skill]["description"])
    data_string = []
    for i in range(len(skills)):
        data_string.append(f"__{skills[i]}__\n*{descrips[i]}*")
    if not data_string:
        data_string = ["None"]
    final_ability_values = ("\n".join(data_string))

    print(final_ability_values)

    format_inventory = ", ".join(hero.inventory)
    format_keys = ", ".join(hero.keys)
    format_armory = ", ".join(hero.armory)

    statusi = [status for status in hero.status if status not in ["AotP", "AotB", "AotL", "AotA"]]
    print(statusi)
    final_statusi = ", ".join(statusi)
    if len(final_statusi) < 1:
        final_statusi = "Normal"

    base = discord.Embed(
        title=f"__{hero.name}__",
        colour=discord.Colour.gold(),
        description=f"{hero.class_} / {hero.level}\n"
                    f"*{hero.current_hp}/{hero.max_hp + hero.bonus_hp}* HP\n"
    )
    if hero.ascended:
        base.add_field(name="Ascended", value=ascended_final, inline=False)
    base.set_thumbnail(url=hero.link)
    base.add_field(name=f"Special Abilities EP: {hero.current_ep}/{hero.max_ep + hero.bonus_ep}",
                   value=f"{final_ability_values}",
                   inline=False)
    base.add_field(name=f"Status",
                   value=f"{final_statusi}",
                   inline=True)
    base.add_field(name=f"Equipment",
                   value=f"{hero.equipment}",
                   inline=False)
    base.add_field(name=f"Armor",
                   value=f"{hero.armor}",
                   inline=False)
    base.add_field(name="...",
                   value=
                   f"**Owner:**\n{hero.owner}\n\n"
                   f"**Max HP:**\n{hero.max_hp+hero.bonus_hp}\n\n"
                   f"**Max Attack:**\n{hero.atk+hero.bonus_atk}\n\n"
                   f"**Defense:**\n{hero.defense+hero.bonus_def}\n\n"
                   f"**Keys:**\n{format_keys}\n\n"
                   f"**Crit:**\n{round(hero.crit_multiplier, 1)}\n\n",
                   inline=True)
    base.add_field(name="...",
                   value=
                   f"**Initiative:**\n{hero.initiative}\n\n"
                   f"**XP:**\n{hero.xp}\n\n"
                   f"**Armory:**\n{format_armory}\n\n"
                   f"**Resting:**\n{hero.resting}\n\n"
                   f"**GP:**\n{hero.gold}\n\n"
                   f"**Inventory:**\n{format_inventory}\n\n",
                   inline=True)
    return base


def stat_embed(hero):

    ascended_final = "slave"
    if hero.ascended:
        ascension_emotes = {
            "Fighter": "🗡",
            "Cleric": "🌿",
            "Tank": "🛡",
            "Artificer": "⚙",
            "Mage": "🌪",
            "Assassin": "🦂",
            "Necromancer": "💀",
            "Dark Druid": "🦖",
            "Monk": "👊"
        }
        ascended_string = []
        for ascension in hero.ascended_classes:
            ascended_string.append(ascension_emotes[ascension])
        ascended_final = "".join(ascended_string)
        if not ascended_final:
            ascended_final = "None"

    skills = []
    descrips = []
    for skill in hero.sp_atk:
        skills.append(hero.sp_atk[skill]["name"])
        descrips.append(hero.sp_atk[skill]["description"])
    data_string = []
    for i in range(len(skills)):
        data_string.append(f"**__{skills[i]}__**\n*{descrips[i]}*")
    if not data_string:
        data_string = ["None"]
    final_ability_values = ("\n".join(data_string))

    format_inventory = ", ".join(hero.inventory)
    format_keys = ", ".join(hero.keys)
    format_armory = ", ".join(hero.armory)

    statusi = [status for status in hero.status]

    final_statusi = ", ".join(statusi)
    if len(final_statusi) < 1:
        final_statusi = "Normal"

    base = discord.Embed(
        title=f"__{hero.name}__",
        colour=discord.Colour.gold(),
        description=f"**{hero.class_} / {hero.level}**\n"
                    f"*{hero.current_hp}/{hero.max_hp + hero.bonus_hp} HP*\n"
    )
    if hero.ascended:
        base.add_field(name="Prestige Ascensions", value=ascended_final, inline=False)
    base.set_thumbnail(url=hero.link)
    base.add_field(name=f"Special Abilities EP: {hero.current_ep}/{hero.max_ep + hero.bonus_ep}",
                   value=f"{final_ability_values}",
                   inline=False)
    base.add_field(name=f"Status",
                   value=f"{final_statusi}",
                   inline=True)
    base.add_field(name=f"Equipment",
                   value=f"{hero.equipment}",
                   inline=False)
    base.add_field(name=f"Armor",
                   value=f"{hero.armor}",
                   inline=False)
    base.add_field(name="...",
                   value=
                   f"**Max HP:**\n{hero.max_hp+hero.bonus_hp}\n\n"
                   f"**Max Attack:**\n{hero.atk+hero.bonus_atk}\n\n"
                   f"**Defense:**\n{hero.defense+hero.bonus_def}\n\n"
                   f"**Keys:**\n{format_keys}\n\n"
                   f"**Crit:**\n{round(hero.crit_multiplier + hero.bonus_crit, 1)}\n\n",
                   inline=True)
    base.add_field(name="...",
                   value=
                   f"**Initiative:**\n{hero.initiative}\n\n"
                   f"**XP:**\n{hero.xp}\n\n"
                   f"**Armory:**\n{format_armory}\n\n"
                   f"**Resting:**\n{hero.resting}\n\n"
                   f"**GP:**\n{hero.gold}\n\n"
                   f"**Inventory:**\n{format_inventory}\n\n",
                   inline=True)
    return base


def standard_embed(title, text, footer=""):
    base = discord.Embed(
        title=title,
        description=text,
        colour=discord.Colour.random()

    )
    base.set_author(name="The Maw",
                    icon_url="https://64.media.tumblr.com/d304e7c08da55e86200eb6dfd715c579/792ef4b7e833ddef-7e/s500x750/3a0f98dd7e7ed403346bd85f0e59fe4c0762de52.gifv")
    base.set_footer(text=footer)
    return base


def scroll_of_summoning_embed(mtr, improved):
    if improved:
        xp_value = "| XP Doubled |"
        item_value = "| Item Guaranteed |"
    else:
        xp_value = ""
        item_value = ""

    base = discord.Embed(
        title=mtr.name,
        colour=discord.Colour.light_gray(),
        description=f"Rank: {mtr.rank}\n"
                    f"*{mtr.current_hp}/{mtr.max_hp} HP*"
    )
    base.set_thumbnail(url=mtr.link)
    base.set_author(name="Scan Complete!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name=f"Special Abilities",
                   value=
                   f"__{mtr.sp_atk['name']}__\n"
                   f"*Max Damage: {mtr.sp_atk['dmg']}*",
                   inline=False)
    base.add_field(name="...",
                   value=
                   f"**Status:**\n{', '.join(mtr.status)}\n\n"
                   f"**Max HP:**\n{mtr.max_hp}\n\n"
                   f"**Max Attack:**\n{mtr.atk}\n\n"
                   f"**Defense:**\n{mtr.defense}\n\n",
                   inline=True)
    base.add_field(name="...",
                   value=
                   f"**Initiative: **\n{mtr.initiative}\n\n"
                   f"**XP:** \n{mtr.xp} {xp_value}\n\n"
                   f"**Inventory:**\n{mtr.item} {item_value}\n\n"
                   f"**Attackers:**\n{', '.join(mtr.attacked_by)}",
                   inline=True)
    return base
#
def monster_scanner_embed(mtr):
    base = discord.Embed(
        title=mtr.name,
        colour=discord.Colour.light_gray(),
        description=f"Rank: {mtr.rank}\n"
                    f"*{mtr.current_hp}/{mtr.max_hp} HP*"
    )
    base.set_thumbnail(url=mtr.link)
    base.set_author(name="Scan Complete!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name=f"Special Abilities",
                   value=
                   f"__{mtr.sp_atk['name']}__\n"
                   f"*Max Damage: {mtr.atk}*",
                   inline=False)
    if mtr.rank == "Apex":
        base.add_field(name="Summoned",
                       value=f"Summoner: {mtr.summoner}\nSummoned: {mtr.summoned}\nDispersal: {mtr.dispersal}",
                       inline=False)
    base.add_field(name="...",
                   value=
                   f"**Status:**\n{', '.join(mtr.status)}\n\n"
                   f"**Max HP:**\n{mtr.max_hp}\n\n"
                   f"**Max Attack:**\n{mtr.atk}\n\n"
                   f"**Defense:**\n{mtr.defense}\n\n",
                   inline=True)
    base.add_field(name="...",
                   value=
                   f"**Initiative: **\n{mtr.initiative}\n\n"
                   f"**XP:** \n{mtr.xp}\n\n"
                   f"**Inventory:**\n{mtr.item}\n\n"
                   f"**Attackers:**\n{', '.join(mtr.attacked_by)}",
                   inline=True)
    return base

def dummy_monster_scanner_embed():
    base = discord.Embed(
        title="Test Dummy",
        colour=discord.Colour.light_gray(),
        description=f"Rank: 0\n"
                    f"*1 / 1 HP*"
    )
    base.set_thumbnail(url="https://cdn1.epicgames.com/ue/product/Screenshot/4-1920x1080-876ab4ec733207e2e4051d05a686f5fc.jpg?resize=1&w=1920")
    base.set_author(name="Scan Complete!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name="...",
                   value=
                   f"**Status:**\nNormal\n\n"
                   f"**Max HP:**\n1\n\n"
                   f"**Max Attack:**\n0\n\n"
                   f"**Defense:**\n0\n\n",
                   inline=True)
    base.add_field(name="...",
                   value=
                   f"**Initiative: **\n0\n\n"
                   f"**XP:** \n0\n\n"
                   f"**Inventory:**\nNone\n\n"
                   f"**Attackers:**\nNone",
                   inline=True)
    return base

def records_embed(records, hero):

    base = discord.Embed(
        title=f"__{hero.name}__",
        colour=discord.Colour.dark_magenta(),
        description=f"**Total Monsters Slain:**\n*{records['total monsters killed']}*"
    )
    base.set_thumbnail(url=hero.link)
    base.set_author(name="Tome Opened!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name="...",
                   value=
                   f"**Total Damage Done:**\n{records['total damage done']}\n\n"
                   f"**Time Spent Resting:**\n{round(records['times rested']*10/60, 1)} Hours\n\n"
                   f"**Highest Attack:**\n{records['highest damage']}\n\n"
                   f"**Items Used:**\n{records['items used']}\n\n"
                   f"**Combats Initiated:**\n{records['combats initiated']}\n\n"
                   f"**Abilities Used:**\n{records['abilities used']}\n\n"
                   f"**Keys Collected:**\n{records['keys collected']}\n\n"
                   f"**Legends Slaughtered**\n{records['legendary monsters killed']}\n\n"
                   f"**Apexes Survived**\n{records['apexes slaughtered']}\n\n",
                   inline=True)
    base.add_field(name="...",
                   value=
                   f"**Highest Raid:**\n{records['highest raid complete']}\n\n",
                   inline=True)
    return base


def fight_train_embed(title, text):
    base = discord.Embed(
        title=title,
        description=text,
        colour=discord.Colour.from_rgb(0, 250, 154)
    )
    base.set_image(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/d42d897e-b8d5-4d47-b722-e41cf"
                       "8c28943/d5o0hx4-1e29b37a-1da9-44a3-b5c9-4108415d46d4.jpg?token=eyJ0eXAiOiJKV1QiLCJhbG"
                       "ciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXN"
                       "zIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJc"
                       "L2ZcL2Q0MmQ4OTdlLWI4ZDUtNGQ0Ny1iNzIyLWU0MWNmOGMyODk0M1wvZDVvMGh4NC0xZTI5YjM3YS0xZGE5LT"
                       "Q0YTMtYjVjOS00MTA4NDE1ZDQ2ZDQuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQi"
                       "XX0.XsTK8IktCvaC8RWtlNC-6K42Lvw4s4OABxHRp3Jri2U")
    base.set_author(name="The Maw",
                    icon_url="https://64.media.tumblr.com/d304e7c08da55e86200eb6dfd715c579/792ef4b7e833ddef-"
                             "7e/s500x750/3a0f98dd7e7ed403346bd85f0e59fe4c0762de52.gifv")
    return base


def monster_list_embed(monster_object_list):
    monsters = []
    hps = []
    ranks = []
    stati = []
    max_atks = []

    legendary_string = ["None"]
    legendary_string_none_removal = False
    keys_string = ["None"]
    legendary_count = 0

    keys_count = 0

    chest_count = 0
    chest_string = []

    # Build empowered check skull stacks
    for mtr in monster_object_list:

        # Create Chest string
        if mtr.name == "Chest":
            chest_string.append(
                f"**__{mtr.name}__**\n"
                f"*Rank: {mtr.rarity}*\n"
                f"*Status: Unopened*\n"
            )
            chest_count += 1
            continue

        # Create Legendary string
        if mtr.rank == "Legendary":
            if mtr.name in mns.keys():
                shortcut = f"|{mns[mtr.name]}|\n"
            else:
                shortcut = ""
            if mtr.current_hp <= 0:
                hp_string = "Deceased"
            else:
                hp_string = f"{mtr.current_hp}/{mtr.max_hp} HP"
            legendary_count += 1
            legendary_string_none_removal = True
            legendary_string.append(
                f"**__{mtr.name}__**\n"
                f"{shortcut}*Rank:* *{mtr.rank}*\n"
                f"*Status:* *{', '.join(mtr.status)}*\n"
                f"Attack: {mtr.atk}\n"
                f"{hp_string}\n"
            )
            continue

        # Create Apex string
        elif mtr.rank == "Apex":
            if mtr.name in mns.keys():
                shortcut = f"|{mns[mtr.name]}|\n"
            else:
                shortcut = ""
            keys_count += 1
            if "None" in keys_string:
                keys_string.remove("None")
            if mtr.current_hp <= 0:
                hp_string = "Deceased"
            else:
                hp_string = f"{mtr.current_hp}/{mtr.max_hp} HP"
            keys_string.append(
                f"**__{mtr.name}__**\n"
                f"{shortcut}*Rank:* *{mtr.rank}*\n"
                f"*Status:* *{', '.join(mtr.status)}*\n"
                f"Attack: {mtr.atk}\n"
                f"{hp_string}\n"
            )
            continue

        monsters.append(mtr.name)
        if mtr.current_hp <= 0:
            hp_string = "Deceased"
        else:
            hp_string = f"{mtr.current_hp}/{mtr.max_hp} HP"
        hps.append(f"{hp_string}")
        ranks.append(mtr.rank)
        stati.append(", ".join(mtr.status))
        max_atks.append(mtr.atk)

    if legendary_string_none_removal:
        legendary_string.remove("None")

    # SORT BY RANK
    unsorted_list = [
        (monsters[i], ranks[i], stati[i], hps[i], max_atks[i])
        for i in range(len(monster_object_list) - legendary_count - keys_count - chest_count)]

    unsorted_list.sort(key=lambda x: x[1])

    print(unsorted_list)
    data_string = []
    for mon in unsorted_list:
        if mon[0] in mns.keys():
            shortcut = f"|{mns[mon[0]]}|\n"
        else:
            shortcut = ""

        data_string.append(
            f"**__{mon[0]}__**\n"
            f"{shortcut}*Rank:* *{mon[1]}*\n"
            f"*Status:* *{mon[2]}*\n"
            f"Attack: {mon[4]}\n"
            f"*{mon[3]}*\n")

    for chest in chest_string:
        random_index = random.randint(0, len(unsorted_list))
        data_string.insert(random_index, chest)

    middle_index = math.ceil(len(data_string)/2)
    final_monster_list_back = ("\n".join(data_string[:middle_index]))
    final_monster_list_front = ("\n".join(data_string[middle_index:]))
    legendary_list_string = ("\n".join(legendary_string))
    keys_list_string = ("\n".join(keys_string))

    base = discord.Embed(
        title="The Endless Maw",
        colour=discord.Colour.teal(),
    )
    if len(data_string) < 2:
        final_monster_list_front = "-"
    if len(data_string) < 1:
        final_monster_list_back = "The Maw is calm... for now"

    base.set_author(name="Roaming Monsters",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name="**Legendary**\n",
                   value=f"{legendary_list_string}\n\n",
                   inline=True)
    base.add_field(name="**Apex**\n",
                   value=f"{keys_list_string}\n\n",
                   inline=False)
    base.add_field(name=". . .",
                   value=final_monster_list_back,
                   inline=True)
    base.add_field(name=". . .",
                   value=final_monster_list_front,
                   inline=True)
    base.set_footer(text='Use .fight "monster name" to initiate a round of combat!')
    return base

def level_up_embed(hero, level_up_list):

    skills = []
    descrips = []
    for skill in hero.sp_atk:
        skills.append(hero.sp_atk[skill]["name"])
        descrips.append(hero.sp_atk[skill]["description"])

    data_string = []
    for i in range(len(skills)):
        data_string.append(f"__{skills[i]}__\n*{descrips[i]}*")
    final_ability_values = ("\n".join(data_string))

    base = discord.Embed(
        title=hero.name,
        colour=discord.Colour.orange(),
        description=f"{hero.class_} / {hero.level}\n"
                    f"*{hero.current_hp}/{hero.max_hp + hero.bonus_hp}*"
    )
    base.set_thumbnail(url=hero.link)
    base.set_author(name=f"{hero.name} is now level {hero.level}!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name=f"Special Abilities EP: {hero.current_ep}/{hero.max_ep + hero.bonus_ep}",
                   value=final_ability_values,
                   inline=False)
    base.add_field(name="...",
                   value=
                   f"**Max HP:**\n{level_up_list[1][0]} + {level_up_list[1][1]}\n\n"
                   f"**Max Attack:**\n{level_up_list[2][0]} + {level_up_list[2][1]}\n\n"
                   f"**Defense:**\n{level_up_list[3][0]} + {level_up_list[3][1]}\n\n"
                   f"**Crit:**\n{round(level_up_list[4][0], 1)} + {level_up_list[4][1]}\n\n"
                   f"**XP:**\n{hero.xp}\n\n",
                   inline=True)
    return base

def ability_card_embed(hero, ability, result):
    ability = ability.lower()
    ability_images = {
        "shieldbash": "https://i.ibb.co/2Kw2Pfw/0000.jpg",
        "assassinate": "https://storage.googleapis.com/replit/images/1550774109254_e0ab0e5878ed8276ad25151dab1b98dd.jpe",
        "helmbreaker": "https://i.ibb.co/vvpKKXC/0000.jpg",
        "spearsling": "https://i.pinimg.com/originals/1f/29/e9/1f29e9ccce057be8264bfe386e9e3282.jpg",
        "regenerate": "https://i.pinimg.com/originals/19/a9/a9/19a9a90cbbdbabb38615eebae56fc046.jpg",
        "martyr": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRt5atQcX_7QvVSEfrttzt4CLm_FlzGYTmWIInnNW_Ao8-0OsjW3QIOUgGX1HFZ6WwYUTM&usqp=CAU",
        "stalk": "https://i.pinimg.com/originals/40/36/e7/4036e70c1e663066da4c6963b14119ab.png",
        "obsecrate": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/8e318b2b-1f44-4c4b-907d-80760f47e31a/d6ndegh-6f81b26c-776a-4a37-bdf0-9c025981290c.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzhlMzE4YjJiLTFmNDQtNGM0Yi05MDdkLTgwNzYwZjQ3ZTMxYVwvZDZuZGVnaC02ZjgxYjI2Yy03NzZhLTRhMzctYmRmMC05YzAyNTk4MTI5MGMuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.qJpxD_FYamPg3kHeKVK-1O0POBBGOjObsqHdOFfhdz0",
        "executor": "https://i.pinimg.com/originals/f0/e8/6d/f0e86d352d25428b6758a0723cf1f70b.jpg",
        "intuition": "https://i.pinimg.com/originals/03/72/f4/0372f4bcdb20e4063c83341600f06ede.jpg",
        "tinker": "https://aurorabuilder.com/wp-content/uploads/2019/07/ravnica-artificer-1024x753.jpg",
        "magic missile": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLHySCY6Gf_T0YO6C2gbR3pH1QBXbvB1AH36M2vbNu03UHlhrKtmbDGkg3TLLo6F7lth4&usqp=CAU",
        "recharge": "https://www.gmbinder.com/images/kQ5rPJC.jpg",
        "battlemage": "https://i.pinimg.com/550x/b5/e0/80/b5e080f19097d3a7e6458bd7ed9dc325.jpg",
        "fireball": "https://i.pinimg.com/originals/c5/5b/34/c55b34284c78a722f47e135c6766df3a.jpg",
        "detonate": "https://64.media.tumblr.com/3e341bc0e6738f856f47602a6e308c03/tumblr_odxynbFmdh1v2b4rlo1_1280.jpg",
        "mass casualty": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQw7iQYv2_eZc4Sl5c0hApTHe3r8GYgD0-NWg&usqp=CAU",
        "transform": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZPmPRyVZBn_ZbvMM1_wLJvfmSv_eQ_a3tMA&usqp=CAU",
        "plane shift": "https://www.wallpaperbetter.com/wallpaper/82/897/93/fantasy-art-magic-sword-720P-wallpaper.jpg",
        "divinity": "https://img5.goodfon.com/wallpaper/nbig/d/74/art-game-art-angel-fantasy-wings-sword-art-angel-krylia-mech.jpg",
        "celestial consult": "https://i.pinimg.com/originals/03/53/b3/0353b3b725048b758e8c93c994aa3d77.jpg",
        "raise dead": "https://www.wallpaperflare.com/static/137/257/188/diablo-diablo-iii-video-games-fantasy-art-wallpaper-thumb.jpg",
        "sacrifice": "https://cdnb.artstation.com/p/assets/images/images/000/762/197/large/conor-burke-shaman.jpg?1432504052",
        "reanimate": "https://c4.wallpaperflare.com/wallpaper/826/238/539/digital-art-artwork-illustration-necromancer-dark-hd-wallpaper-preview.jpg",
        "legend ritual": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQDJYGRBNm3eOSkCg90qRUev89IA5LfNdu29Q&usqp=CAU",
        "predator ritual": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzRCXPO0BYMNhpdPVssUh2-wbGxMP-3JQT-CEklic5oxa8lchLkXkNvsKYQW0sJDHvDqc&usqp=CAU",
        "behemoth ritual": "https://i.pinimg.com/originals/28/73/a7/2873a70b4df118ab1437d39720bbf895.jpg",
        "apex ritual": "https://external-preview.redd.it/moOML1QLoAD3kixSMtudX6OKIEZagaf26ulMcW7qpm4.jpg?auto=webp&s=ecad717fbd93a149f2baf5ac5c1ba53d8d9186df",
        "maw oath": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBejabPkzPQwCCjoeY0EoxYski6h8ZQtajQ8UIc6pJvz_lzaZ8xY_UEAl-mciO73i9MK8&usqp=CAU",
        "cognition": "https://i.pinimg.com/originals/95/82/79/95827913b53c205da237c61f42c9372b.jpg",
        "rake claws": "https://i.pinimg.com/736x/e8/f2/4c/e8f24c0380c7bac7aa94ae60b45e9cb9.jpg",
        "become immense": "https://64.media.tumblr.com/17d11cd95a91a7cb8b0d0f7d4a8242cd/tumblr_piaxbsrvwY1sn3ne4o1_1280.jpg",
        "depraved frenzy": "https://i.pinimg.com/474x/17/bb/9b/17bb9b459a859ec3ec0fd74faee94848.jpg",
        "focus": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQALKSk30oIbhi8bSTAm3RZ8AX9IyKMRAnVog&usqp=CAU",
        "dragon kick": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/2ba1491f-5842-4307-b4e7-40a9c4f6d9bd/d972dwv-f6500d48-da7b-47c2-93d0-d10a989af22a.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzJiYTE0OTFmLTU4NDItNDMwNy1iNGU3LTQwYTljNGY2ZDliZFwvZDk3MmR3di1mNjUwMGQ0OC1kYTdiLTQ3YzItOTNkMC1kMTBhOTg5YWYyMmEuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.mBksYIoz-UWPlvvPZT_iPfloRBsJiH6WQOrAjSw_caE",
        "ki bomb": "https://i.pinimg.com/originals/b1/cf/ba/b1cfbac0d32c59aee1d23d260d025d27.jpg",
        "monastic pilgrimage": "https://i.pinimg.com/originals/ea/a9/0a/eaa90adfef41d2dc8246ad281994751d.jpg",
        "apex form": "https://i.pinimg.com/originals/bc/c4/1d/bcc41dbcd648317a834f8de9fa1d69f8.jpg"
    }

    base = discord.Embed(
        title=f"{hero.name} used {ability.title()}!",
        colour=discord.Colour.dark_green(),
        description=f"**Remaining EP:** {hero.current_ep}/{hero.max_ep + hero.bonus_ep}")
    base.set_thumbnail(url=ability_images[ability])
    base.add_field(name=ability.title(),
                   value=result,
                   inline=True)

    return base

def item_card_embed(hero_name, item, result):
    item = item.lower()
    item_images = {
        "fireball scroll": "https://i.etsystatic.com/5528056/r/il/1a22b5/235530609/il_570xN.235530609.jpg",
        "improved fireball scroll": "https://i.etsystatic.com/5528056/r/il/1a22b5/235530609/il_570xN.235530609.jpg",
        "healing potion": "https://i.pinimg.com/originals/fe/1f/fd/fe1ffd7fe2bdcdde184bc8e4adfb4620.jpg",
        "improved healing potion": "https://i.pinimg.com/originals/fe/1f/fd/fe1ffd7fe2bdcdde184bc8e4adfb4620.jpg",
        "whetstone": "https://c4.wallpaperflare.com/wallpaper/940/421/261/artwork-fantasy-art-digital-art-galaxy-wallpaper-preview.jpg",
        "improved whetstone": "https://c4.wallpaperflare.com/wallpaper/940/421/261/artwork-fantasy-art-digital-art-galaxy-wallpaper-preview.jpg",
        "energy tonic": "https://i.pinimg.com/736x/98/d2/b4/98d2b4844d62b1957067599fdc27d34f.jpg",
        "improved energy tonic": "https://i.pinimg.com/736x/98/d2/b4/98d2b4844d62b1957067599fdc27d34f.jpg",
        "blood of berserker": "https://static.tvtropes.org/pmwiki/pub/images/430218-bigthumbnail_9728.jpg",
        "improved blood of berserker": "https://static.tvtropes.org/pmwiki/pub/images/430218-bigthumbnail_9728.jpg",
        "witchbolt wand": "https://s-media-cache-ak0.pinimg.com/originals/46/76/34/467634f639c2b6dff3f1b0f3addcba4f.jpg",
        "improved witchbolt wand": "https://s-media-cache-ak0.pinimg.com/originals/46/76/34/467634f639c2b6dff3f1b0f3addcba4f.jpg",
        "blood dagger": "https://i.pinimg.com/originals/c8/ba/f6/c8baf6bf5992590db1e952dce2bd874f.jpg",
        "improved blood dagger": "https://i.pinimg.com/originals/c8/ba/f6/c8baf6bf5992590db1e952dce2bd874f.jpg",
        "tome of wisdom": "https://images.saymedia-content.com/.image/ar_1:1%2Cc_fill%2Ccs_srgb%2Cfl_progressive%2Cq_auto:eco%2Cw_1200/MTc0NDYwOTUyNTUxNTY0NjQ4/cliches-to-avoid-in-your-fantasy-novel.jpg",
        "improved tome of wisdom": "https://images.saymedia-content.com/.image/ar_1:1%2Cc_fill%2Ccs_srgb%2Cfl_progressive%2Cq_auto:eco%2Cw_1200/MTc0NDYwOTUyNTUxNTY0NjQ4/cliches-to-avoid-in-your-fantasy-novel.jpg",
        "decay bomb": "https://cdna.artstation.com/p/assets/images/images/012/278/234/medium/rainman-page-253-poison-s.jpg?1533948099",
        "improved decay bomb": "https://cdna.artstation.com/p/assets/images/images/012/278/234/medium/rainman-page-253-poison-s.jpg?1533948099",
        "gravity bomb": "https://wallpaperaccess.com/full/3879573.jpg",
        "improved gravity bomb": "https://wallpaperaccess.com/full/3879573.jpg",
        "mesmer stone": "https://ae01.alicdn.com/kf/HTB1BvGfLVXXXXXwXVXXq6xXFXXXW/226077377/HTB1BvGfLVXXXXXwXVXXq6xXFXXXW.jpg",
        "improved mesmer stone": "https://ae01.alicdn.com/kf/HTB1BvGfLVXXXXXwXVXXq6xXFXXXW/226077377/HTB1BvGfLVXXXXXwXVXXq6xXFXXXW.jpg",
        "gift of arawn": "https://cdnb.artstation.com/p/assets/images/images/030/404/035/large/zia-rasekhi-asset.jpg?1600498459",
        "improved gift of arawn": "https://cdnb.artstation.com/p/assets/images/images/030/404/035/large/zia-rasekhi-asset.jpg?1600498459",
        "sundering axe": "https://i.pinimg.com/originals/78/18/85/78188545d984b8aafd5e0d23c60e5a32.jpg",
        "improved sundering axe": "https://i.pinimg.com/originals/78/18/85/78188545d984b8aafd5e0d23c60e5a32.jpg",
        "eldritch keybox": "https://i.pinimg.com/originals/34/fc/85/34fc85fc1b539e486f78e0be986e0b13.png",
        "improved eldritch keybox": "https://i.pinimg.com/originals/34/fc/85/34fc85fc1b539e486f78e0be986e0b13.png",
        "bardic tale": "https://i.scdn.co/image/ab67706c0000bebb4a1aca3f2b64399ed51ca7e0",
        "smelling salts": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSPNwokPeXUdT_vQsFpU74Fs7KzSOIFsztDmIdFRDGM-xZyl2YxGKk8ML3qOh6oDM0Zm1g&usqp=CAU",
        "improved smelling salts": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSPNwokPeXUdT_vQsFpU74Fs7KzSOIFsztDmIdFRDGM-xZyl2YxGKk8ML3qOh6oDM0Zm1g&usqp=CAU"

    }
    base = discord.Embed(
        title=f"{hero_name} used {item.title()}!",
        colour=discord.Colour.blue(),
        description="")
    base.set_thumbnail(url=item_images[item])
    base.add_field(name="__Effect__",
                   value=result,
                   inline=True)

    return base

def character_death_embed(hero, monster):
    base = discord.Embed(
        title=f"{monster.name} has killed {hero.name}!",
        colour=discord.Colour.dark_purple(),
        description=f"**Level:** {hero.level} / **Experience:** {hero.xp + hero.ascended_xp}\n"
                    f"{hero.name} shall be added to the halls of the dead.")
    base.set_author(name="Hero Slain...",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.set_image(
        url="https://i.ytimg.com/vi/TGFeJnaS-rY/maxresdefault.jpg")

    return base


def shop_embed(shop_list, hero):
    shop = Shop()
    shop_list.sort(key=lambda x: x[1])

    tier1_string = [f"{item[0]}: {item[1]}gp" for item in shop_list if item[0] in shop.tier1_items]
    tier1 = "\n".join(tier1_string)
    if len(tier1) == 0:
        tier1 = "OUT OF STOCK"
    tier2_string = [f"{item[0]}: {item[1]}gp" for item in shop_list if item[0] in shop.tier2_items]
    tier2 = "\n".join(tier2_string)
    if len(tier2) == 0:
        tier2 = "OUT OF STOCK"
    tier3_string = [f"{item[0]}: {item[1]}gp" for item in shop_list if item[0] in shop.tier3_items]
    tier3 = "\n".join(tier3_string)
    if len(tier3) == 0:
        tier3 = "OUT OF STOCK"
    tier4_string = [f"{item[0]}: {item[1]}gp" for item in shop_list if item[0] in shop.tier4_items]
    tier4 = "\n".join(tier4_string)
    if len(tier4) == 0:
        tier4 = "OUT OF STOCK"
    armor_string = [f"{item[0]}: {item[1]}gp" for item in shop_list if item[0] in shop.armors]
    armor = "\n".join(armor_string)
    if len(armor) == 0:
        armor = "OUT OF STOCK"

    base = discord.Embed(
        title=f"__{hero.name}'s GP: {hero.gold}__",
        colour=discord.Colour.dark_green(),
    )
    base.set_thumbnail(url="https://i.pinimg.com/564x/73/5e/5d/735e5da3c5a46564cb9b3df94b785c20.jpg")
    base.set_author(name="Item Shop",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name="__Armor__",
                   value=f"{armor}\n\n**__Special__**\n{tier4}\n\n**__Rare__**\n{tier3}\n\n**__Uncommon__**\n{tier2}\n\n**__Common__**\n{tier1}\n\n**__Chance__**\nRandom Item: 1000gp\n",
                   inline=False)
    base.set_footer(text="use .purchase 'item name' to buy")
    return base

def halls_embed(halls_list):
    halls_list.sort(key=lambda x: x[2], reverse=True)
    strings = [f"**__{hero[0]} / {hero[2]}__**\n*{hero[1]}*\n*{hero[3]} xp*\n\n" for hero in halls_list]

    base = discord.Embed(
        title=f"Halls of the Dead",
        description=" ".join(strings),
        colour=discord.Colour.dark_purple(),
    )
    base.set_thumbnail(url="https://i.pinimg.com/originals/47/44/85/4744852cae8cf68b974196b0344d0f44.jpg")
    base.set_author(name="Tome Opened!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    return base

def mesmer_stone_embed(hero_name, monster, random_target, monster_damage, random_target_damage, improved):
    base = discord.Embed(
        title=f"{hero_name} used a Mesmer Stone on {monster.name}",
        description=f"*{monster.name} attacks {random_target.name}!*",
        colour=discord.Colour.dark_blue()
    )
    base.set_thumbnail(url="https://ae01.alicdn.com/kf/HTB1BvGfLVXXXXXwXVXXq6xXFXXXW/226077377/HTB1BvGfLVXXXXXwXVXXq6xXFXXXW.jpg")
    if improved:
        base.add_field(name=f"Monsters Enraged!", value="Entranced monsters attack multiplied.", inline=False)
    base.add_field(name=f'{monster.name} Combat Results',
                   value=f"*{monster.current_hp}/{monster.max_hp}* HP\n"
                         f"**Damage Roll**\n{monster_damage}\n",
                   inline=True)

    base.add_field(name=f'{random_target.name} Combat Results',
                   value=f"*{random_target.current_hp}/{random_target.max_hp}* HP\n"
                         f"**Damage Roll**\n{random_target_damage}",
                   inline=True)

    return base

def hello_embed():
    base = discord.Embed(
        title="Welcome!",
        colour=discord.Colour.blurple(),
        description="")
    base.set_thumbnail(url="https://i.pinimg.com/originals/98/d3/9c/98d39c36a79b62475219d191a8d4ea02.jpg")
    base.set_author(name="The Endless Maw",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name="Getting Started",
                   value=f"Skim through The Library channels for some information on how to play the game "
                         f"and the cover manual for basics of the gameplay structure. When you are ready, head "
                         f"over to #welcome!",
                   inline=False)
    base.add_field(name="Step 1: Create Your Hero",
                   value="First choose a class and a name for your hero. Use the command:\n"
                         ".summon_hero name class (i.e. .summon_hero Joe Fighter)\n"
                         " to summon and bind your hero. Name is whatever name you would like, but if you have a space "
                         "you will need to enclose it in quotes ('hero name'). The classes can be found in #classes. "
                         "Some classes are a bit more complex, so you will need to have some experience before using them "
                         "and cannot be picked immediately.",
                   inline=False)
    base.add_field(name="Assassin",value="Very high damage and crit scaling, low HP and Defense, starts with the "
                                         "ability 'assassinate' which has the potential to instantly kill any monster.",
                   inline=True)
    base.add_field(name="Fighter",
                   value="Midrange damage, midrange HP and Defense, starts with the ability 'helmbreaker' which reduces "
                         "a monster's armor by half of its current value.",
                   inline=True)
    base.add_field(name="Tank",value="Low damage scaling, high HP and Defense, starts with the ability 'shieldbash' which stuns a monster for a single round of combat.",inline=True)
    base.add_field(name="Cleric",value="Midrange damage, midrange HP and Defense, low crit scaling, starts with the ability 'regenerate' which heals you or an ally for 75% of their maximum health.",inline=True)
    base.add_field(name="Artificer",value="High HP, low defense and attack, high crit scaling, starts with the ability 'intuition' which can upgrade monster held items.",inline=True)

    base.add_field(name="Step 2: Set Your Image",
                   value="Find an image you like online to represent your character in-game. Copy the image address and "
                         "use the command **.set_hero_image 'url address to image'**\n"
                         "Please no rude or disruptive images.",
                   inline=False)
    base.add_field(name="Step 3: Begin",
                   value="Lastly, use the command **.begin** to start your adventure! If you have any questions, "
                         "please ask current members in #general-chat. This server is frequently updated with new "
                         "features. Please report any bugs or perceived issues to @Voodoo or within the #Bugs channel")
    base.set_footer(text="Now go kill some monsters. - Voodoo")
    return base

def gift_of_arawn_result_embed(hero):
    base = discord.Embed(
        title=f"{hero} has evaded death.",
        description="*The blessing of Arawn has faded...*",
        colour=discord.Colour.purple(),
    )
    base.set_author(name="Gift Activated!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.set_image(url="https://i.pinimg.com/originals/a5/6d/30/a56d304bf5e33553a1d9fe1f77bcc2a3.jpg")
    return base

def keys_field_embed(hero):
    base = discord.Embed(
        title=f"A Mysterious Field",
        description=f"{hero}, exasperated from a sanguinous battle with the hordes of the maw stumbles across "
                    f"a massive untouched field. Fresh grass, thickets and foliage inexplicably grow, locked within"
                    f"the desolate maw. The pursuing monsters refuse to even place a foot on this ominous meadow...",
        colour=discord.Colour.from_rgb(91, 36, 150)
    )
    base.set_image(url="https://scadconnector.com/wp-content/uploads/2019/03/Ober-J-19WIN-ILLU735-Burns-A01-DesertOasis_WEB-copy.jpg")
    return base

def keys_blood_soaked_embed(hero):
    base = discord.Embed(
        title=f"A Bloody Alter",
        description=f"As {hero} investigates the strange meadow, they locate a macabre scene behind a dense line of trees"
                    f" revealing behind it an **alter of blood**. At the base of the alter, a mortice dripping in blood calls "
                    f"to a **blood-soaked key.**",
        colour=discord.Colour.from_rgb(91, 36, 150)
    )
    base.set_image(url="https://c4.wallpaperflare.com/wallpaper/364/41/125/art-artwork-blood-fantasy-wallpaper-thumb.jpg")
    return base

def keys_tortoise_embed(hero):
    base = discord.Embed(
        title=f"A Mourning Tortoise",
        description=f"As {hero} investigates the strange meadow, they locate a shambling tortoise, eyes dead to it's surroundings, "
                    f"and endlessly trying to reach the top of a small hill. Atop the hill you see the decaying remains of "
                    f"a **tortoise shell** with a strange lock ensconced within.",
        colour=discord.Colour.from_rgb(91, 36, 150)
    )
    base.set_image(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT1w3vzrIlTq72T4c_UGiSMoMXK--RV4vw0lw&usqp=CAU")
    return base

def keys_dimensional_embed(hero):
    base = discord.Embed(
        title=f"A Shifting Plane",
        description=f"As {hero} investigates the strange meadow, they locate a thicket, obscuring an open path just beyond. "
                    f"They continue on to see the bordering grass flicker in and out of existence. Towards the end of the path, "
                    f"a strange rock pillar of swirling energy stands eerily calling out to them.",
        colour=discord.Colour.from_rgb(91, 36, 150)
    )
    base.set_image(url="https://c4.wallpaperflare.com/wallpaper/421/249/242/grass-magic-trail-rabbit-fantasy-hd-wallpaper-preview.jpg")
    return base

def keys_mountain_embed(hero):
    base = discord.Embed(
        title=f"A Lonely Golem",
        description=f"As {hero} investigates the strange meadow, they locate a an overgrown golem, frozen in time. The overgrown "
                    f"creature, with glowing eyes, appears to be grasping an altar of stone. Ensconced deep within the alter, "
                    f"{hero} spots what appears to be a key hole.",
        colour=discord.Colour.from_rgb(91, 36, 150)
    )
    base.set_image(url="https://i.pinimg.com/564x/01/53/36/015336b79d28cd1d804e105b7efc4319.jpg")
    return base

def keys_use_key_embed(hero, key):
    text_dict = {
        "Blood-Soaked Key": f"The **Blood-Soaked Key** fits into the alter with a loud crack. The ground begins to shake, "
                            f"and the air about the alter starts to crackle as the alter slowly morphs into a swirling "
                            f"portal of energy. A giant beam of energy shoots out over {hero}'s head towards the center "
                            f"of the meadow",
        "Tortoise Key": f"{hero} somberly pushes the **Tortoise Key** into the receptacle on the shell. The shell "
                        f"disintegrates around the key, leaving a single small green egg within a concealed nest. "
                        f"Like a shot a green beam of energy flashes into the sky over {hero}.",
        "Dimensional Key": f"{hero} briefly investigates the base of the swirling pylon and locates a key hole similar "
                           f"to the others. As {hero} sets the **Dimensional Key** into the altar the swirling maelstrom "
                           f"begins to grow. {hero} stumbles backwards as the maelstrom explodes into a nova and crashes "
                           f"back into the pylon, shaping a cosmic portal. Shortly after, a large beam of energy shoots "
                           f"from the portal back into the meadow.",
        "Mountain Key": f"{hero} cautiously approaches the golem and sets the **Mountain Key** into the altar. The ground "
                        f"about {hero} quakes as bits of the ancient golem fall away revealing the outline of a large "
                        f"stone pillar. As {hero} begins to gather their surroundings a streak of energy shoots forth "
                        f"from the pillar towards the center of the meadow."
    }
    image_dict = {
        "Blood-Soaked Key": "https://i.pinimg.com/736x/fa/b1/d4/fab1d42ea904856c16bd599f185e54d3.jpg",
        "Tortoise Key": "https://i.pinimg.com/originals/a1/6a/19/a16a194259fcbab1e55880ad9cbfe494.jpg",
        "Dimensional Key": "https://cdna.artstation.com/p/assets/images/images/016/598/904/large/shahab-alizadeh-time-scar-low-res.jpg?1552757959",
        "Mountain Key": "https://i.pinimg.com/736x/59/f7/15/59f7153ba4a84a4b1b13aa58085056cc---day-environment-concept.jpg"

    }
    base = discord.Embed(
        title=f"{key} Used!",
        description=text_dict[key],
        colour=discord.Colour.from_rgb(91, 36, 150)
    )
    base.set_image(url=image_dict[key])
    return base

def keys_apex_summon(hero, monster, summoned, dispersal):
    image_dict = {
        "Kraken": "http://cdn.akamai.steamstatic.com/steamcommunity/public/images/clans/23041954/e800b3a6941ad59b3c4d9bf6ef8904932154c710.png",
        "Tarrasque": "https://i.ibb.co/GTgY6by/0000.jpg",
        "Amygdalia": "https://i.pinimg.com/originals/85/eb/bf/85ebbf7a097bee8f4c76ee5f73c59fbc.jpg"
    }
    monster_image = image_dict[monster.name]

    base = discord.Embed(
        title=f"{hero.name} has summoned an Apex {monster.name}!",
        colour=discord.Colour.from_rgb(91, 36, 150),
        description=f"{monster.name} has been bound to this plane for 2 hours\nSummoned: {summoned}\nDispersal: {dispersal}"
    )
    base.set_image(url=monster_image)
    base.set_author(name="Apex Summoned!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name=f"{monster.name}",
                   value=f"Rank: {monster.rank}\n"
                    f"*{monster.current_hp} / {monster.max_hp} HP*",
                   inline=False)
    base.add_field(name=f"Special Abilities",
                   value=
                   f"__{monster.sp_atk['name']}__\n"
                   f"*Max Damage: {monster.atk}*",
                   inline=False)
    base.add_field(name="...",
                   value=
                   f"**Status:**\n{', '.join(monster.status)}\n\n"
                   f"**Max HP:**\n{monster.max_hp}\n\n"
                   f"**Max Attack:**\n{monster.atk}\n\n"
                   f"**Defense:**\n{monster.defense}\n\n",
                   inline=True)
    base.add_field(name="...",
                   value=
                   f"**Initiative: **\n{monster.initiative}\n\n"
                   f"**XP:** \n{monster.xp}\n\n"
                   f"**Inventory:**\n{monster.item}\n\n"
                   f"**Attackers:**\n{', '.join(monster.attacked_by)}",
                   inline=True)
    return base

def chest_embed(hero, rarity, contents):
    chest_image_thumbs = ["https://i.pinimg.com/originals/fc/28/16/fc281611ae7d4c726c33a96ab1f8b37d.jpg",
                          "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSAgpWaFk2YGyFAdGrhxDU21Oy-nRlh8F6aUiBRVTqsN-v8PCtML9dqzcp98zfcDZboymE&usqp=CAU",
                          "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQKdSeUbAkyeX6F23hwbJ-RtRSVYBIUTqVgMJrGUt9M3n8pp6b7FeTe495Fn03nvTq4BQk&usqp=CAU",
                          "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQnJyiqFS6VeCvtX-S-uQWO-RU26CTAAPTdU4qjuZHg5VS3uzQSPpNxyHUQG0aWetfqBSc&usqp=CAU",
                          "https://i.pinimg.com/originals/22/8c/e4/228ce48fa40df64bf4a8379994a0ae44.jpg"]
    image = random.choice(chest_image_thumbs)
    if rarity == "Common":
        contents_text = f"{contents} GP"
    else:
        contents_text = f"{contents}"

    if rarity in ["Common", "Rare"]:
        a_or_an = "a"
    else:
        a_or_an = "an"

    base = discord.Embed(
        title=f"{hero} has opened {a_or_an} {rarity} chest!",
        description=f"{contents_text} added to your inventory",
        colour=discord.Colour.greyple()
    )
    base.set_image(url=image)
    return base

def martyr_embed(tank, hero_name, dmg_martyr_taken, xp_gain):
    base = discord.Embed(
        title=f"Martyrdom",
        description=f"{tank.name} shielded {hero_name} from {dmg_martyr_taken} points of damage!\n"
                    f"{tank.name} received {xp_gain} XP",
        colour=discord.Colour.teal()
    )
    base.set_thumbnail(url=tank.link)
    return base

def new_ability_embed(hero, new_ability_dict):
    skill_name = new_ability_dict["name"]
    skill_text = new_ability_dict["text"]
    skill_descrip = new_ability_dict["description"]

    base = discord.Embed(
        title=f"{hero} unlocked a new ability!",
        description=f"**Name: {skill_name}**\nEffect: {skill_descrip}\n*{skill_text}*",
        colour=discord.Colour.blue()
    )
    base.set_author(name="New Ability!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.set_thumbnail(url="https://i.pinimg.com/originals/aa/02/d4/aa02d477025b498c0e6a462c5c156f29.gif")

    return base

def leaderboard_embed(class_, list):
    base = discord.Embed(
        title=f"{class_} Leaderboard",
        description=list,
        colour=discord.Colour.dark_purple(),
    )
    base.set_thumbnail(url="https://i.pinimg.com/originals/47/44/85/4744852cae8cf68b974196b0344d0f44.jpg")
    base.set_author(name="Maw Apex",
                    icon_url="https://phoneky.co.uk/thumbs/screensavers/down/technology/blueenergy_5wczjekw.gif")

    return base

def heroes_embed(hero_list):
    hero_strings = []
    for hero in hero_list:
        if hero.name == "Yamato":
            continue
        conc_hp = f"{hero.current_hp}/{hero.max_hp + hero.bonus_hp} HP"
        status_list = ", ".join(hero.status)
        hero_strings.append(f"**__{hero.name}__**\n{hero.class_} {hero.level}\n*{conc_hp}*\n{status_list}")

    middle_key = math.ceil(len(hero_strings) / 2)
    front = hero_strings[:middle_key]
    back = hero_strings[middle_key:]

    base = discord.Embed(
        title=f"Heroes",
        description="*Champions of the Maw*",
        colour=discord.Colour.dark_purple(),
    )
    base.add_field(name=". . .", value="\n\n".join(front), inline=True)
    base.add_field(name=". . .", value="\n\n".join(back) , inline=True)
    base.set_thumbnail(url="https://i.pinimg.com/originals/47/44/85/4744852cae8cf68b974196b0344d0f44.jpg")

    return base

def status_effect_card(affected_target, status, monster=None, damage=0):
    status_images = {
        "Bleeding": "https://wallpaper.dog/large/20421124.jpg",
        "Sharpened": "https://oldschoolroleplaying.com/wp-content/uploads/2019/06/critical-hit-four-745x1024.jpg",
        "Dazed": "https://www.desktopbackground.org/download/o/2012/04/20/377583_fantasy-mermaids-monsters-paintings-best-widescreen-backgrounds_3840x2160_h.jpg",
        "Ambiguity": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRg-3BQUSHWje0Sdv4Y8njRyIRFo4Uq2NJRA&usqp=CAU&reload=on",
        "Berserker": "https://us.v-cdn.net/5021068/uploads/attachments/1/8/4/5/2/6/20703.jpg",
        "Battle Rhythm": "https://mocah.org/uploads/posts/4520572-warrior-fantasy-art-magic.jpg",
        "Speed Rest": "https://www.tribality.com/wp-content/uploads/2018/12/90cf36ed118ba1b209dc53785d122b611.jpg",
        "Enraged": "https://cdnb.artstation.com/p/assets/images/images/034/080/747/large/jackson-richardson-142197217-240067084345193-9085932260779832507-n.jpg?1611334731",
        "Stalking": "https://i.pinimg.com/originals/6d/ce/54/6dce542ab4536f5d6add3457ca54d07d.jpg",
        "Retribution": "https://www.wallpaperflare.com/static/952/584/1007/warrior-fantasy-art-knight-holding-wallpaper.jpg",
        "Oath-Strong": "https://i.pinimg.com/736x/34/5c/e5/345ce5730322256cdedc6f5c16cdc0c2--golem-sword-art.jpg",
        "Fractured": "https://img.playbuzz.com/image/upload/ar_1.5,c_pad,f_jpg,b_auto/cdn/c97607a5-d261-48a6-865c-ef75249235e0/7c0ae9cd-4ee4-40d7-8579-ff6ff81a6821_560_420.jpg"
    }
    status_text = {
        "Bleeding": f"{affected_target} is bleeding!\n*{affected_target} has lost {damage} HP*",
        "Sharpened": f"{affected_target}'s blade slides unhindered through the {monster}",
        "Dazed": f"{affected_target} is dazed and unable to attack! Automatic critical attack!",
        "Ambiguity": f"{affected_target}'s Mantle has deflected the {monster}'s attack",
        "Berserker": f"{affected_target}'s damage doubled!",
        "Enraged Berserker": f"{affected_target}'s damage is tripled!",
        "Battle Rhythm": f"{affected_target} has spotted a weak {monster} and marked them for death!",
        "Speed Rest": f"{affected_target} has located a warm bed near a crackling fireplace.",
        "Enraged": f"{affected_target} is empowered by rage!",
        "Stalking": f"{monster} has been pulled into the shadows!",
        "Retribution": f"{affected_target} received {damage} damage in Retribution!",
        "Oath-Strong": f"{affected_target} has increased defense by {damage}!",
        "Fractured": f"{affected_target} suffers {damage} damage from their fracture!"
    }
    base = discord.Embed(
        title=f"{status} effect activated!",
        colour=discord.Colour.dark_green(),
        description=status_text[status]
    )
    base.set_thumbnail(url=status_images[status])

    return base

def battlemage_end_embed(hero, spell_broken):
    if spell_broken:
        text = f"{hero} has lost concentration by casting a spell. Battlemage buffs have ended."
    else:
        text = f"{hero} has lost concentration from a powerful hit. Battlemage buffs have ended."
    base = discord.Embed(
        title="Concentration Broken!",
        colour=discord.Colour.dark_blue(),
        description=text)
    base.set_thumbnail(url="https://qph.fs.quoracdn.net/main-qimg-964243cc5d1449e39d0baeff4b14b3cc")
    base.set_footer(text="Ciri Rule")
    return base

def art_of_war_embed(overkill_dmg, hero, cleaved_mon):
    base = discord.Embed(
        title="Art of War activated!",
        colour=discord.Colour.dark_blue(),
        description=f"{hero} killed their original target, striking a nearby {cleaved_mon} for {overkill_dmg} damage!")
    base.set_thumbnail(url="https://cdn.shopify.com/s/files/1/1323/7543/products/Zephra_-_Cleave_The_World_1024x1024.jpg?v=1563604530")
    return base

def tome_activate_embed(xp_gain, hero, monster):
    base = discord.Embed(
        title="XP Doubled!",
        colour=discord.Colour.dark_blue(),
        description=f"{hero} gained {round(xp_gain/2)} additional XP from the death of the {monster}")
    base.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS9WlkzcjUlEntRSG7RD1dLKlC1I-gGFlvdDCR00JpwoM-bJlyxPRQf0Cpsg5Pwg8Kkly8&usqp=CAU")
    return base

def raid_monster_list_embed(raid):
    unsorted_list = []

    for monster in raid.monsters:
        if monster.rank == "Legendary":
            legend = monster
            continue
        unsorted_list.append([monster, monster.rank])

    unsorted_list.sort(key=lambda x: x[1], reverse=True)
    final_list = [item[0] for item in unsorted_list]
    final_list.append(legend)

    text_string = []
    boss_string = "failed to fill boss string"

    for mtr in final_list:
        if mtr.name in mns.keys():
            shortcut = f"|{mns[mtr.name]}|"
        else:
            shortcut = ""
        mtr_string = f"**__{mtr.name}__**{shortcut}\nMaxAtk: {mtr.atk}\n{mtr.current_hp}/{mtr.max_hp} HP\n"
        if mtr.rank == "Legendary":
            boss_string = f"**__{mtr.name}__**{shortcut}\nMaxAtk: {mtr.atk}\n{mtr.current_hp}/{mtr.max_hp}\n"
            continue
        else:
            text_string.append(mtr_string)

    if not text_string:
        value = "All Variants Defeated"
    else:
        value = "\n".join(text_string)
    base = discord.Embed(
        title=f"**The Last Bastion**\n*Resistance: {raid.difficulty}*\n\n",
        colour=discord.Colour.gold(),
    )
    base.set_author(name=f"{raid.raider}'s Raid Board",
                    icon_url="https://c.tenor.com/JARCaQAiT7cAAAAC/skull.gif")
    base.add_field(name="Raid Rewards",
                   value=f"XP: {raid.xp_bank}\n"
                         f"Gold: {raid.gold_bank}\n"
                         f"Items: {', '.join(raid.item_bank)}")
    base.add_field(name="Pack Leader\n",
                    value=boss_string,
                    inline=False)
    base.add_field(name="**Variant Monsters**\n",
                   value=value,
                   inline=False)

    base.set_image(url="https://c4.wallpaperflare.com/wallpaper/675/38/512/battle-fantasy-battle-sword-fantasy-art-wallpaper-preview.jpg")
    base.set_footer(text='Use .raid "monster name" to initiate a round of combat!')
    return base

def raid_monster_death_embed(hero, xp_earned, treasure):
    if isinstance(treasure, int):
        loot = f"{treasure} GP"
    else:
        loot = treasure
    base = discord.Embed(
        title=f"__{hero.name}__",
        colour=discord.Colour.dark_gold(),
        description=f"{hero.class_} / {hero.level}\n"
                    f"*{hero.current_hp} / {hero.max_hp + hero.bonus_hp} HP*"
    )
    base.set_thumbnail(url="https://i.imgur.com/rRqTWN6.jpg")
    base.set_author(name="Raid Monster Slain!",
                    icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
    base.add_field(name=f"**XP Banked:**",
                value=f"{xp_earned}",
                inline=True)
    base.add_field(name=f"**Loot Banked:**",
                value=f"{loot}",
                inline=True)

    return base

def raid_victory_embed(hero, raid):
        items = [item for item in raid.item_bank]
        if len(items) < 1:
            items = ["None"]
        if raid.key_bank != "No Key":
            items.append(raid.key_bank)

        base = discord.Embed(
            title=f"{hero.name} has completed the level {raid.difficulty} raid!",
            colour=discord.Colour.blurple(),
            description=f"XP Reward: *{raid.xp_bank}*\n"
                        f"Gold Reward: *{raid.gold_bank}*\n"
                        f"Items Found: *{', '.join(items)}*"
            )
        base.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSR8z0pGpTplUPeHGenWX"
                               "IIyVxZUT_DVW43pMkl3RiVJIUghTxv2qDNwTk5hiFBmdt1Z1Y&usqp=CAU")
        return base

def raid_end_early(raid):
    if not raid.item_bank:
        found_items = "None"
    else:
        found_items = f"*{', '.join(raid.item_bank)}*"
    base = discord.Embed(
        title=f"{raid.raider} has abandoned the level {raid.difficulty} raid.",
        colour=discord.Colour.blurple(),
        description=f"XP Reward: *{raid.xp_bank}*\n"
                    f"Gold Reward: *{raid.gold_bank}*\n"
                    f"Items Found: {found_items}"
    )
    base.set_thumbnail(
        url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSR8z0pGpTplUPeHGenWXIIyVxZUT_"
            "DVW43pMkl3RiVJIUghTxv2qDNwTk5hiFBmdt1Z1Y&usqp=CAU")
    return base

def divine_path_embed():
    base = discord.Embed(
        title=f"Divine Path Selection",
        colour=discord.Colour.dark_teal(),
        description=f"Please select a divine path.")
    base.set_image(url="http://pm1.narvii.com/7132/0c6a5a9fd260468b2ad4bd9c987f2932b1c0bedar1-1024-768v2_uhq.jpg")
    base.add_field(name="Light Domain",
                   value="▫ Adds ability Celestial Consult, which boosts a target's XP gain on kill\n"
                         "▫ Adds XP gain on spell cast\n"
                         "▫ EP modified +2\n"
                         "▫ Attack/Def/HP reduced by 10%\n"
                         "Type **'LD'**\n\n",
                   inline=False)
    base.add_field(name="War Domain",
                   value="▫ Removes Regenerate Ability\n"
                         "▫ Increases Atk/Def/Crit/HP by 50%\n"
                         "▫ Obtain the power of God and Anime\n"
                         "Type **'WD'**",
                   inline=False)
    return base

def light_domain_xp_embed(hero_name, xp, ability):
    base = discord.Embed(
        title=f"Light Domain XP!",
        colour=discord.Colour.dark_blue(),
        description=f"{hero_name} has gained **{xp}** XP for using {ability}!")
    base.set_thumbnail(url="https://artfiles.alphacoders.com/624/62416.jpg")
    return base

def vestige_embed(send_purpose, hero, monster=None, vestige=None):
    itemability = Items()
    itemability.absolute_chance()
    item = itemability.random_item(random.choice([1, 5, 8]))

    random_sword_image = random.choice(["https://i.pinimg.com/736x/4d/71/17/4d7117bad795aea2eaca97b572ccc81f.jpg",
                                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRjhVC8n5D3hYTH0QKXq6SZXuEbivapgvrI-0Fu1_Uk8c7V-ya51p50R-tOPTYR6Q83CVU&usqp=CAU",
                                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR-4AyANWlDrtpIB-nQcywX0M9BYg6LNCntW7VEkLm9dWOe9y_2rVlTSsVrkt7evuwTJEA&usqp=CAU",
                                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSmhGb6yjh1x3IGx4RHKiHdecw8WnRegOAHdB9cANPtBD9ZFpSw_pk2-mrL7ThE9om92Ro&usqp=CAU",
                                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRdYAhevbIsRDHKLUrAancCHQBlxYRTVUXJT4bbDOinP8xEI_hF5YjNeasYYNxj_RKh904&usqp=CAU",
                                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0LQFA0OkyZlSIsHxXnIT1Vtv4JF6UPN8p5iF8fq9lMVBJGBkwvKfhPEzR20uRGtDama4&usqp=CAU",
                                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYhuuEnRGqDSFSPRi8ICqit-20q8NxUKWl2pxNPYGzj4sR5nnJWQWRhlHti7zvVg2D-rs&usqp=CAU"])
    random_loop_text = random.choice([f"I found this **{item}** as I was cutting through the last monster you swung me at...",
                                      f"You are so lucky to have me as a sword. The ROLM is actual trash.",
                                      f"Hey... you there?",
                                      f"If we could go kill some monsters that would be... just swell.",
                                      f"I've been hanging on to this {item}, my previous owner didn't use it on the Apex",
                                      f"{item} is not my favorite item, but it's free. So shut up.",
                                      f"You know if we would be actually fighting in the maw, I wouldn't have to give you all these",
                                      f"Bruh",
                                      f"Do you have a whetstone that I can borrow?",
                                      f"I used to be a mace you know. Until they reforged me. It really hurt."
                                      ])
    if send_purpose == "loop":
        item_list = [f"I found this **{item}** as I was cutting through the last monster you swung me at...",
                     f"I have given you this **{item}**. Pray I do not give you further items.",
                     f"This **{item}** seems pretty useless, like you. You can have it.",
                     f"So... I noticed you arent even level 30... use this **{item}**. Try harder.",
                     f"A casual **{item}** for a casual player",
                     f"A merchant told me this **{item}** would make me sharper, but with how blunt you are, I think "
                     f"you need it more.",
                     f"Your stat card image... needs work. Slap it with this **{item}**",
                     f"**{item}**. Shhhh. Shhhh now...",
                     f"ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn **{item}**",
                     f"YOU CAN'T HANDLE THE **{item}**",
                     f"Ah yes, a beautiful **{item}** for a beautiful lady.",
                     f"I need to see a better raid out of you. Please. **{item}**",
                     f"What is blue and also not this **{item}**. Me. Being held by you. Because I'm SAD.",
                     f"I'm bored. Blow them up with this **{item}**.",
                     f"Bro. Bro hear me out. **{item}**. **{item}** everywhere.",
                     f"Do you even remember the infinite power battlemage? You couldn't use this **{item}** or else it would "
                     f"kick you out",
                     f"bleedoop. **{item}**",
                     f"Hahahahahaha.... you thought this notification was important? Thats nice. Take this **{item}**",
                     f"Once time I fell down while slicing a monster. It really hurt my nalfesh-knee. **{item}**",
                     f"Ahem. I bestow upon you, the single greatest item in the entire game: **{item}**",
                     f"I *sword*, I put my hilt right where this **{item}** was...",
                     f"Please tell me you aren't one of those freaky knife licking people. I'm... I'm not into that. **{item}**"]
        text = random.choice(item_list)
        title = f"{item} received!"
        image = random_sword_image

        hero.inventory.append(item)

    elif send_purpose == "crit":
        text = random.choice(["I knew I was the best blade here...",
                              "Dunh Dunh Dunh, another one bites the dust",
                              f"Don't take it personally {monster}, I'm just sharper than you",
                              "What a hack. Get it? Hey do you get it?",
                              "How about we fight monsters at your rank eh?",
                              "Oh gods... there is blood everywhere...",
                              "Wait... this one bleeds purple. Neat.",
                              "Oh boy, I do love whetstones. Way better than dry stones.",
                              "Oh... I went right through its ankles. I guess it's been... de-feeted",
                              "No im not a honedge. I don't even know what that is.",
                              "Oh my...",
                              "One day I want to find myself a nice broadsword.",
                              "My name is Inigo Mo... wait",
                              "Swath... great word. I cut swaths."])
        title = f"Vestige Blade"
        image = random_sword_image

    elif send_purpose == "equip":
        text = f"*|Why hello there beautiful.|*\n\n" \
               f"**Attack**:\n{hero.atk + hero.bonus_atk} + {vestige.atk_mod}\n" \
               f"**Defense**:\n{hero.defense + hero.bonus_def} + {vestige.def_mod}\n" \
               f"**Crit**:\n{hero.crit_multiplier + hero.bonus_crit} + {vestige.crit_mod}\n" \
               f"**Max HP**:\n{hero.max_hp + hero.bonus_hp} + {vestige.hp_mod}\n" \
               f"**Max EP**:\n{hero.max_ep + hero.bonus_ep} + {vestige.ep_mod}\n\n" \
               f"**Spirit Trace** status added!\n" \
               f"*Vestige routinely rewards items... and wont shut up.*"
        title = "Vestige the Living Blade equipped!"
        image = random_sword_image

    elif send_purpose == "unequip":
        text = f"Was I good? Please don't go."
        title = "Vestige the living blade unequipped!"
        image = random_sword_image

    else:
        text = f"Well look what I found..."
        title = f"**{item}** received!"
        image = random_sword_image

        hero.inventory.append(item)

    base = discord.Embed(
        title=title,
        colour=discord.Colour.teal(),
        description=text)
    base.set_thumbnail(url=image)
    return base

def dark_druid_ritual_embed(result):
    url = "https://i.pinimg.com/474x/72/c9/60/72c9606c8577ddeddf551d5772535fda.jpg"
    if result[2] == "Apex":
        url = "https://i.pinimg.com/474x/11/07/3c/11073ce7ceb3ad29a30448fc9942f929--character-concept-concept-art.jpg"
    if result[2] == "Legend":
        url = "https://i.pinimg.com/236x/60/4d/ad/604dad1fcd7b652b10422bf8d085114a.jpg"
    if result[2] == "Behemoth":
        url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRYAfAbm_vY6gAfg0l030I2r2Yo2jQFMO5Alg&usqp=CAU"
    if result[2] == "Predator":
        url = "https://i.pinimg.com/474x/72/c9/60/72c9606c8577ddeddf551d5772535fda.jpg"

    base = discord.Embed(
        title=f"Aspect Unlocked",
        colour=discord.Colour.teal(),
        description=result)
    base.set_thumbnail(url=url)
    return base

def sell_embed(item, value, item_tier):
    if item_tier == 5:
        text = f"Unbelievable that a hero would part with such a treasure! I'll gladly take it!"
    elif item_tier == 4:
        text = f"Wait... didn't I sell you this? I suppose I can accept a return."
    elif item_tier == 3:
        text = f"Now that is pretty rare... I'll buy it at a high price."
    elif item_tier == 2:
        text = "I have quite a few of these... I can't pay much for it."
    else:
        text = "Pawning your trash eh? Here is your money."

    base = discord.Embed(
        title=f"{item} sold for {value} gp!",
        colour=discord.Colour.gold(),
        description=f"*{text}*")
    base.set_thumbnail(url="https://i.pinimg.com/originals/fe/27/00/fe27005160ddf885205ec3466cede702.jpg")
    return base


def armor_embed(armor, hero):
    arm_def = hero.armor_defense_bonus
    arm_atk = hero.armor_attack_detriment
    arm_crit = hero.armor_crit_detriment
    arm_ep = hero.armor_bonus_ep

    armor_dict = {
        "Cloth Armor": f"**EP**:\n{hero.max_ep + hero.bonus_ep - arm_ep} + {arm_ep}",
        "Leather Armor": f"**EP**:\n{hero.max_ep + hero.bonus_ep - arm_ep} + {arm_ep}\n"
                         f"**Defense**:\n{hero.defense + hero.bonus_def - arm_def} + {arm_def}",
        "Mail Armor": f"**Defense**:\n{hero.defense + hero.bonus_def - arm_def} + {arm_def}",
        "Plate Armor": f"**Defense**:\n{hero.defense + hero.bonus_def - arm_def} + {arm_def}\n"
                       f"**Attack**:\n{hero.atk + hero.bonus_atk + abs(arm_atk)} - {abs(arm_atk)}\n"
                       f"**Critical**:\n{hero.crit_multiplier + hero.bonus_crit + abs(arm_crit)} - {abs(arm_crit)}",
        "Bag Of Holding": "**Organized** status added!\n"
                          "*Inventory capacity expanded by 5*"
    }

    armor_images = {
        "Cloth Armor": "https://db4sgowjqfwig.cloudfront.net/campaigns/96912/assets/431797/PlainClothes.png?1425301763",
        "Leather Armor": "https://static.wikia.nocookie.net/forgottenrealms/images/8/85/StuddedLeather-5e.png/revision/latest?cb=20200628135121",
        "Mail Armor": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSn8R3rHgm0gz1v-BEoZBkFgdqJ4NI6egRZwkPmjJpe9a5v9ejzt0wZVIKgtWC0SWjftKk&usqp=CAU",
        "Plate Armor": "https://static.wikia.nocookie.net/sharra/images/e/e1/Dusk_Half_Plate.jpg/revision/latest/top-crop/width/360/height/450?cb=20190426070748",
        "Bag Of Holding": "https://www.epicpath.org/images/thumb/b/bc/Slotless_1.jpg/395px-Slotless_1.jpg"
    }
    base = discord.Embed(
        title=f"{hero.name} has equipped {armor}!",
        colour=discord.Colour.darker_grey(),
        description=armor_dict[armor])
    base.set_author(name="Armor Equipped!",
                    icon_url="https://cdn.dribbble.com/users/2497355/screenshots/4993977/shield_motion_icon.gif")
    base.set_thumbnail(url=f"{armor_images[armor]}")
    return base

def rolm_embed(equip_object, hero, mode):
    mode = mode.lower()

    image_dict = {
        "battleaxe": "https://preview.redd.it/ddrpbj2gy7zz.jpg?auto=webp&s=76116ae3479f3ba0aec2bc67ae1e679e866e6098",
        "spear": "https://www.nicepng.com/png/detail/237-2370305_06infinitystormer-gorgeous-spear-weapon-magic.png",
        "barrier": "https://i.pinimg.com/474x/4d/d3/bf/4dd3bffd901174f4bcce32ff34bc696b.jpg"
    }

    text_dict = {
        "battleaxe": f"**Attack**:\n{hero.atk + hero.bonus_atk} + {equip_object.atk_mod}\n"
                     f"**Defense**:\n{hero.defense + hero.bonus_def} + {equip_object.def_mod}\n"
                     f"**Crit**:\n{hero.crit_multiplier + hero.bonus_crit} + {equip_object.crit_mod}\n"
                     f"**Mode**:\nBattleaxe\n\n"
                     f"Special Ability **Transform** added!",
        "spear": f"**Attack**:\n{hero.atk + hero.bonus_atk} + {equip_object.atk_mod}\n"
                 f"**Crit**:\n{hero.crit_multiplier + hero.bonus_crit} + {equip_object.crit_mod}\n"
                 f"**Mode**:\nSpear\n\n"
                 f"Special Ability **Spearsling** added!\n"
                 f"Special Ability **Transform** added!",
        "barrier": f"**Attack**:\n{hero.atk + hero.bonus_atk} + {equip_object.atk_mod}\n"
                   f"**Defense**:\n{hero.defense + hero.bonus_def} + {equip_object.def_mod}\n"
                   f"**Max HP**:\n{hero.max_hp + hero.bonus_hp} + {equip_object.hp_mod}\n"
                   f"**Crit**:\n{hero.crit_multiplier + hero.bonus_crit} + {equip_object.crit_mod}\n"
                   f"**Max EP**:\n{hero.max_ep + hero.bonus_ep} + {equip_object.ep_mod}\n"
                   f"**Mode**:\nBarrier\n\n"
                   f"Special Ability **Transform** added"
    }

    base = discord.Embed(
        title=f"ROLM: God's {mode.title()}!",
        colour=discord.Colour.gold(),
        description=text_dict[mode])
    base.set_author(name="Legendary Equipped!",
                    icon_url="https://c.tenor.com/aHgPPTK73_AAAAAM/crystal-diamond.gif")
    base.set_thumbnail(url=f"{image_dict[mode]}")
    print(image_dict[mode])
    return base

def chidori_embed(chidori, hero):
    base = discord.Embed(
        title=f"Chidori",
        colour=discord.Colour.gold(),
        description=f"**Attack**:\n{hero.atk + hero.bonus_atk} + {chidori.atk_mod}\n"
                    f"**Defense**:\n{hero.defense + hero.bonus_def} - {abs(chidori.def_mod)}\n"
                    f"**Max HP**:\n{hero.max_hp + hero.bonus_hp} - {abs(chidori.hp_mod)}\n\n"
                    f"**Flash** status added!\n"
                    f"*{hero.name}'s attacks are faster than light.*")
    base.set_author(name="Legendary Equipped!",
                    icon_url="https://c.tenor.com/aHgPPTK73_AAAAAM/crystal-diamond.gif")
    base.set_thumbnail(
        url="https://www.wallpaperup.com/uploads/wallpapers/2015/10/18/820570/f7cb652033115b2aceba8d099e5ea0fe-700.jpg")
    return base

def forbidden_fruit_embed(forb_fruit, hero):
    base = discord.Embed(
        title=f"Forbidden Fruit",
        colour=discord.Colour.gold(),
        description=f"**Defense**:\n{hero.defense + hero.bonus_def} + {forb_fruit.def_mod}\n"
                    f"**Max HP**:\n{hero.max_hp + hero.bonus_hp} + {forb_fruit.hp_mod}\n\n"
                    f"**Vital Tree** status added!\n"
                    f"*{hero.name} feels an overwhelmingly healthy.*")
    base.set_author(name="Legendary Equipped!",
                    icon_url="https://c.tenor.com/aHgPPTK73_AAAAAM/crystal-diamond.gif")
    base.set_thumbnail(
        url="https://i.pinimg.com/originals/41/9e/8a/419e8a0b1abccc33ea202726866b5b47.jpg")
    return base


def ytk_embed(ytk, hero):
    base = discord.Embed(
        title=f"Yamato's Training Katana",
        colour=discord.Colour.gold(),
        description=f"**Attack**:\n{hero.atk + hero.bonus_atk} + {ytk.atk_mod}\n"
                    f"**Crit**:\n{hero.crit_multiplier + hero.bonus_crit} + {ytk.crit_mod}\n\n"
                    f"Special Ability **Focus** added!")
    base.set_author(name="Legendary Equipped!",
                    icon_url="https://c.tenor.com/aHgPPTK73_AAAAAM/crystal-diamond.gif")
    base.set_thumbnail(
        url="https://media.gettyimages.com/photos/mixed-race-woman-wielding-sword-in-kimono-picture-id494323153?s=612x612")
    return base


def natures_mantle_embed(nm, hero):
    base = discord.Embed(
        title=f"Nature's Mantle",
        colour=discord.Colour.gold(),
        description=f"**Attack**:\n{hero.atk + hero.bonus_atk} + {nm.atk_mod}\n"
                    f"**Defense**:\n{hero.defense + hero.bonus_def} + {nm.def_mod}\n"
                    f"**Crit**:\n{hero.crit_multiplier + hero.bonus_crit} + {nm.crit_mod}\n"
                    f"**Max HP**:\n{hero.max_hp + hero.bonus_hp} + {nm.hp_mod}\n"
                    f"**Max EP**:\n{hero.max_ep + hero.bonus_ep} + {nm.ep_mod}\n\n"
                    f"**Ambiguity** status added!\n"
                    f"*{hero.name} is invisible!*")
    base.set_author(name="Legendary Equipped!",
                    icon_url="https://c.tenor.com/aHgPPTK73_AAAAAM/crystal-diamond.gif")
    base.set_thumbnail(
        url="http://coolvibe.com/wp-content/uploads/2013/02/Fantasy-Art-david-s.-hong-Grin-At-You.jpg")
    return base


def ki_bomb_result_embed(exploding_monster, struck_monster_list, damage_done):
    base = discord.Embed(
        title=f"Ki Bomb Detonated!",
        colour=discord.Colour.gold(),
        description=f"{exploding_monster} **exploded** on death for **{damage_done}** damage!\n"
                    f"**Monsters Struck**: {', '.join([mon.name for mon in struck_monster_list])}")
    base.set_thumbnail(
        url="https://i.pinimg.com/originals/29/0d/b1/290db1f5a728a5fecac38d328e2ffc05.jpg")
    return base

def apex_status_embed(status_effect, status_result):
    status_image_dict = {
        "Silencer": "https://static.wikia.nocookie.net/monster/images/5/56/Psyker.png/revision/latest?cb=20200329065437",
        "Barbed": "https://static2.mtgarena.pro/mtg/pict/spikefield-hazard-znr-166-art-mtga.png",
        "Drainer": "https://i.pinimg.com/originals/f9/e6/e4/f9e6e4944674ed0fd24ee222c2980d08.jpg",
        "Absorbing": "https://i.pinimg.com/736x/8e/b2/41/8eb2419af80b03a33dd361dbdf0fcd05.jpg",
        "Caustic": "http://corwyn.wdfiles.com/local--files/steaming-marsh/MISTY%20SWAMP.jpg",
        "Breaker": "https://wallup.net/wp-content/uploads/2018/09/29/697629-diant-monster-creature-fantasy-ar-artwork.jpg"
    }

    base = discord.Embed(
        title=f"Aura of the Meadow",
        colour=discord.Colour.dark_blue(),
        description=status_result)
    base.set_thumbnail(url=status_image_dict[status_effect])
    base.set_author(name="Apex Aura!",
                    icon_url="https://c.tenor.com/hOF1YZDv6dcAAAAC/fire-gif.gif")
    return base

def apex_aura_embed(aura_effect):
    status_image_dict = {
        "Silencer": "https://i.pinimg.com/originals/ea/34/53/ea3453b199f84ee063386c49d83024f2.jpg",
        "Barbed": "https://artfiles.alphacoders.com/622/thumb-1920-62250.gif",
        "Drainer": "https://i.pinimg.com/originals/f7/1f/06/f71f06c23ed81ce174c52f33607509c6.jpg",
        "Absorbing": "https://i.pinimg.com/originals/10/1d/96/101d96db62c905277325accfe650a0d1.jpg",
        "Caustic": "https://i.pinimg.com/originals/3f/1a/22/3f1a229d4e54668c17e7e3ff6324c23b.jpg",
        "Breaker": "https://i.pinimg.com/originals/d2/81/f9/d281f9a375de83de3884fc5df12bb1c2.jpg"
    }
    text_dict = {
        "Silencer": "A hush befalls the meadow amidst the Apex. You feel a creeping amnesia... Fighting "
                    "the Apex will result in the temporary loss of an ability.",
        "Barbed": "The meadow surrounding the Apex evolves from a lush green field to a dessicated and " \
                  "violent thistle infested brush. Attacking the Apex will cause your hero to suffer damage.",
        "Drainer": "The Apex drains your energy while you remain in the meadow. When you fight "
                   "the Apex, your max EP will reduce by 1. At 0 max EP your life will drain significantly",
        "Absorbing": "The Apex absorbs life through the Meadow. Every round of combat empowers the Apex.",
        "Caustic": "The Meadow surrounding the Apex evolvs from a lush green field to an acidic "
                   "hellscape. Fighting in the Meadow reduces armor by half and destroys any equipped armor.",
        "Breaker": "The Apex attacks are as destructive as the Maw itself, shattering your body "
                   "on each hit. Critical strikes will now do 0 damage and hurt your hero from internal "
                   "damage."
    }
    base = discord.Embed(
        title=f"{aura_effect} Effect",
        colour=discord.Colour.dark_blue(),
        description=text_dict[aura_effect])
    base.set_thumbnail(url=status_image_dict[aura_effect])
    base.set_author(name="Apex Aura!",
                    icon_url="https://c.tenor.com/hOF1YZDv6dcAAAAC/fire-gif.gif")
    return base