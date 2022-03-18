import platform
import pickle

from staticfunctions import *
from embeds import *
from fight import Fight

import os
from leaderboard import Leaderboard
from shop import Shop
from herobuilder import HeroBuilder
from monsterbuilder import MonsterBuilder, Chest, Raid
from discord.ext import tasks
from discord.ext.commands import Bot
from asyncio import sleep, TimeoutError
from datetime import datetime, timedelta
from equipment import Legendary, Armors
from items import Items

# Create shortcut variables
with open("config.json") as file:
    config = json.load(file)
with open("shortcuts/monster_shortcuts.json", "r") as file:
    moncuts_dict = json.load(file)
    moncuts = list(moncuts_dict.keys())
with open("shortcuts/monster_shortcuts_swapped.json", "r") as file:
    mss = json.load(file)
with open("shortcuts/item_shortcuts.json", "r") as file:
    itemcuts_dict = json.load(file)
    itemcuts = list(itemcuts_dict.keys())
with open("shortcuts/ability_shortcuts.json", "r") as file:
    abilicuts_dict = json.load(file)
    abilicuts = list(abilicuts_dict.keys())
with open("shortcuts/permanent_shortcuts.json", "r") as file:
    permacuts_dict = json.load(file)
    permacuts = list(permacuts_dict.keys())
with open("shortcuts/item_shortcuts_swapped.json", "r") as file:
    iss = json.load(file)

# Token collection, bot object creation
intents = discord.Intents.all()
client = discord.Client()
bot = Bot(command_prefix=config["bot_prefix"], help_command=None, intents=intents)


def build_leaderboard():
    """Write leaderboard to memory from pickle file if present, or new if not"""
    try:
        with open("leaderboards/leaderboard.pickle", "rb") as f:
            data = pickle.load(f)
        LEADERBOARD = data

    except FileNotFoundError:
        LEADERBOARD = Leaderboard()

    return LEADERBOARD


# Global Variables
MONSTER_LIST = []
MONSTER_LIST2 = []
MONSTER_LIST3 = []
MASTER_RAID_DICT = {}
HERO_LIST = []
HERO_NAME_LIST = []
GLOBAL_STATUS_DICT = {}
LEADERBOARD = build_leaderboard()
SHOP = [["thing", "cost"]]

# Channels
welcome = 0
beyond_the_gates = 0
beyond_the_battlefield = 0
heart_of_the_maw = 0
the_meadow = 0
general_chat = 0
the_shop = 0
admin = 0
testing_home = 0
test_server = 0
raid_1 = 0
raid_2 = 0
raid_3 = 0
bugs = 0
mixed_leaderboard = 0
class_leaderboard = 0
ideas_features = 0
classes = 0

# Admin
admin = 0

# Initialize functions _________________________________________________________________________________________________


def fix_resting():  # Fix resting heroes for server resets during gameplay
    """Completes a resting cycle for heroes resting during bot reset"""
    for hero in HERO_LIST:
        if hero.resting == "Resting":
            if "Immense" in hero.status:
                hero.status.remove("Immense")
                hero.bonus_hp -= hero.immense_hp
                delattr(hero, "immense_hp")

            hero.current_ep = hero.max_ep + hero.bonus_ep
            hero.current_hp = hero.max_hp + hero.bonus_hp

            hero.resting = "Not Resting"
            delattr(hero, "alarm_clock")
            return


def build_hero_list():
    """Builds hero objects from saved files and appends to HERO_LIST"""
    for filename in os.listdir("characters"):
        with open(f"characters/{filename}", "r") as f:
            data = json.load(f)

        hero = HeroBuilder()
        hero.__dict__ = data
        print(hero.name)
        HERO_LIST.append(hero)
        HERO_NAME_LIST.append(hero.name)


def build_raids():
    """Builds raid objects from saved files and adds them to MASTER_RAID_DICT"""
    for filename in os.listdir("raids"):
        raid_name = filename.split(".")[0]

        with open(f"raids/{filename}", "rb") as f:
            data = pickle.load(f)

        MASTER_RAID_DICT[raid_name] = data


@bot.event  # The code in this event is executed when the bot is ready
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()
    fill_maw_continuous.start()
    shop_update.start()
    build_hero_list()
    build_leaderboard()
    build_raids()
    save_data.start()
    apex_check.start()
    vestige_perm_dms.start()
    raid_leaderboard_update.start(LEADERBOARD)
    add_martyr.start()
    fix_resting()


# LOOPS ____________________________________________________________________________________________________
# Setup the game status task of the bot

@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """Rotates status for bot in Discord"""
    statuses = ["Slaughtering Heroes", "Producing Demons", f"{config['bot_prefix']}help", "MonsterBot"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


@tasks.loop(minutes=0.15)
async def fill_maw_continuous() -> None:
    """Fills monster lists with monster objects for each rank"""
    global MONSTER_LIST, MONSTER_LIST2, MONSTER_LIST3

    def new_monster(rank):
        return MonsterBuilder(rank)

    for mon_list in [MONSTER_LIST, MONSTER_LIST2, MONSTER_LIST3]:
        ranks = [mon.rank for mon in mon_list]
        names = [mon.name for mon in mon_list]

        standard_list = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8]

        for idx, value in enumerate(ranks):
            if value == "Legendary":
                ranks[idx] = 9
            elif value == "Apex":
                ranks[idx] = 10
            elif value == "Chest":
                ranks[idx] = 11

        for rank in ranks:
            if rank in standard_list:
                standard_list.remove(rank)

        for rank in standard_list:
            monster = new_monster(rank)
            if monster.name in names:
                monster.name = f"Empowered {monster.name}"
                monster.empower()
                mon_list.append(monster)
            else:
                mon_list.append(monster)
                names.append(monster.name)

        if 9 not in ranks:
            for _ in range(2):
                chance = random.randint(1, 75)
                if chance == 1:
                    monster = new_monster("Legendary")
                    if monster.name in names:
                        pass
                    else:
                        mon_list.append(monster)

        if 11 not in ranks:
            chance = random.randint(1, 50)
            if chance == 1:
                new_chest = Chest()
                mon_list.append(new_chest)

        non_numerical_ranks = [mtr for mtr in mon_list if mtr.rank in ["Legendary", "Apex", "Chest"]]
        [mon_list.remove(non_num) for non_num in non_numerical_ranks]
        mon_list.sort(key=lambda x: x.rank)
        mon_list.extend(non_numerical_ranks)


@tasks.loop(minutes=5)
async def add_martyr() -> None:
    """Adds Martyr status to GLOBAL_STATUS_DICT for activation"""
    for hero in HERO_LIST:
        if "Martyr" in list(hero.sp_atk.keys()):
            GLOBAL_STATUS_DICT.update({hero: "Martyr"})

@tasks.loop(minutes=5)
async def save_data() -> None:
    """Saves hero data, raid data, and leaderboards to file"""
    for hero in HERO_LIST:
        with open(f"characters/{hero.name}.json", "w") as f:
            json.dump(hero.__dict__, f, indent=2)

    for raid in MASTER_RAID_DICT:
        with open(f"raids/{MASTER_RAID_DICT[raid].raider}.pickle", "wb") as f:
            pickle.dump(MASTER_RAID_DICT[raid], f)

    with open("leaderboards/leaderboard.pickle", "wb") as f:
        pickle.dump(LEADERBOARD, f)


@tasks.loop(minutes=15)
async def raid_leaderboard_update(leaderboard) -> None:
    """Updates the leaderboard embeds in class and mixed leaderboard channels"""
    channel = bot.get_channel(class_leaderboard)
    await channel.purge(limit=10)

    if leaderboard.tank_leaders:
        tank_string = [f"{tank[0]}........{tank[1]}" for tank in leaderboard.tank_leaders]
        tank_string.reverse()
        await channel.send(embed=leaderboard_embed("Tank", "\n".join(tank_string)))
    if leaderboard.fighter_leaders:
        fighter_string = [f"{fighter[0]}........{fighter[1]}" for fighter in leaderboard.fighter_leaders]
        fighter_string.reverse()
        await channel.send(embed=leaderboard_embed("Fighter", "\n".join(fighter_string)))
    if leaderboard.assassin_leaders:
        assassin_string = [f"{assassin[0]}........{assassin[1]}" for assassin in leaderboard.assassin_leaders]
        assassin_string.reverse()
        await channel.send(embed=leaderboard_embed("Assassin", "\n".join(assassin_string)))
    if leaderboard.mage_leaders:
        mage_string = [f"{mage[0]}........{mage[1]}" for mage in leaderboard.mage_leaders]
        mage_string.reverse()
        await channel.send(embed=leaderboard_embed("Mage", "\n".join(mage_string)))
    if leaderboard.artificer_leaders:
        art_string = [f"{art[0]}........{art[1]}" for art in leaderboard.artificer_leaders]
        art_string.reverse()
        await channel.send(embed=leaderboard_embed("Artificer", "\n".join(art_string)))
    if leaderboard.monk_leaders:
        monk_string = [f"{monk[0]}........{monk[1]}" for monk in leaderboard.monk_leaders]
        monk_string.reverse()
        await channel.send(embed=leaderboard_embed("Monk", "\n".join(monk_string)))
    if leaderboard.dark_druid_leaders:
        dd_string = [f"{druid[0]}........{druid[1]}" for druid in leaderboard.tank_leaders]
        dd_string.reverse()
        await channel.send(embed=leaderboard_embed("Dark Druid", "\n".join(dd_string)))
    if leaderboard.cleric_leaders:
        cleric_string = [f"{cleric[0]}........{cleric[1]}" for cleric in leaderboard.cleric_leaders]
        cleric_string.reverse()
        await channel.send(embed=leaderboard_embed("Cleric", "\n".join(cleric_string)))

    channel = bot.get_channel(mixed_leaderboard)
    await channel.purge(limit=2)

    mixed_string = [f"{char[0]}, {char[2]}........{char[1]}" for char in leaderboard.leaders]
    mixed_string.reverse()
    compiled_string = "\n".join(mixed_string)
    if compiled_string:
        await channel.send(embed=leaderboard_embed("Mixed", compiled_string))


@tasks.loop(minutes=30)
async def shop_update() -> None:
    """Updates shop items"""
    global SHOP
    shop_object = Shop()
    for_sale_list = shop_object.shop_items()
    SHOP = shop_object.set_cost(for_sale_list)


@tasks.loop(minutes=60)
async def vestige_perm_dms() -> None:
    """Sends item gift notifications to individuals equipped with Vestige Blade"""
    for hero in HERO_LIST:
        if "Spirit Trace" in hero.status:
            if len(hero.inventory) < 10 or len(hero.inventory) < 15 and "Organized" in hero.status:
                member = bot.get_user(hero.owner)
                await member.send(embed=vestige_embed("loop", hero))


@tasks.loop(minutes=3)
async def apex_check() -> None:
    """Removes Apex monster if 2 hours from summoned time"""
    t_format = "%b %d %Y at %I:%M%p"
    for monster in MONSTER_LIST:
        if monster.rank == "Apex":
            channel = bot.get_channel(the_meadow)

            # get hours
            dispersal = monster.dispersal
            dispersal_datetime = datetime.strptime(dispersal, t_format)
            if datetime.now() > dispersal_datetime:
                for character in monster.attacked_by:
                    character = get_hero(HERO_LIST, character)
                    apex_status_cure(character, monster.aura)
                await channel.send(block_text(f"The {monster.name} has left this plane"))
                MONSTER_LIST.remove(monster)


# # EVENTS ____________________________________________________________________________________________________

@bot.event
async def on_message(message):
    """Ignore Bot Messages"""
    # Ignores if a command is being executed by a bot or by the bot itself
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    """Set training channel and ping new users for training"""
    # Second join message in welcome channel and ping user to training channel
    welcome_channel = bot.get_channel(id=welcome)
    await welcome_channel.send(f"Hello {member.mention}! Welcome to The Endless Maw! "
                               f"We have set up a beginner channel just for you!"
                               )

    # Create role for specific user and assign it to user
    guild = member.guild
    role_name = f"Fledgling {member.name}"
    await guild.create_role(name=role_name)

    role = discord.utils.get(guild.roles, name=role_name)
    await member.add_roles(role)

    def standard_embed(title, text):
        base = discord.Embed(
            title=title,
            description=text,
            colour=discord.Colour.from_rgb(0, 250, 154)
        )
        return base

    # Set variable for channel name
    training_channel_name = f"{member.name.lower()}-training"

    # Get category to create new text channel
    category = discord.utils.get(guild.categories, id=919038033972572170)

    # Create a text channel named after new member
    await guild.create_text_channel(training_channel_name, category=category)
    await sleep(2)
    # Get channel object
    channel = discord.utils.get(guild.channels, name=training_channel_name)

    # Set permissions in channel for new role
    await channel.set_permissions(role, send_messages=True, view_channel=True)

    # Send message
    await channel.send(
        embed=standard_embed(
            title="Getting Started",
            text=f"Hello {member.mention}... Welcome to The Endless Maw! I am here to "
                 f"show you the ropes so you don't get lost, or worse, killed. This is "
                 f"your private channel, so it's just you and me!\n\n"
                 f"First off, type the command: **.train**"
        )
    )


@bot.command(aliases=["arm"])
async def armory(ctx, target="None"):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:

        hero_name = set_hero_user(ctx.message.author.id)

        if target == "None":
            hero = get_hero(HERO_LIST, hero_name)
        else:
            if target.title() in HERO_NAME_LIST:
                hero = get_hero(HERO_LIST, target.title())
            else:
                await ctx.send(block_text(f"{target.title()} is not on the Hero List"))
                return

        armory = ", ".join(hero.armory)
        await ctx.send(block_text(f"{hero_name}'s Armory:\n{armory}"))


@bot.command(aliases=["asc"])
async def ascension(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:

        user_id = ctx.message.author.id
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if hero.level < 15:
            await ctx.send(block_text(f"{hero.name} must be level 15 before they can ascend."))
            return

        await ctx.send(
            f"```Ascending {hero.name} will reset your stats back to level 1, re-roll them to a selected class"
            f", and mark {hero.name} as ascended. Ascending at level 25 will provide a special badge in your "
            f"ascension stat. Leaderboard XP will continue to count up, "
            f"however hero xp will reset.\nPlease type your hero name to proceed.```")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and \
                   msg.content.lower() == hero.name.lower()

        try:
            await bot.wait_for("message", check=check, timeout=45)
        except TimeoutError:
            await ctx.send(block_text("Ascension awaits"))
            return

        await ctx.send(block_text(f"What class would you like to roll for {hero.name}?"))

        def check_class(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and \
                   msg.content.lower() in ["mage", "cleric", "fighter", "tank", "assassin", "artificer", "dark druid",
                                           "monk"]

        try:
            msg = await bot.wait_for("message", check=check_class, timeout=45)
        except TimeoutError:
            await ctx.send(block_text("Ascension awaits"))
            return

        if msg.content.lower() == "dark druid" and len(hero.ascended_classes) < 3:
            await ctx.send(code_block("You may not ascend to the dark druid class until "
                                      "you have spent sufficient time in the Maw (ascended at least 3 times)"))
            return

        roll_class = msg.content

        # Save data for new hero
        asc_xp = hero.xp + hero.ascended_xp
        asc_class = hero.class_
        asc_classes = hero.ascended_classes
        asc_ascensions = hero.ascensions

        # Create new hero object
        new_hero = HeroBuilder()
        new_hero.new_class_set(roll_class, hero.name, hero.owner)

        # Set new hero information
        new_hero.ascended_xp = asc_xp
        new_hero.ascended_classes.extend(asc_classes)
        new_hero.ascensions = hero.ascensions + 1

        if asc_class in new_hero.ascended_classes:
            pass
        else:
            if hero.level > 24:
                new_hero.ascended_classes.append(asc_class)

        new_hero.ascended = True
        new_hero.link = hero.link

        HERO_LIST.remove(hero)
        HERO_LIST.append(new_hero)
        await ctx.send(embed=stat_embed(new_hero))


@bot.command(aliases=["er"])
async def end_raid(ctx):
    if ctx.channel.id in [raid_1, raid_2, raid_3, testing_home]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        raid = get_raid(hero.name, MASTER_RAID_DICT)

        hero.xp += raid.xp_bank
        hero.gold += raid.gold_bank
        hero.inventory.extend(raid.item_bank)
        hero.raiding = False

        MASTER_RAID_DICT.pop(hero.name)

        await ctx.send(embed=raid_end_early(raid))


@bot.command()
async def ep(ctx, target="None"):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:
        hero_name = set_hero_user(ctx.message.author.id)

        if target == "None":
            hero = get_hero(HERO_LIST, hero_name)
        else:
            if target.title() in HERO_NAME_LIST:
                hero = get_hero(HERO_LIST, target.title())
            else:
                await ctx.send(block_text(f"{target.title()} is not on the Hero List"))
                return
        await ctx.send(
            block_text(
                f"{hero.name} currently has {hero.current_ep}/{hero.max_ep + hero.bonus_ep} energy points"
            )
        )


@bot.command(aliases=["eq"])
async def equip(ctx, equippable):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        legendary = Legendary()
        armors = Armors()

        # Shortcuts
        equippable = shortcut_return(equippable.title())

        # Lock equipment during raid
        if hero.raiding:
            await ctx.send(block_text(f"You haven't the time to change equipment in The Bastion!"))
            return

        # Verify permanent is in armory
        if equippable in legendary.legends:
            if hero.equipment != "None":
                await ctx.send(block_text(f"You must unequip {hero.equipment} before equipping a new legendary."))
                return

            if equippable not in hero.armory:
                await ctx.send(block_text(f"{equippable} is not in your armory!"))
                return

            # Get Mode
            if equippable == "Rod Of Lordly Might":
                await ctx.send(block_text("You have equipped the Rod of Lordly Might!\nPlease choose a mode:\n"
                                          "Battleaxe: Immense damage modification\n"
                                          "Spear: Damage modification, can use the ability 'Spearsling'\n"
                                          "Barrier: Impenetrable defenses"))

                def check(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel and \
                           msg.content.lower() in ["battleaxe", "spear", "barrier"]

                try:
                    mode = await bot.wait_for("message", check=check, timeout=15)
                    mode = mode.content.lower()

                except TimeoutError:
                    await ctx.send(block_text("The ROLM was denied transformation and refused attunement"))
                    return

                transform_ability = {
                    "Transform": {
                        "name": "Transform |tra|",
                        "text": f"Like a magic shifting blur",
                        "dmg": 0,
                        "effect": "transform",
                        "description": f"Changes the equipment type of the Rod Of Lordly Might"
                    }
                }

                hero.sp_atk["Transform"] = transform_ability["Transform"]

                legendary.rod_of_lordly_might(mode_set=mode)

                await ctx.send(embed=rolm_embed(legendary, hero, mode))

            elif equippable == "Natures Mantle":
                legendary.natures_mantle()
                await ctx.send(embed=natures_mantle_embed(legendary, hero))

            elif equippable == "Vestige Blade":
                legendary.vestige_blade()
                await ctx.send(embed=vestige_embed("equip", hero, vestige=legendary))

            elif equippable == "Chidori":
                legendary.chidori(hero)
                await ctx.send(embed=chidori_embed(legendary, hero))

            elif equippable == "Forbidden Fruit":
                legendary.forbidden_fruit(hero)
                await ctx.send(embed=forbidden_fruit_embed(legendary, hero))

            elif equippable == "Yamatos Training Katana":
                legendary.yamatos_training_katana()
                await ctx.send(embed=ytk_embed(legendary, hero))

            else:
                await ctx.send(f"{equippable} not added to equippable legendaries, notify the admin")
                return

            legendary.equip(hero)

            hero.armory.remove(equippable)
            hero.equipment = equippable

        elif equippable in armors.armors:
            if hero.armor != "None":
                await ctx.send(block_text(f"You must unequip {hero.armor} before equipping a new armor."))
                return

            if equippable not in hero.armory:
                await ctx.send(block_text(f"{equippable} is not in your armory!"))
                return

            if equippable == "Cloth Armor":
                armors.cloth_armor()

            elif equippable == "Leather Armor":
                armors.leather_armor()

            elif equippable == "Mail Armor":
                armors.mail_armor()

            elif equippable == "Plate Armor":
                armors.plate_armor()

            elif equippable == "Bag Of Holding":
                armors.bag_of_holding()

            else:
                await ctx.send(f"{equippable} not added to equippable armors command, notify the admin")
                return

            armors.equip(hero)
            await ctx.send(embed=armor_embed(equippable, hero))

            hero.armory.remove(equippable)
            hero.armor = equippable

        else:
            await ctx.send(
                block_text(f"Equipment not found. Please check your target equipment spelling and try again. "
                           f"Equipment: {equippable}"))
            return
    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        return
    else:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        legendary = Legendary()
        armors = Armors()

        # Shortcuts
        equippable = shortcut_return(equippable.title())
        print(equippable)
        # Verify permanent is in armory
        if equippable in legendary.legends:
            if hero.equipment != "None":
                await ctx.send(block_text(f"You must unequip {hero.equipment} before equipping a new legendary."))
                return

            if equippable not in hero.armory:
                await ctx.send(block_text(f"{equippable} is not in your armory!"))
                return

            if equippable == "Yamatos Training Katana":
                legendary.yamatos_training_katana()
                await ctx.send(embed=ytk_embed(legendary, hero))

            legendary.equip(hero)

            hero.armory.remove(equippable)
            hero.equipment = equippable
            hero.training_stage += 1

            await ctx.send(
                embed=standard_embed(
                    title="Legendary Equipped!",
                    text="You have equipped Yamato's Training Katana! Legendary equipment "
                         "is obtained by summoning (obtain 4 keys from legendary monster "
                         "kills) an Apex creature, and killing it."
                         "\n\n"
                         "Legendary equipment can "
                         "add permanent statuses, new abilities, and huge stat bonuses. "
                         "\n\n"
                         "That is uh... family heirloom though. So I will need it back. "
                         'Use the command: **.unequip "yamatos training katana"** '
                         "*(.uneq ytk for short)* to unequip the item. This returns the "
                         "katana to your armory.",
                    footer="Don't forget to **.equip ca**!"
                )
            )

        elif equippable in armors.armors:
            if hero.armor != "None":
                await ctx.send(block_text(f"You must unequip {hero.armor} before equipping a new armor."))
                return

            if equippable not in hero.armory:
                await ctx.send(block_text(f"{equippable} is not in your armory!"))
                return

            if equippable == "Cloth Armor":
                armors.cloth_armor()

            else:
                await ctx.send(f"{equippable} not added to equippable armors command, notify the admin")
                return

            armors.equip(hero)
            await ctx.send(embed=armor_embed(equippable, hero))

            hero.armory.remove(equippable)
            hero.armor = equippable
            hero.training_stage += 1

            await ctx.send(
                embed=standard_embed(
                    title="Cloth Armor Equipped!",
                    text="You have equipped Cloth Armor! Armor is obtained by purchasing "
                         "it from the shopkeeper in the armor category. Armor can add EP, "
                         "some defense, or more defense at the expense of attack power. "
                         "\n\n"
                         "A particularly rare armor even expands your inventory space. "
                         "\n\n"
                         "That is uh... family heirloom though. So I will need it back. "
                         'Use the command: **.unequip "cloth armor"** *(.uneq ca for short)* '
                         "to unequip the armor. This returns the armor to your armory.",
                    footer="Don't forget to **.equip ytk**!"
                )
            )


@bot.command(aliases=["f"])
async def fight(ctx, monster):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home]:
        # Assign directory for channel
        if ctx.channel.id in [beyond_the_gates, the_meadow, testing_home]:
            current_mon_directory = MONSTER_LIST
        elif ctx.channel.id == beyond_the_battlefield:  # beyond the bf
            current_mon_directory = MONSTER_LIST2
        elif ctx.channel.id == heart_of_the_maw:  # heart of the maw
            current_mon_directory = MONSTER_LIST3
        else:
            print("Directory not set, channel information not included")
            return

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Catch resting heroes
        if hero.resting == "Resting":
            t_format = "%b %d %Y at %I:%M%p"
            alarm_clock = datetime.strptime(hero.alarm_clock, t_format)
            now = datetime.now()
            diff = alarm_clock - now
            time_left = int(diff / timedelta(minutes=1))
            await ctx.send(block_text(f"{hero.name} is still resting! {time_left} minutes left."))
            return

        # Catch Raiding
        if hero.raiding:
            await ctx.send(code_block(f"{hero.name} must complete their raid before fighting the main board monsters"))
            return

        # Stop raiders from fighting in the main board
        if ctx.channel.id in [raid_1, raid_2, raid_3]:
            await ctx.send(
                code_block(f"To fight the denizens of the raid you must use the .raid 'monster name' command!"))
            return

        # Shortcuts
        monster_name = shortcut_return(monster.title())

        # Get monster object
        monster = get_monster(current_mon_directory, monster_name)

        if not monster:
            await ctx.send(block_text(f"{monster_name} not found in the Maw."))
            return

        # Prevent fighting in meadow against non-Apex monsters1
        if ctx.channel.id == the_meadow and monster.rank != "Apex":
            await ctx.send(code_block("You may only fight the Apex in the meadow"))
            return

        # Pick up Chest
        if monster.name == "Chest":

            if monster.rarity == "Common":
                hero.gold += monster.contents
            else:
                if not inventory_capped(hero):
                    hero.inventory.append(monster.contents)
                else:
                    await ctx.send(block_text("Your inventory is full!"))
                    return

            current_mon_directory.remove(monster)
            await ctx.send(embed=chest_embed(hero.name, monster.rarity, monster.contents))
            return

        fight = Fight(hero, monster)

        # Add hero to attacked by list
        if hero.name not in monster.attacked_by:
            monster.attacked_by.append(hero.name)

        # Count fight records
        records = open_hero_records(ctx.message.author.id)
        records["records"]["combats initiated"] += 1

        # Set attack order, set attack stats
        fight.set_attack_order(hero, monster)

        # Handle status changes
        fight.status_handler(hero, monster)

        # Roll Damages
        fight.roll_hero_damage()
        fight.roll_monster_damage()

        # Apply post damage roll status
        fight.post_damage_status_handler(hero, monster)

        if "Fractured" in hero.status:
            if fight.hero_crit:
                damage = fight.fractured_damage()
                await ctx.send(embed=status_effect_card(hero.name, "Fractured", damage=damage))

        # Vestige effect send
        if "Spirit Trace" in hero.status:
            if fight.hero_crit:
                await ctx.send(embed=vestige_embed("crit", hero.name, monster=monster.name))

        # Martyr status block
        if "Martyr" in list(GLOBAL_STATUS_DICT.values()):
            tank = list(GLOBAL_STATUS_DICT.keys())[list(GLOBAL_STATUS_DICT.values()).index("Martyr")]
            if random.randint(1, 15) == 1 and hero.name != tank.name:
                blocked_damage = fight.monster_damage
                fight.martyr_mitigation()
                martyr_xp = random.randint(500, 650)
                tank.xp += martyr_xp
                await ctx.send(embed=martyr_embed(tank, hero.name, blocked_damage, martyr_xp))
                del GLOBAL_STATUS_DICT[tank]

        # Battlemage status block
        if "Battlemage" in hero.status:
            if fight.monster_damage > 0 and not fight.monster_damage_mitigated:
                hero.status.remove("Battlemage")
                hero.bonus_atk -= hero.battlemage_attack_mod
                hero.defense -= hero.battlemage_defense_mod
                hero.crit_multiplier -= hero.battlemage_crit_mod
                await ctx.send(embed=battlemage_end_embed(hero.name, False))

        fight.check_damage_mitigation()
        fight.apply_damage(hero, monster)

        # Save damage records
        if fight.hero_damage > records["records"]["highest damage"]:
            records["records"]["highest damage"] = fight.hero_damage
        records["records"]["total damage done"] += fight.hero_damage

        # Art of War status block
        if "Art Of War" in hero.status:
            if fight.overkill > 0:
                random_monster = select_random_monster(1, current_mon_directory, monster.name)[0]
                random_monster.current_hp -= fight.overkill
                if random_monster.current_hp < 0:
                    random_monster.current_hp = 1
                await ctx.send(embed=art_of_war_embed(fight.overkill, hero.name, random_monster.name))

        # Check Hero Death
        if hero.current_hp <= 0:
            if "Arawn's Gift" in hero.status:
                hero.current_hp = 1
                hero.status.remove("Arawn's Gift")
                await ctx.send(embed=gift_of_arawn_result_embed(hero.name))
            else:
                # Remove Hero from attacked by lists
                directories = [MONSTER_LIST, MONSTER_LIST2, MONSTER_LIST3]
                for directory in directories:
                    for mon in directory:
                        if mon.name == "Chest":
                            continue
                        elif hero.name in mon.attacked_by:
                            mon.attacked_by.remove(hero.name)
                hero.current_hp = 0
                entomb(hero)
                await ctx.send(embed=character_death_embed(hero, monster))
                os.remove(f"characters/{hero.name}.json")

        # Check Monster Death
        if monster.rank == "Apex" and hero.name != monster.summoner and monster.current_hp <= 0:
            await ctx.send(
                code_block(f"The Apex has fallen. Only {monster.summoner} may collect the body of the Apex!"))
            close_hero_records(records, hero.owner)
            return

        if monster.current_hp <= 0:

            # Increment Apex survived record
            if monster.rank == "Apex":
                records["records"]["apexes slaughtered"] += 1

            # Get Rewards
            total_gp = gp_set(monster.rank)
            if monster.name == "Treasure Goblin":
                total_gp = 1000
            gp_divided = total_gp // len(monster.attacked_by)
            divided_xp = monster.xp // len(monster.attacked_by)

            attacking_heroes = [get_hero(HERO_LIST, hero_name) for hero_name in monster.attacked_by]
            enlightened_hero = []
            for attacking_hero in attacking_heroes:
                attacking_hero.gold += gp_divided

                if "Enlightened" in attacking_hero.status:
                    en_xp = divided_xp * 2
                    enlightened_hero.append(attacking_hero.name)
                    attacking_hero.xp += en_xp
                    attacking_hero.status.remove("Enlightened")
                else:
                    attacking_hero.xp += divided_xp

            if monster.item is not None:
                if monster.rank == "Apex":
                    hero.armory.append(monster.item)

                elif monster.rank == "Legendary":
                    hero.keys.append(monster.item)

                    # Increment Key Record
                    records["records"]["keys collected"] += 1

                else:
                    if not inventory_capped(hero):
                        hero.inventory.append(monster.item)

            # Send Fight Kill Embed
            await ctx.send(embed=fight_kill_embed(fight, hero, monster, gp_divided, divided_xp, enlightened_hero))

            # Check Levels
            for attacking_hero in attacking_heroes:
                leveled = check_xp(attacking_hero)
                if leveled:
                    results = level_up(attacking_hero)
                    if results[5][0]:
                        await ctx.send(embed=new_ability_embed(attacking_hero.name, results[5][1]))
                    await ctx.send(embed=level_up_embed(attacking_hero, results))

            # Increment Dark Druids
            if hero.class_ == "Dark Druid":
                dark_druid_return = increment_dark_druid(hero, monster.rank)
                print(f"Dark Druid Return: {dark_druid_return}")
                if dark_druid_return[0]:
                    await ctx.send(embed=dark_druid_ritual_embed(dark_druid_return[1]))

            # Ki bomb status block
            if "Ki Bomb" in monster.status and "Ki Bomb" in list(hero.sp_atk.keys()):
                hit_monsters = select_random_monster(2, current_mon_directory, monster.name)

                # Roll Ki Bomb damage
                skill_dmg = hero.sp_atk["Ki Bomb"]["dmg"]
                floor_dmg = skill_dmg // 2
                kb_dmg = random.randint(floor_dmg, skill_dmg)

                for target_struck in hit_monsters:
                    target_struck.current_hp -= kb_dmg
                    if target_struck.current_hp <= 0:
                        target_struck.current_hp = 1

                await ctx.send(embed=ki_bomb_result_embed(monster.name, hit_monsters, kb_dmg))

            # Suggest new monster
            suggestion_list = []
            for mtr in current_mon_directory:
                if monster.rank in ["Apex", "Legendary"]:
                    break
                elif mtr.rank in ["Apex", "Legendary", "Chest"]:
                    continue
                else:
                    if monster.rank - 1 <= mtr.rank <= monster.rank + 1 and mtr.name != monster.name:
                        if mtr.name in list(mss.keys()):
                            suggestion_list.append([mtr.name, f"|{mss[mtr.name]}|"])
                        else:
                            suggestion_list.append([mtr.name, ""])

            suggestion_list2 = [f"{suggestion[0]}{suggestion[1]}" for suggestion in suggestion_list]

            if not suggestion_list2:
                text = "No monsters within 2 ranks"
            else:
                text = ', '.join(suggestion_list2)

            await ctx.send(code_block(f"Comparable Monsters: {text}"))

            # Update kill records
            records["records"]["total monsters killed"] += 1

            # Cure apex aura
            if monster.rank == "Apex":
                for character in monster.attacked_by:
                    print(f"apex_character {character}")
                    character = get_hero(HERO_LIST, character)
                    apex_status_cure(character, monster.aura)

            # Remove monster
            current_mon_directory.remove(monster)

        else:
            if monster.rank == "Apex":
                apex_status = apex_status_afflict(hero, monster)
                if apex_status != "no effect":
                    await ctx.send(embed=apex_status_embed(apex_status[0], apex_status[1]))

            await ctx.send(embed=fight_embed(fight, hero, monster))
            # Return monster status to normal if cleared
            if not monster.status:
                monster.status.append("Normal")

        # Return hero status to normal if cleared
        if not hero.status:
            hero.status.append("Normal")
        elif len(hero.status) > 1 and "Normal" in hero.status:
            hero.status.remove("Normal")

        # Clear deceased hero
        if hero.current_hp < 1:
            HERO_LIST.remove(hero)

        # Shut record book
        close_hero_records(records, hero.owner)

    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features, raid_1, raid_2, raid_3]:
        pass
    else:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        if monster.lower() != "imp" and not hero.raiding:
            await ctx.send(block_text("No, the Imp. Fight the Imp. Check your spelling!"))
            return

        if hero.training_stage == 2:
            await ctx.send(
                embed=fake_fight_embed(hero))

            hero.current_hp -= 3
            hero.training_stage = 3
            await sleep(2)
            await ctx.send(
                embed=standard_embed(
                    title="Fight Complete!",
                    text="Great! You just took part in your first round "
                         "of combat! When you fight a monster, you "
                         "roll your stats against the monster's stats "
                         "and apply damage.\n\n"
                         ""
                         "If you want to know what stats we are talking about, "
                         "use the command **.stats** to check out your hero!"))

            await sleep(7)
            await ctx.send(
                embed=standard_embed(
                    title="Finish Him!",
                    text="Anyway... that Imp is still prowling around. "
                         "Lets finish it off. Use the **.fight Imp** "
                         "command to begin another round of combat!"))

        elif hero.training_stage == 3:
            hero.current_hp -= 22
            hero.fight_stage = 4
            hero.xp += 55
            hero.inventory.append("Healing Potion")

            await ctx.send(
                embed=fake_fight_embed2(hero))

            await sleep(3)
            await ctx.send(
                embed=standard_embed(
                    title="Battle Complete!",
                    text="You killed the Imp! When you kill a monster you will "
                         "see your rewards on this 'Monster Slain' card. This shows every hero "
                         "that took part in killing the monster as well as everyone's XP "
                         "and item reward. Only the monster slayer gets the item. Everyone "
                         "else gets gold pieces (or GP) used to buy items and armor in the shop. Not "
                         "every monster holds an item. Sometimes you will only get GP as a "
                         "reward!\n\n"
                         ""
                         "It looks like that Imp hit you pretty hard. How about you use the "
                         "healing potion it just dropped you? To use items, you call the "
                         "item as a command. Spaced items require an underscore. "
                         "Type the command: **.healing_potion** or **.hpot** for short."))


@bot.command(aliases=["g"])
async def give(ctx, item, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:

        hero_name = set_hero_user(ctx.message.author.id)
        target_name = target.title()
        item = item.title()

        hero = get_hero(HERO_LIST, hero_name)
        target = get_hero(HERO_LIST, target_name)

        print(hero.name)
        print(hero.inventory)
        # Shortcuts
        item = shortcut_return(item)

        # Block permanent trading
        legends = Legendary()
        armors = Armors()
        items = Items()

        if item in armors.armors or item in legends.legends:
            await ctx.send(block_text(f"Trading of Legendary gear and armors is strictly prohibited. For now."))
            return

        # Block trading to capped targets
        if inventory_capped(target):
            await ctx.send(block_text(f"{target}'s inventory is full!"))
            return

        # Verify item is in inventory
        if item in items.keys and item not in hero.keys or item in items.master and item not in hero.inventory:
            await ctx.send(block_text(f"{hero.name} does not have {item}"))
            return

        # Check Target Present
        if target not in HERO_LIST:
            await ctx.send(block_text(f"{target.name} is not in the Hero List."))
            return

        if target.raiding:
            await ctx.send(block_text(f"The Last Bastion prevents you from trading with {target.name}!"))
            return

        # Remove and append target card
        item_type = items.return_item(item)

        if item_type == "inventory":
            hero.inventory.remove(item)
            target.inventory.append(item)
        elif item_type == "keys":
            hero.keys.remove(item)
            target.keys.append(item)

        await ctx.send(embed=give_item_embed(hero.name, item, target.name))


@bot.command()
async def gp(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        await ctx.send(block_text(f"{hero.name}'s GP: {hero.gold}"))


@bot.command(aliases=["hrs"])
async def heroes(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:
        await ctx.send(embed=heroes_embed(HERO_LIST))


@bot.command()
async def hp(ctx, target="None"):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:
        if target == "None":
            hero_name = set_hero_user(ctx.message.author.id)
            hero = get_hero(HERO_LIST, hero_name)
        else:
            if target.title() in HERO_NAME_LIST:
                hero = get_hero(HERO_LIST, target.title())
            else:
                await ctx.send(block_text(f"{target.title()} is not on the Hero List"))
                return

        await(ctx.send(block_text(f"{hero.name}\n{hero.current_hp}/{hero.max_hp + hero.bonus_hp} HP")))


@bot.command(aliases=["inv"])
async def inventory(ctx, target="None"):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:
        hero_name = set_hero_user(ctx.message.author.id)

        if target == "None":
            hero = get_hero(HERO_LIST, hero_name)
        else:
            if target.title() in HERO_NAME_LIST:
                hero = get_hero(HERO_LIST, target.title())
            else:
                await ctx.send(block_text(f"{target.title()} is not on the Hero List"))
                return

        string_list = [f"{item} |{iss[item]}|" for item in hero.inventory]
        string = ", ".join(string_list)
        inventory_used = len(hero.inventory)

        if inventory_used > 0:
            if "Organized" in hero.status:
                await ctx.send(block_text(f"Inventory Capacity: {inventory_used}/15\n{string}"))
            else:
                await ctx.send(block_text(f"Inventory Capacity: {inventory_used}/10\n{string}"))
        else:
            await ctx.send(block_text("Your inventory is empty!"))


@bot.command(aliases=["k"])
async def keys(ctx, target="None"):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:
        hero_name = set_hero_user(ctx.message.author.id)

        if target == "None":
            hero = get_hero(HERO_LIST, hero_name)
        else:
            if target.title() in HERO_NAME_LIST:
                hero = get_hero(HERO_LIST, target.title())
            else:
                await ctx.send(block_text(f"{target.title()} is not on the Hero List"))
                return
        keys = hero.keys
        joined_keys = ", ".join(keys)
        if not hero.keys:
            joined_keys = "You have no keys... yet"
        await ctx.send(block_text(joined_keys))


@bot.command()
async def apex(ctx):
    if ctx.channel.id in [the_meadow]:

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ["y", "n"]

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        hero_inv = hero.keys

        await ctx.send(embed=keys_field_embed(hero.name))

        await ctx.send(block_text("Checking keys..."))
        await sleep(0)

        if "Blood-Soaked Key" in hero_inv:
            await ctx.send(embed=keys_blood_soaked_embed(hero.name))
            bsk = True
        else:
            await ctx.send(block_text("You are missing the key to the bloody altar"))
            return

        await sleep(2)
        await ctx.send(block_text(f"Use Blood-Soaked Key? Y or N."))

        try:
            msg = await bot.wait_for("message", check=check)
        except TimeoutError:
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return

        if msg.content == "y":
            await ctx.send(embed=keys_use_key_embed(hero.name, "Blood-Soaked Key"))
        elif msg.content == "n":
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return

        await sleep(0)
        await ctx.send(block_text(f"{hero.name} continues to investigate the meadow..."))
        await sleep(0)
        if "Tortoise Key" in hero_inv:
            await ctx.send(embed=keys_tortoise_embed(hero.name))
            tk = True
        else:
            await ctx.send(block_text("You are missing the key to a shelled lock"))
            return

        await sleep(0)
        await ctx.send(block_text(f"Use Tortoise Key? Y or N."))

        try:
            msg = await bot.wait_for("message", check=check)
        except TimeoutError:
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return

        if msg.content == "y":
            await ctx.send(embed=keys_use_key_embed(hero.name, "Tortoise Key"))
        elif msg.content == "n":
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return

        await sleep(0)
        await ctx.send(block_text(f"{hero.name} continues to investigate the meadow..."))
        await sleep(0)
        if "Dimensional Key" in hero_inv:
            await ctx.send(embed=keys_dimensional_embed(hero.name))
            dk = True
        else:
            await ctx.send(block_text("You are missing the key to the cosmic stone"))
            return

        await sleep(0)
        await ctx.send(block_text(f"Use Dimensional Key? Y or N."))

        try:
            msg = await bot.wait_for("message", check=check)
        except TimeoutError:
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return
        if msg.content == "y":
            await ctx.send(embed=keys_use_key_embed(hero.name, "Dimensional Key"))
        elif msg.content == "n":
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return

        await sleep(0)
        await ctx.send(block_text(f"{hero.name} continues to investigate the meadow..."))
        await sleep(0)
        if "Mountain Key" in hero_inv:
            await ctx.send(embed=keys_mountain_embed(hero.name))
            mk = True
        else:
            await ctx.send(block_text("You are missing a key to the stone golem altar"))
            return

        await sleep(0)
        await ctx.send(block_text(f"Use Mountain Key? Y or N."))
        try:
            msg = await bot.wait_for("message", check=check)
        except TimeoutError:
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return
        if msg.content == "y":
            await ctx.send(embed=keys_use_key_embed(hero.name, "Mountain Key"))
        elif msg.content == "n":
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return

        await sleep(0)
        await ctx.send(block_text(f"{hero.name} hears a thunderous rumble back in the meadow..."))
        await ctx.send(block_text(f"Re-enter the meadow? Y or N"))

        try:
            msg = await bot.wait_for("message", check=check)
        except TimeoutError:
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return
        if msg.content.lower() == "y":
            await ctx.channel.purge(limit=100)
        if msg.content.lower() == "n":
            await ctx.channel.purge(limit=100)
            await ctx.send(block_text(f"{hero.name} has been teleported out of the meadow."))
            return

        if bsk and tk and dk and mk:
            hero.keys.remove("Blood-Soaked Key")
            hero.keys.remove("Tortoise Key")
            hero.keys.remove("Dimensional Key")
            hero.keys.remove("Mountain Key")

            mtr = MonsterBuilder("Apex")
            mtr.summoner = hero.name

            t_format = "%b %d %Y at %I:%M%p"
            summon_time = str(datetime.now().strftime(t_format))
            dispersal_time = str((datetime.now() + timedelta(hours=2)).strftime(t_format))

            mtr.summoned = summon_time
            mtr.dispersal = dispersal_time
            mtr.aura = random.choice(["Silencer", "Barbed", "Drainer", "Absorbing", "Caustic", "Breaker"])

            # Check duplicate permanent
            if mtr.item in hero.equipment or mtr.item in hero.armory:
                mtr.item = None

            MONSTER_LIST.append(mtr)

            await ctx.send(embed=keys_apex_summon(hero, mtr, summon_time, dispersal_time))
            await ctx.send(block_text(f"The {mtr.name} is bound to this plane until {dispersal_time}.\n"
                                      f"After such time, the meadow will disperse and return to it's previous state."))
            await ctx.send(embed=apex_aura_embed(mtr.aura))
        else:
            await ctx.send(block_text("Apex monster empowered... what have you done..."))
            return


@bot.command(aliases=["mons"])
async def monsters(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, testing_home, beyond_the_battlefield, heart_of_the_maw]:
        if ctx.channel.id in [beyond_the_gates, the_meadow]:
            current_mon_directory = MONSTER_LIST
        elif ctx.channel.id == beyond_the_battlefield:
            current_mon_directory = MONSTER_LIST2
        elif ctx.channel.id == heart_of_the_maw:
            current_mon_directory = MONSTER_LIST3
        else:
            print("channel ID not found")
            return

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if hero.raiding:
            await ctx.send(block_text("You must complete your raid before returning to the Maw! Use .end_raid to end "
                                      "your raid early."))
            return

        await ctx.send(embed=monster_list_embed(current_mon_directory))

    elif ctx.channel.id in [raid_1, raid_2, raid_3, testing_home]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        raid = MASTER_RAID_DICT[f"{hero.name}"]

        # Respond to command when no raid present
        if not hero.raiding:
            await ctx.send(block_text(f"{hero.name} does not have an assigned raid!"))
            return

        await ctx.send(embed=raid_monster_list_embed(raid))
    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        pass
    else:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        hero.training_stage = 4

        await ctx.send(embed=monster_list_embed(MONSTER_LIST))
        await sleep(4)
        await ctx.send(
            embed=standard_embed(
                title="The Maw",
                text="There will be infinite monsters to fight in the Maw. Monster status "
                     "is shown in this screen as well as their max attack roll. Watch out for "
                     "monsters that are empowered! They have higher than "
                     "normal stats, but also give greater rewards.\n\n"
                     ""
                     "While fighting "
                     "monsters, you will gain experience, level up, find equippable gear and "
                     "gain new abilities! With time and power, you may even find yourself "
                     "fighting your way up the raid leaderboard!\n\n"
                     ""
                     "Lets take a look at abilities... type **.train** to continue."))


@bot.command(aliases=["pur"])
async def purchase(ctx, item):
    if ctx.channel.id in [the_shop]:
        item = item.title()

        item = shortcut_return(item)
        armors = Armors()
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if hero.shop_lock:
            await ctx.send(code_block(f"Nah nah nah nah nah. Turn around and keep talking to Yamato bud."))
            return

        # Catch Raiding
        if hero.raiding:
            await ctx.send(code_block(f"You must complete your raid before utilizing the shop!"))
            return

        # Check if inventory capped
        if item in armors.armors:
            pass
        else:
            if inventory_capped(hero):
                await ctx.send(block_text("Your inventory is full!"))
                return

        # Check if armor already owned
        if item in armors.armors:
            if item in hero.armory or item in hero.armor:
                await ctx.send(block_text("I see you already have this armor. I'll hold on to this one for a needy "
                                          "traveler."))
                return

        global SHOP

        # Random item handling
        if item == "Random Item":
            roll = Items()
            item_nested_list = [roll.tier1_items, roll.tier2_items, roll.tier3_items, roll.keys]
            select_nest = random.choices(item_nested_list, weights=[6, 5, 4, 1])
            select_item = random.choice(select_nest[0])

            if hero.gold >= 1000:
                hero.gold -= 1000

                if select_item in roll.keys:
                    hero.keys.append(select_item)
                else:
                    hero.inventory.append(select_item)

                if select_item in roll.tier1_items:
                    text = f"Well... here is your {select_item}. No refunds."
                elif select_item in roll.tier2_items:
                    text = f"Not bad... use this {select_item} well."
                elif select_item in roll.tier3_items:
                    text = f"Wait, wait, wait, this {select_item} shouldn't be in here!"
                else:
                    text = f"I don't even know what this {select_item} is. Thanks for buying it."

                await ctx.send(block_text(text))
                await ctx.send(embed=shop_embed(SHOP, hero))
                return

            else:
                await ctx.send(block_text(f"You have only {hero.gold} gold pieces! Go kill more monsters!"))
                return

        merch = None
        item_present = False
        for sale_item in SHOP:
            if item in sale_item:
                item_present = True
                merch = sale_item

        if item_present:
            if hero.gold >= merch[1]:
                SHOP.remove(merch)
                hero.gold -= merch[1]

                if merch[0] in armors.armors:
                    hero.armory.append(merch[0])
                else:
                    hero.inventory.append(merch[0])

                await ctx.send(block_text(f"{item} purchased! Thank you for your business {hero.name}!"))
                await ctx.send(embed=shop_embed(SHOP, hero))
            else:
                await ctx.send(block_text(f"You have only {hero.gold} gold pieces! Go kill more monsters!"))
                return


@bot.command(aliases=["br", "raid_begin"])
async def begin_raid(ctx):
    if ctx.channel.id in [raid_1, raid_2, raid_3, testing_home]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        yamato = get_hero(HERO_LIST, "Yamato")

        yamato.inventory.clear()

        if hero.raiding:
            await ctx.send(block_text("You must finish your current raid before starting a new one."))
            return

        def yamato_embed_inventory():
            base = discord.Embed(
                title="The Thousand Year Hunter",
                description=f"You have nothing to offer in this hellscape. Begone.",
                colour=discord.Colour.teal(),
            )
            base.set_thumbnail(url="https://images.beastsofwar.com/2014/09/The-Defeated1-660-371.jpg")
            return base

        if not hero.inventory:
            await ctx.send(embed=yamato_embed_inventory())
            return
        else:
            random_request_item = random.choice(hero.inventory)
            random_request_shortcut = iss[random_request_item]

        t_format = "%b %d %Y at %I:%M%p"
        last_check = hero.raid_cooldown
        comparable_time = datetime.strptime(last_check, t_format)
        if datetime.now() > comparable_time + timedelta(hours=1):
            hero.raid_cooldown = str(datetime.now().strftime(t_format))
        else:
            await ctx.send(block_text("You search everywhere, unable to locate Yamato in the endless blizzard"))
            return

        # Catch Resting
        if hero.resting == "Resting":
            t_format = "%b %d %Y at %I:%M%p"
            alarm_clock = datetime.strptime(hero.alarm_clock, t_format)
            now = datetime.now()
            diff = alarm_clock - now
            time_left = int(diff / timedelta(minutes=1))
            await ctx.send(block_text(f"{hero.name} is still resting! {time_left} minutes left."))
            return

        def yamato_embed_1():
            base = discord.Embed(
                title="The Thousand Year Hunter",
                description=f"You come across a lone hunter, scarred and bloody from an eternity in the Maw. She beckons you over.",
                colour=discord.Colour.teal(),
            )
            base.set_thumbnail(url="https://i.pinimg.com/originals/34/33/0c/34330c1348f48eb384bbdedd677c452f.jpg")
            return base

        await ctx.send(embed=yamato_embed_1())
        await sleep(1)

        def yamato_embed_2(random_request_item):
            base = discord.Embed(
                title="Yamato",
                description=f"I desperately need your {random_request_item} |{random_request_shortcut}|... may I have it?",
                colour=discord.Colour.teal(),
            )
            base.set_thumbnail(url="https://images.beastsofwar.com/2014/09/The-Defeated1-660-371.jpg")
            base.set_footer(text="Try using .give 'item' yamato.")
            return base

        await ctx.send(embed=yamato_embed_2(random_request_item))

        def yamato_embed_3(hero_class):
            base = discord.Embed(
                title="Yamato",
                description=f"Then I find no reason for this conversation to continue. On with you {hero_class}.\n"
                            f"*Yamato continues on, pushing by you, disappearing into the flurry.*",
                colour=discord.Colour.teal(),
            )
            base.set_thumbnail(url="https://images.beastsofwar.com/2014/09/The-Defeated1-660-371.jpg")
            return base

        hero.shop_lock = True

        waiting = True
        count = 0
        while waiting:
            if random_request_item in yamato.inventory:
                waiting = False

            count += 1
            if count == 60:
                await ctx.send(embed=yamato_embed_3(hero.class_))
                return

            await sleep(1)

        def yamato_embed_4():
            base = discord.Embed(
                title="Yamato",
                description=f"I've been here for millennia and no one has shared such kindness in this terrible place"
                            f" I haven't much to give... but I do know of a nearby marsh that is teaming with powerful"
                            f" monsters. I trained there when I was an Assassin. I'll show you the way.",
                colour=discord.Colour.teal(),
            )
            base.set_image(url="https://images.beastsofwar.com/2014/09/The-Defeated1-660-371.jpg")
            return base

        await ctx.send(embed=yamato_embed_4())

        await sleep(1)

        records = open_hero_records(hero.owner)

        await ctx.send(block_text(f"Choose a difficulty (scaling difficulty starting at 1 - easiest)\n"
                                  f"Last Resistance Level: {hero.last_raid_complete}\n"
                                  f"Highest Resistance Level: {records['records']['highest raid complete']}"))

        def int_check(value):
            try:
                return isinstance(int(value), int)
            except ValueError:
                return False

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and int_check(msg.content)

        try:
            difficulty = await bot.wait_for("message", check=check, timeout=600)
        except TimeoutError:
            await ctx.send(f"You failed to select a difficulty.")
            await ctx.purge(limit=15)
            return

        difficulty_rating = int(difficulty.content)

        # Set raiding and raid start time
        t_format = "%b %d %Y at %I:%M%p"
        now = datetime.now()

        hero.shop_lock = False
        hero.raiding = True
        hero.raid_start = now.strftime(t_format)

        raid = Raid(hero.name)
        raid.set_difficulty(difficulty_rating)
        raid.set_equipment(hero)

        for i in range(1, 9):
            monster = MonsterBuilder(i)
            monster.raid_monster(difficulty_rating)
            if i != 1:
                monster.position_locked = True
            raid.add_monster(monster)

        boss = MonsterBuilder("Legendary")
        boss.raid_monster(difficulty_rating)
        raid.add_monster(boss)

        MASTER_RAID_DICT[hero.name] = raid

        await ctx.send(embed=raid_monster_list_embed(raid))


@bot.command(aliases=["rd"])
async def raid(ctx, target):
    if ctx.channel.id in [raid_1, raid_2, raid_3, testing_home]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        target = target.title()

        if hero.name not in list(MASTER_RAID_DICT.keys()):
            await ctx.send(block_text(f"{hero.name} has not started a Raid!"))
            return

        # Shortcuts
        if target in moncuts:
            target = moncuts_dict[target]

        raid = MASTER_RAID_DICT[hero.name]

        name_list = [monster.name for monster in raid.monsters]

        if target not in name_list:
            await ctx.send(block_text(f"{target} not found in your raid."))
            return

        monster = get_monster(raid.monsters, target)

        if monster.position_locked:
            await ctx.send(block_text(f"{monster.name} cannot be a target until the previous monster is killed"))
            return

        # Catch Resting
        if hero.resting == "Resting":
            t_format = "%b %d %Y at %I:%M%p"
            alarm_clock = datetime.strptime(hero.alarm_clock, t_format)
            now = datetime.now()
            diff = alarm_clock - now
            time_left = int(diff / timedelta(minutes=1))
            await ctx.send(block_text(f"{hero.name} is still resting! {time_left} minutes left."))

        raid = MASTER_RAID_DICT[hero.name]
        fight = Fight(hero, monster)

        # Count fight records
        records = open_hero_records(hero.owner)
        records["records"]["combats initiated"] += 1

        # Set attack order
        fight.set_attack_order(hero, monster)

        # Handle status changes
        fight.status_handler(hero, monster)

        # Roll Damages
        fight.roll_hero_damage()
        fight.roll_monster_damage()

        # Apply post damage roll status
        fight.post_damage_status_handler(hero, monster)

        if "Spirit Trace" in hero.status:
            if fight.hero_crit:
                await ctx.send(embed=vestige_embed("crit", hero.name, monster=monster.name))

        # Martyr status block
        if "Martyr" in list(GLOBAL_STATUS_DICT.keys()):
            tank_name = GLOBAL_STATUS_DICT["Martyr"]
            if random.randint(1, 10) == 1:
                blocked_damage = fight.monster_damage
                fight.martyr_mitigation()
                tank = get_hero(HERO_LIST, tank_name)
                martyr_xp = random.randint(500, 650)
                tank.xp += martyr_xp
                await ctx.send(embed=martyr_embed(tank, hero.name, blocked_damage, martyr_xp))
                del GLOBAL_STATUS_DICT["Martyr"]

        # Battlemage status block
        if "Battlemage" in hero.status:
            if fight.monster_damage > 0 and not fight.monster_damage_mitigated:
                hero.status.remove("Battlemage")
                hero.bonus_atk -= hero.battlemage_attack_mod
                hero.defense -= hero.battlemage_defense_mod
                hero.crit_multiplier -= hero.battlemage_crit_mod
                await ctx.send(embed=battlemage_end_embed(hero.name, False))

        fight.check_damage_mitigation()
        fight.apply_damage(hero, monster)

        # Save Damage Records
        if fight.hero_damage > records["records"]["highest damage"]:
            records["records"]["highest damage"] = fight.hero_damage
        records["records"]["total damage done"] += fight.hero_damage

        # Art of War status block
        if "Art Of War" in hero.status:
            if fight.overkill > 0:
                random_monster = select_random_monster(1, raid.monsters, monster.name)[0]
                if random_monster == "None":
                    pass
                else:
                    random_monster.current_hp -= fight.overkill
                    if random_monster.current_hp < 0:
                        random_monster.current_hp = 1
                    await ctx.send(embed=art_of_war_embed(fight.overkill, hero.name, random_monster.name))

        # Send fight stats
        await ctx.send(embed=fight_embed(fight, hero, monster))

        # Check Hero Death
        if hero.current_hp <= 0:
            if "Arawn's Gift" in hero.status:
                hero.current_hp = 1
                hero.status.remove("Arawn's Gift")
                await ctx.send(embed=gift_of_arawn_result_embed(hero.name))
            else:
                # Remove Hero from attacked by lists
                directories = [MONSTER_LIST, MONSTER_LIST2, MONSTER_LIST3]
                for directory in directories:
                    for monster in directory:
                        if monster.name == "Chest":
                            continue
                        elif hero.name in monster.attacked_by:
                            monster.attacked_by.remove(hero.name)
                hero.current_hp = 0
                entomb(hero)
                await ctx.send(embed=character_death_embed(hero, monster))
                os.remove(f"characters/{hero.name}.json")

        # Check Monster Death
        if monster.current_hp < 1:
            # Add GP to book
            if monster.rank == "Legendary":
                treasure = raid.difficulty * 23
            else:
                treasure = monster.rank * 23
            raid.gold_bank += treasure
            if monster.item is not None:
                if monster.item in ["Blood-Soaked Key", "Dimensional Key", "Tortoise Key", "Mountain Key"]:
                    raid.key_bank = monster.item
                    treasure = monster.item
                else:
                    raid.item_bank.append(monster.item)
                    treasure = monster.item

            # Add XP to book
            raid.xp_bank += monster.xp

            # Increment Dark Druids
            if hero.class_ == "Dark Druid":
                dark_druid_return = increment_dark_druid(hero, monster.rank)
                if dark_druid_return[0]:
                    await ctx.send(embed=dark_druid_ritual_embed(dark_druid_return[1]))

            # Ki bomb status block
            def kb_damage(monsters, hero):
                skill_damage = hero.sp_atk["Ki Bomb"]["dmg"]
                floor_damage = skill_damage // 2
                ki_bomb_damage = random.randint(floor_damage, skill_damage)

                for target_struck in monsters:
                    target_struck.current_hp -= ki_bomb_damage
                    if target_struck.current_hp < 0:
                        target_struck.current_hp = 1
                return ki_bomb_damage

            if "Ki Bomb" in monster.status:
                if len(raid.monsters) > 3:
                    hit_list = select_random_monster(2, raid.monsters, monster.name)
                    result_damage = kb_damage(hit_list, hero)
                    await ctx.send(embed=ki_bomb_result_embed(monster.name, hit_list, result_damage))
                elif len(raid.monsters) > 2:
                    hit_list = select_random_monster(1, raid.monsters, monster.name)
                    result_damage = kb_damage(hit_list, hero)
                    await ctx.send(embed=ki_bomb_result_embed(monster.name, hit_list, result_damage))
                else:
                    pass

            # Remove dead monster
            raid.monsters.remove(monster)

            # Update records
            records["records"]["total monsters killed"] += 1

            # Send embed with updated information on raid
            await ctx.send(embed=raid_monster_death_embed(hero, monster.xp, treasure))

            # Raid complete
            if len(raid.monsters) < 1:
                await ctx.send(
                    embed=raid_victory_embed(hero, raid))

                raid.reward_raid(hero)

                raid_record = open_hero_records(hero.owner)
                if raid.difficulty > raid_record["records"]["highest raid complete"]:
                    raid_record["records"]["highest raid complete"] = raid.difficulty

                # Find time to beat raid
                t_format = "%b %d %Y at %I:%M%p"
                raid_start = hero.raid_start
                then = datetime.strptime(raid_start, t_format)
                now = datetime.now()
                time_diff = now - then
                minutes = int(time_diff / timedelta(minutes=1))
                hours = math.floor(minutes / 60)
                minutes = minutes % 60
                time_string = f"{hours}H {minutes}M"

                LEADERBOARD.check_leaderboard(raid, hero, time_string)
                del MASTER_RAID_DICT[hero.name]

                # Finalize records
                close_hero_records(records, hero.owner)
                return

        # Unlock next monster
        raid.monsters[0].position_locked = False

        # Suggest next raid monster
        if raid.monsters[0].name in list(mss.keys()):
            suggestion_short = f"|{mss[raid.monsters[0].name]}|"
        else:
            suggestion_short = ""

        await ctx.send(block_text(f"Next Raid Monster: {raid.monsters[0].name}{suggestion_short}"))

        # Return monster status to normal
        if not monster.status:
            monster.status.append("Normal")

        # Return hero status to normal if cleared
        if not hero.status:
            hero.status.append("Normal")
        elif hero.status and "Normal" not in hero.status:
            hero.status.append("Normal")

        # Clear deceased hero
        if hero.current_hp <= 0:
            HERO_LIST.remove(hero)

        # Finalize records
        close_hero_records(records, hero.owner)


@bot.command(aliases=["recs"])
async def records(ctx):
    """
    Shows records for set hero, hero must be already set with .set_hero "HeroName"
        ex. .records
    ___
    No params
    """
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        with open(f"users/{ctx.message.author.id}.json", "r") as f:
            data = json.load(f)

        records = data["records"]
        await ctx.send(embed=records_embed(records, hero))


@bot.command(aliases=["r"])
async def rest(ctx, length="short"):
    """
    Set up camp with  your hero and rest for 10 minutes, recovering 25% hp and 1 skill point. (hero must be set)
        ex. .rest "HeroName"
    """
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        t_format = "%b %d %Y at %I:%M%p"

        if hero.resting == "Resting":
            alarm_clock = datetime.strptime(hero.alarm_clock, t_format)
            now = datetime.now()
            diff = alarm_clock - now
            time_left = int(diff / timedelta(minutes=1))
            await ctx.send(block_text(f"{hero.name} is still resting! {time_left} minutes left."))
            return

        if "Apex" in hero.status:
            hero.status.remove("Apex")

        if "Speed Rest" in hero.status:
            length = "long"

        if hero.raiding:
            await ctx.send(block_text(f"Resting while engaged in a raid will end the raid and award your "
                                      f"current raid bank. Enter 'y' to continue."))

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel and \
                       msg.content.lower() in ["y", "n"]

            msg = await bot.wait_for("message", check=check, timeout=30)

            if msg.content.lower() == "y":

                raid = MASTER_RAID_DICT[hero.name]
                raid.reward_raid(hero)

                await ctx.send(embed=raid_end_early(raid))

                del MASTER_RAID_DICT[hero.name]

            else:
                return

        records = open_hero_records(hero.owner)
        records["records"]["times rested"] += 1

        # Short rest activation
        if length.lower() == "short":
            hero.resting = "Resting"

            if "Speed Rest" in hero.status:
                hero.status.remove("Speed Rest")
                await ctx.send(block_text(f"{hero.name} has found a warm bed (10 seconds)"))
                await sleep(10)
            else:
                await ctx.send(block_text(f"{hero.name} set up a bedroll (5 minutes)"))
                resting_clock = datetime.now() + timedelta(minutes=5)
                hero.alarm_clock = resting_clock.strftime(t_format)
                await sleep(300)

            if hero.resting == "Not Resting":
                return

            hero.resting = "Not Resting"

            # Immense removal
            if "Immense" in hero.status:
                hero.status.remove("Immense")
                hero.bonus_hp -= hero.immense_hp
                if hero.current_hp > hero.max_hp + hero.bonus_hp:
                    hero.current_hp = hero.max_hp + hero.bonus_hp
                delattr(hero, "immense_hp")

            # Recover ability point if less than max
            if hero.current_ep < hero.max_ep + hero.bonus_ep:
                hero.current_ep += (hero.max_ep + hero.bonus_ep) // 2
                if hero.current_ep > (hero.max_ep + hero.bonus_ep):
                    hero.current_ep = hero.max_ep + hero.bonus_ep

            # Recover HP if less than max
            if hero.current_hp < hero.max_hp + hero.bonus_hp:
                hero.current_hp += (hero.max_hp + hero.bonus_hp) // 2
                if hero.current_hp > hero.max_hp + hero.bonus_hp:
                    hero.current_hp = hero.max_hp + hero.bonus_hp

            delattr(hero, "alarm_clock")
            await ctx.send(block_text(f"{hero.name} feels rested!\n"
                                      f"{hero.current_hp} / {hero.max_hp + hero.bonus_hp}"))

        # Long rest activation
        elif length.lower() == "long" or length.lower() == "l":
            hero.resting = "Resting"

            if "Speed Rest" in hero.status:
                hero.status.remove("Speed Rest")
                resting_clock = datetime.now() + timedelta(minutes=2)
                hero.alarm_clock = resting_clock.strftime(t_format)
                await ctx.send(block_text(f"{hero.name} has found a warm cabin (2 minutes)"))
                await sleep(120)

            else:
                await ctx.send(block_text(f"{hero.name} has set up camp (10 minutes)"))
                resting_clock = datetime.now() + timedelta(minutes=10)
                hero.alarm_clock = resting_clock.strftime(t_format)
                await sleep(600)

            if hero.resting == "Not Resting":
                return

            hero.resting = "Not Resting"

            # Immense removal
            if "Immense" in hero.status:
                hero.status.remove("Immense")
                hero.bonus_hp -= hero.immense_hp
                if hero.current_hp > hero.max_hp + hero.bonus_hp:
                    hero.current_hp = hero.max_hp + hero.bonus_hp
                delattr(hero, "immense_hp")

            # Return HP and EP to maxs
            hero.current_ep = hero.max_ep + hero.bonus_ep
            hero.current_hp = hero.max_hp + hero.bonus_hp

            await ctx.send(block_text(f"{hero.name} feels rested!\n"
                                      f"{hero.current_hp} / {hero.max_hp + hero.bonus_hp}"))


@bot.command(aliases=["rtg"])
async def resting(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, the_shop, general_chat, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        t_format = "%b %d %Y at %I:%M%p"

        if hero.resting == "Resting":
            alarm_clock = datetime.strptime(hero.alarm_clock, t_format)
            now = datetime.now()
            diff = alarm_clock - now
            time_left = int(diff / timedelta(minutes=1))
            await ctx.send(block_text(f"{hero.name} is still resting! {time_left} minutes left."))
        else:
            await ctx.send(block_text(f"{hero.name} is currently awake! Go kill some monsters!"))
        return


@bot.command(aliases=["sl"])
async def sell(ctx, item):
    if ctx.channel.id in [the_shop]:
        item = item.title()

        item = shortcut_return(item)

        improved = False
        if item[:8] == "Improved":
            improved = True
            item = item[9:]

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item_object = Items()

        if item in item_object.tier1_items:
            item_tier = 1
            item_value = random.randint(100, 300)
        elif item in item_object.tier2_items:
            item_tier = 2
            item_value = random.randint(200, 400)
        elif item in item_object.tier3_items:
            item_tier = 3
            item_value = random.randint(600, 1000)
        elif item in item_object.tier4_items:
            item_tier = 4
            item_value = random.randint(1000, 1400)
        else:
            print("Item not found in sell command item distribution")
            await ctx.send(code_block("I'm not interested"))
            return

        if improved:
            item = f"Improved {item}"
            item_value = math.ceil(item_value * 1.6)

        if item in hero.inventory:
            hero.inventory.remove(item)
            hero.gold += item_value
            await ctx.send(embed=sell_embed(item, item_value, item_tier))
            return
        else:
            await ctx.send(code_block(f"{item} not found in your inventory"))


@bot.command()
async def set_hero_image(ctx, url):
    """
    Set hero card image from web url
        ex. .set_hero_image "https://i.ibb.co/yRPmqJ6/0000.jpg"
    ___
    :param url: image link in raw url format
    """
    if ctx.channel.id in [welcome, beyond_the_gates, the_meadow, general_chat, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        hero.link = url
        await ctx.send(block_text("Image set"))

    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        pass

    else:
        await sleep(2)
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        if hero.link != "https://i.ibb.co/yRPmqJ6/0000.jpg":
            await ctx.send(block_text(f"Your image has already been set! You will need to wait until "
                                      f"after the tutorial to set a new image."))
            return

        hero.link = url
        hero.image_set = True
        await ctx.send(block_text("Image set"))

        hero.training_stage = 2
        await ctx.send(
            embed=fight_train_embed(
                title="Fight Training",
                text="Great! Now your hero has a picture to represent them in the Maw.\n\n"
                     "**Awwyyyggghhh!** An Imp?! Lets fight it! Use the command **.fight imp** to start a "
                     "round of combat!"))


@bot.command(aliases=["store"])
async def shop(ctx):
    pass
    if ctx.channel.id in [the_shop]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        # Check if raiding

        if hero.raiding:
            await ctx.send(code_block("There is no Shop in The Last Bastion! Complete your raid to do the shop or"
                                      " .end_raid to end early."))
            return

        await ctx.send(embed=shop_embed(SHOP, hero))


@bot.command(aliases=["s"])
async def stats(ctx):
    """
    Shows your hero stats
        ex. .stats "HeroName"
    """
    try:
        hero_name = set_hero_user(ctx.message.author.id)

    except FileNotFoundError:
        await ctx.send(block_text(f"You do not have a hero set! Summon a hero!"))
        return

    hero = get_hero(HERO_LIST, hero_name)

    await ctx.send(embed=stat_embed(hero))


@bot.command(aliases=["st"])
async def status(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        statusi = [status for status in hero.status if status not in ["AotP", "AotB", "AotL", "AotA", "Normal"]]
        joined_status = ", ".join(statusi)
        await ctx.send(code_block(f"{hero.name}'s current status effects:\n{joined_status}"))


@bot.command()
async def summon_hero(ctx, name, class_):
    if ctx.channel.id == welcome:
        return

    name = name.title()
    name_taken = check_if_taken(name)
    name_banned = check_if_banned(name)

    if name_banned:
        await ctx.send(block_text(f"You have chosen a banned name, please choose a different name."))
        return

    for char in name:
        if char.lower() not in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                                "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]:
            await ctx.send(block_text(f"Your new name may only be alphabetical, names may not contain "
                                      f"numbers or symbols."))
            return

    for hero in HERO_LIST:
        if hero.owner == ctx.message.author.id and ctx.message.author.id != admin:
            await ctx.send(block_text(f"You are already attuned to {hero.name}."))
            return

    if name_taken:
        await ctx.send(block_text(f"That name is already taken."))
        return

    if class_.lower() == "dark druid":
        await ctx.send(code_block("You may not summon the dark druid class until "
                                  "you have spent sufficient time in the Maw (ascend at least 3 times)"))
        return

    elif class_.lower() == "mage":
        await ctx.send(code_block("You may not summon the mage class until "
                                  "you have spent sufficient time in the Maw (ascend at least 1 time"))
        return

    elif class_.lower() == "monk":
        await ctx.send(code_block("You may not summon the monk class until "
                                  "you have spent sufficient time in the Maw (ascend at least 1 time"))
        return

    # Get discord id
    user_id = ctx.message.author.id
    user_name = ctx.message.author.name

    # Construct hero object
    hero = HeroBuilder()

    # Set hero object to desired class
    hero.new_class_set(class_, name, user_id)

    # Save hero to file
    save_hero(hero)

    # Append to hero list
    HERO_LIST.append(hero)

    # Check if user is existing player
    returning_user = False
    if exists(f"users/{user_id}.json"):
        returning_user = True

    # Create User file
    add_user_data(ctx.message.author, hero.name)

    await ctx.send(block_text(f"{user_name} has attuned to {name}."))
    await ctx.send(embed=stat_embed(hero))

    if not returning_user:
        hero.training_stage = 1
        await ctx.send(
            embed=standard_embed(
                title="Hero Summoned!",
                text=f"Fantastic! The {hero.class_} is pretty "
                     f"fun. I think you'll like it. Now lets set up an image for your hero."
                     f" Use the command: **.set_hero_image** followed by "
                     f"a URL link to your preferred image.\n\n"
                     f"If you dont want to find one, you can use this one:\n\n"
                     f"**copyable message below**\n\n"
                     f"You can change it at any time by calling the same "
                     f"command with a new URL"))
        await ctx.send("```.set_hero_image https://c.tenor.com/4V2-UCVfPbIAAAAC/jinx-jinx-arcane.gif```")


@bot.command()
async def classes(ctx):
    """
    Admin use only
    """
    if ctx.message.author.id == admin:
        def class_card_embed():
            base = discord.Embed(
                title=f"__Tank__",
                colour=discord.Colour.gold(),
                description=f"The Tanks of the Maw excel in taking damage and controlling monsters. Tanks assist "
                            f"other heroes by defending critical attacks, stunning targets, and are able to scrap "
                            f"demons by returning their own damage against them. The tank class has elevated HP "
                            f"and Defense")
            base.set_author(name="Maw Class Card",
                            icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
            base.add_field(name="Shieldbash",
                           value="Stuns a target monster for one round of combat. The next attack against the monster by any "
                                 "hero will automatically be set to critically hit.",
                           inline=False)
            base.add_field(name="Retribution, Lv10",
                           value="Returns 50% of damage taken back at the attacker as true damage",
                           inline=False)
            base.add_field(name="Martyr, Lv15",
                           value="Sets up your hero for a chance to block incoming damage any hero receives in combat. "
                                 "Returns a significant amount of experience upon triggering.",
                           inline=False)
            base.add_field(name="Max Rolls - Initial(Level up)",
                           value="HP: 80-100(10-15)\n"
                                 "Attack: 10-16(3-6)\n"
                                 "Defense: 10-16(3-4)\n"
                                 "Crit: 1.5(0.1)\n"
                                 "EP: 1 per 4 levels",
                           inline=False)
            base.set_image(
                url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/8b92c598-a4c8-46f6-a45d-584bc5406523/d5d1bv6-313e9712-9b3c-43ad-853e-a02a24b7ebf0.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzhiOTJjNTk4LWE0YzgtNDZmNi1hNDVkLTU4NGJjNTQwNjUyM1wvZDVkMWJ2Ni0zMTNlOTcxMi05YjNjLTQzYWQtODUzZS1hMDJhMjRiN2ViZjAuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.yLgO9St9l5k63y7DYlvuJWtVn559kHrNjpmuTNd_Rik")
            return base

        await ctx.send(embed=class_card_embed())

        def class_card_embed():
            base = discord.Embed(
                title=f"__Fighter__",
                colour=discord.Colour.blurple(),
                description=f"The Fighters of the Maw excel in steady damage and sustain. Fighters aim to consistenty "
                            f"engage monsters through any difficulty and swiftly spread damage throughout the Maw. "
                            f"Fighters reduce target armor, quickly slay low health creatures, and cleave through "
                            f"finished targets.")
            base.set_author(name="Maw Class Card",
                            icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
            base.add_field(name="Helmbreaker",
                           value="Reduces target monster defense by half of its original value.",
                           inline=False)
            base.add_field(name="Executor, Lv10",
                           value="Doubles rolled damage against monsters with less than 40% HP remaining",
                           inline=False)
            base.add_field(name="Art Of War, Lv15",
                           value="All damage in excess of a monster's remaining HP is instead applied to another random "
                                 "monster.",
                           inline=False)
            base.add_field(name="Max Rolls - Initial(Level up)",
                           value="HP: 65-85(6-12)\n"
                                 "Attack: 16-20(5-10)\n"
                                 "Defense: 6-8(2-3)\n"
                                 "Crit: 1.5(0.1)\n"
                                 "EP: 1 per 4 levels",
                           inline=False)
            base.set_image(url="https://artfiles.alphacoders.com/318/31890.jpg")
            return base

        await ctx.send(embed=class_card_embed())

        def class_card_embed():
            base = discord.Embed(
                title=f"__Assassin__",
                colour=discord.Colour.dark_red(),
                description=f"The Assassins of the Maw excel in the output of huge damage numbers but lack in the "
                            f"sustain necessary for elongated combat. Assassins aim to set up for huge attacks, or "
                            f"to slaughter monsters using EP. Assassins attempt to kill targets outright "
                            f"through assassinations, stalking, or may even kill swathes of creatures in one swoop.")
            base.set_author(name="Maw Class Card",
                            icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
            base.add_field(name="Assassinate",
                           value="Attempts to assassinate a target monster, fail rate scales with rank of monster. "
                                 "Instantly defeats monster on successful roll.",
                           inline=False)
            base.add_field(name="Stalk, Lv10",
                           value="Halves assassination fail rates, automatically sets the next attack to a critical strike.",
                           inline=False)
            base.add_field(name="Mass Casualty, Lv15",
                           value="Attempts an assassination on all creatures currently on the field.",
                           inline=False)
            base.add_field(name="Max Rolls - Initial(Level up)",
                           value="HP: 50-70(4-8)\n"
                                 "Attack: 22-28(6-12)\n"
                                 "Defense: 4-7(1-2)\n"
                                 "Crit: 1.5(0.1-0.2)\n"
                                 "EP: 1 per 4 levels",
                           inline=False)
            base.set_image(
                url="https://64.media.tumblr.com/1444c3944a946f5b321239f79981f78d/tumblr_nmynpynxkG1tb8cbpo1_1280.jpg")
            return base

        await ctx.send(embed=class_card_embed())

        def class_card_embed():
            base = discord.Embed(
                title=f"__Cleric__",
                colour=discord.Colour.teal(),
                description=f"The Clerics of the Maw excel in sustaining themselves or others for elongated combat. "
                            f"Clerics are midrange on all stats. Clerics aim to heal through harder fights, while "
                            f"buffing themselves or others with various boons. At higher levels Clerics may choose "
                            f"to transform into either a combat or support oriented endgame class.")
            base.set_author(name="Maw Class Card",
                            icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
            base.add_field(name="Regenerate",
                           value="Heals a target hero for 75% of their maximum HP instantly.",
                           inline=False)
            base.add_field(name="Obsecrate, Lv10",
                           value="Casts one of five random boons:\n"
                                 "Arawn Blessing: Prevents Death's next occurrence\n"
                                 "Tempus Blessing: Temporarily doubles hero attack stat\n"
                                 "Estanna Blessing: Greatly reduces rest time\n"
                                 "Baal Blessing: Next target hero's attack is automatically critical\n"
                                 "Tymora Blessing: Instantly grants a hero an item",
                           inline=False)
            base.add_field(name="Divinity, Lv15",
                           value="Allows the selection of Light or War domain specialties. War domain greatly increases "
                                 "battle stats but removes Regenerate ability. Light domain increases EP, gives "
                                 "Celestial Consult ability, and provides XP on each spell cast.",
                           inline=False)
            base.add_field(name="Celestial Consult, Light Domain",
                           value="Blesses a hero with doubled XP on the next one to three fight XP rewards.",
                           inline=False)
            base.add_field(name="Max Rolls - Initial(Level up)",
                           value="HP: 65-85(6-12)\n"
                                 "Attack: 12-18(3-8)\n"
                                 "Defense: 8-12(1-2)\n"
                                 "Crit: 1.5(0.1)\n"
                                 "EP: 1 per 4 levels",
                           inline=False)
            base.set_image(url="https://i.pinimg.com/originals/dd/31/45/dd31457bed7279c93a0ebb6e4a028dad.jpg")
            return base

        await ctx.send(embed=class_card_embed())

        def class_card_embed():
            base = discord.Embed(
                title=f"__Artificer__",
                colour=discord.Colour.magenta(),
                description=f"The Artificers of the Maw excel in item manipulation and practiced aim. Artificers have "
                            f"midrange attack and defense, with elevated HP and critical multiplier. Artificers "
                            f"attempt to create an overwhelming supply of magic items, and use their crafting "
                            f"abilities to improve the effects of those items, or simply blow them up for maximum "
                            f"damage.")
            base.set_author(name="Maw Class Card",
                            icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
            base.add_field(name="Intuition",
                           value="Searchs for hidden items on living monsters, or upgrades held items.",
                           inline=False)
            base.add_field(name="Tinker, Lv10",
                           value="Improves a random item in the Artificer inventory, greatly enhancing its effects.",
                           inline=False)
            base.add_field(name="Detonate, Lv15",
                           value="Explodes a target monsters held item for massive individual target damage.",
                           inline=False)
            base.add_field(name="Max Rolls - Initial(Level up)",
                           value="HP: 80-105(12-15)\n"
                                 "Attack: 12-18(4-6)\n"
                                 "Defense: 6-10(2-3)\n"
                                 "Crit: 1.5(0.1, 0.2)\n"
                                 "EP: 1 per 3 levels",
                           inline=False)
            base.set_image(url="https://i.pinimg.com/originals/b2/ae/32/b2ae32636f8f09ce279c12c229a7d79b.jpg")
            return base

        await ctx.send(embed=class_card_embed())

        def class_card_embed():
            base = discord.Embed(
                title=f"__Mage__",
                colour=discord.Colour.blue(),
                description=f"The Mages of the Maw excel in reaping demons through the expenditure of energy. "
                            f"Mages are unable to prolonged physical combat but are adept at using EP to cast "
                            f"damaging spells against field and raid monsters. Mages start with the ability "
                            f"to recover energy points, as well to cast a single target damaging spell. At higher "
                            f"levels, Mages can obliterate entire fields of monsters, empower themselves with "
                            f"their own energy or manipulate the field monster ranks to their whim.")
            base.set_author(name="Maw Class Card",
                            icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
            base.add_field(name="Magic Missile",
                           value="Deals moderate damage to a single target. May critically hit. "
                                 "Damage scales with Mage Levels",
                           inline=False)
            base.add_field(name="Fireball, Lv5",
                           value="Strikes 1 target monster, and 4 random monsters for moderate damage. Damage scales "
                                 "with Mage levels.",
                           inline=False)
            base.add_field(name="Battlemage, Lv10",
                           value="Exchanges EP for attack/HP/defense/crit. Bonuses are lost if a monster rolls a "
                                 "critical hit, or a spell is cast",
                           inline=False)
            base.add_field(name="Max Rolls - Initial(Level up)",
                           value="HP: 40-60(5-10)\n"
                                 "Attack: 10-16(2-3)\n"
                                 "Defense: 4-8(1-2)\n"
                                 "Crit: 1.5(0.1)\n"
                                 "EP: 1 per 2 levels",
                           inline=False)
            base.set_image(url="https://i.pinimg.com/originals/40/60/ea/4060ea5f1414c7a06eedd00dd9c6e832.jpg")
            return base

        await ctx.send(embed=class_card_embed())

        def class_card_embed():
            base = discord.Embed(
                title=f"__Monk__",
                colour=discord.Colour.from_rgb(255, 255, 255),
                description=f"The Monks of the maw excel at customized skill through directed traiing, and the relentless "
                            f"dismantling of monsters through combat. Monks begin with **Disarming Strikes** passive buff,"
                            f" which reduces a monsters attack and defense on every hit. As monks level up, they do not"
                            f" gain combat stats naturally, but pool them for meditation, allowing a monk to allocate "
                            f"their combat points as they see fit. Higher level monks gain the ability to detonate "
                            f"their prey upon death, as well as smash individual targets with a high damage single "
                            f"target ability. As monks reach milestones, they may take a pilgrimage, allowing a total "
                            f"reset of allocated stat points.")
            base.set_author(name="Maw Class Card",
                            icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
            base.add_field(name="Disarming Strikes",
                           value="Reduces target monster attack and defense on hit. Reduction starts at 12% and scales by 5% "
                                 "every 5 levels.",
                           inline=False)
            base.add_field(name="Meditation, Lv2",
                           value="Allows the Monk to spend accrued combat stat points gained by leveling up. Points are "
                                 "spent to boost attack, max health, and defense stats.",
                           inline=False)
            base.add_field(name="Ki Bomb, Lv10",
                           value="Plants a bomb of pure chakra within a target monster set to detonate on the death of "
                                 "target creature, heavily damaging two other random targets on the field. Damage scales "
                                 "with every level.",
                           inline=False)
            base.add_field(name="Dragon Kick, Lv15",
                           value="Deals 20% of a targets max health to the target, and damages one random additional target "
                                 "on the field for 100% of the original targets max health. If the target is afflicted by "
                                 "Ki Bomb, Dragon Kick will automatically detonate the charge.",
                           inline=False)
            base.add_field(name="Monastic Pilgrimage, Lv 8, 16, 20, 30",
                           value="Resets the Monk's attack, max health and defense stats to 1 and returns all earned "
                                 "meditation to be respent with meditation.",
                           inline=False)
            base.add_field(name="Max Rolls - Initial(Level up)",
                           value="HP: 40-60(0)\n"
                                 "Attack: 16-24(0)\n"
                                 "Defense: 8-14(0)\n"
                                 "Crit: 1.5(0.1)\n"
                                 "EP: 1 per 5 levels",
                           inline=False)
            base.set_image(url="https://i.pinimg.com/originals/a2/14/90/a21490ace77ec8dd41513e4cc25e1958.png")
            return base

        await ctx.send(embed=class_card_embed())

        def class_card_embed():
            base = discord.Embed(
                title=f"__Dark Druid__",
                colour=discord.Colour.dark_purple(),
                description=f"The Dark Druids of the Maw excel in pure combat. Dark Druids start with lower base "
                            f"stats, but are empowered by the slaughter of creatures in the Maw. After the collection "
                            f"of a number of lower, higher, legendary, and apex rank monsters, the Dark Druid morphs "
                            f"using rituals into more powerful monsters with various stat bonuses. Prolonging Dark "
                            f"Druid rituals strengthens the effects of the one time bonuses obtained. As evolutions "
                            f"are obtained, Dark Druids can deal massive damage, bleeding, extreme resistances, "
                            f"extreme damage buffs, and eventually, a cataclysmic explosion of energy from the Maw "
                            f"itself.")
            base.set_author(name="Maw Class Card",
                            icon_url="https://media.istockphoto.com/illustrations/dragon-head-on-stone-background-illustration-id1159980027")
            base.add_field(name="Maw Oath",
                           value="Dark Druids can affirm fealty to the Maw for a minor heal and defense buff",
                           inline=False)
            base.add_field(name="Cognition",
                           value="An inward review details current buffs and ritual effects",
                           inline=False)
            base.add_field(name="Predator Ritual/Rake Claws, **???**",
                           value="Ritual Effect: Multiplies attack power by 25%\n"
                                 "Deals maximum damage to a target monster and causes two turns of bleeding damage.",
                           inline=False)
            base.add_field(name="Behemoth Ritual/Become Immense, **???**",
                           value="Ritual Effect: Multiplies defense power by 25%\n"
                                 "Doubles current maximum health pool until rest",
                           inline=False)
            base.add_field(name="Legend Ritual/Depraved Frenzy, **???**",
                           value="Ritual Effect: Multiplies max HP by 25%\n"
                                 "Sacrifices 20% of targets current life to add Enraged and Sharpened status effects.",
                           inline=False)
            base.add_field(name="Apex Ritual/Apex Form, **???**",
                           value="Ritual Effect: Multiplies critical multiplier and initiative by 25%\n"
                                 "Increases Apex damage, Adds auras in combat, empowers ability effects.",
                           inline=False)
            base.add_field(name="Max Rolls - Initial(Level up)",
                           value="HP: 65-85(8-12)\n"
                                 "Attack: 18-22(7-10)\n"
                                 "Defense: 8-12(2-3)\n"
                                 "Crit: 1.5(0.1)\n"
                                 "EP: 1 per 4 levels",
                           inline=False)
            base.set_image(url="https://i.pinimg.com/736x/62/45/28/624528415ae7b5747171969fa75a77c7.jpg")
            return base

        await ctx.send(embed=class_card_embed())


@bot.command(aliases=[])
async def test(ctx, *args):
    """
    Admin use only
    """
    hero_name = set_hero_user(ctx.message.author.id)
    hero = get_hero(HERO_LIST, hero_name)
    print(hero.sp_atk)


@bot.command(pass_context=True)
async def train(ctx):
    try:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

    except FileNotFoundError:
        classes = bot.get_channel(id=912138737377488967)
        await ctx.send(
            embed=standard_embed(
                title="Great!",
                text="You used your first command! All commands will begin with this symbol -> . \n\n"
                     "Time to summon a hero.\n"
                     f"Head over to {classes.mention} and pick a **class**! (Dark Druid, Monk, and Mage are locked "
                     f"until you level up). Now pick a name and use the command: **.summon_hero name class**\n\n"
                     f"*ie: .summon_hero silco{random.randint(1, 999)} assassin*"))
        return

    if hero.training_stage == 4:
        if hero.class_ == "Tank":
            ability_text = "Lets use your ability 'Shieldbash'. This ability stuns any monster target for one round of " \
                           "combat.\n\nTo do that you need a monster to target. Here is a test dummy for you to try it out " \
                           "on. \n\nType: **.shieldbash dummy** to use your shieldbash ability on the test dummy."
        elif hero.class_ == "Fighter":
            ability_text = "Lets use your ability 'Helmbreaker'. This ability halves a target monster's defense " \
                           "perpetually.\n\nTo do that you need a monster to target. Here is a test dummy for you to try " \
                           "it out on.\n\nType: **.helmbreaker dummy** to use your Helmbreaker ability on the test dummy."
        elif hero.class_ == "Assassin":
            ability_text = "Lets use your ability 'Assassinate'. This ability has a chance of killing a monster instantly." \
                           "\n\nTo do that you need a monster to target. Here is a test dummy for you to try it out on.\n\n" \
                           "Type: **.assassinate dummy** to use your Assassinate ability on the test dummy."
        elif hero.class_ == "Cleric":
            ability_text = "Lets use your ability 'Regenerate'. This ability heals a target hero by 75% of their maximum health." \
                           "\n\nTo do that you need a hero target. Go ahead and heal me. \n\nType: **.regenerate maw** to use your Regenerate ability on me."
        elif hero.class_ == "Artificer":
            ability_text = "Lets use your ability 'Intuition'. This ability searches a monster for a hidden item, or tells " \
                           "you if a monster is holding an item.\n\nTo do that, you need a monster to target.Here is a " \
                           "test dummy for you to try it out on.\n\nType: **.intuition dummy** to use your Intuition ability on the test dummy."
        else:
            ability_text = "error: class not identified in ability_text class selector"

        await ctx.send(
            embed=standard_embed(
                title="Abilities",
                text=f"Now that you know how to fight with your raw strength, lets use an ability. "
                     f"Each class has their own starting ability and you will obtain more as you level up. "
                     f"{ability_text}"))

        if hero.class_ in ["Tank", "Fighter", "Assassin", "Artificer"]:
            await ctx.send(embed=dummy_monster_scanner_embed())

    elif hero.armor != "None" or hero.equipment != "None":
        await ctx.send(
            embed=standard_embed(
                title="My Hierlooms!",
                text="Don't forget to **.unequip 'cloth armor'** and **.unequip 'yamatos training katana'**!\n\n"
                     "**.uneq ca** and **.uneq ytk** for short."))

    elif hero.training_stage == 5 and hero.training_complete:

        guild = ctx.guild
        voodoo = discord.utils.get(bot.get_all_members(), id=208970082594848771)
        channel = discord.utils.get(guild.channels, id=897283326862327878)  # general chat
        delattr(hero, "training_complete")
        delattr(hero, "training_stage")

        await ctx.send(
            embed=standard_embed(
                title="Congratulations!",
                text="You made it through the training on the basics! There is so much to "
                     "learn and experience in the Maw! Play through all the classes, "
                     "top the raid leaderboard, and collect all the legendary gear!\n\n"
                     ""
                     "Maybe one day it will be you helping out a new player! "
                     "Please be courteous to others and have a good time here in the Maw. "
                     f"If you have any questions you can {voodoo.mention} or get help in "
                     f"{channel.mention}. You are now a hunter! I'll see you out there!\n\n"
                     f""
                     f"    - Voodoo",
                footer="This channel will remain open for 10 minutes before dispersing."))

        # Get member object from ctx.id
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name="Hunter")
        training_role = discord.utils.get(member.guild.roles, name=f"Fledgling {ctx.message.author.name}")

        # Add hunter role to member
        await member.add_roles(role)
        await member.remove_roles(training_role)
        await training_role.delete()

        # Notifications
        channel = discord.utils.get(guild.channels, id=893607108568817675)
        await channel.send(f"{member.mention} has completed their training!")
        await sleep(600)

        # Remove channel after 10 minutes
        training_channel = discord.utils.get(guild.channels, id=ctx.channel.id)
        await training_channel.delete()


@bot.command(aliases=["uq", "uneq"])
async def unequip(ctx, equippable):
    """
    Equips a permanent item from your inventory into your equipment slot. ex. "rod of lordly might"
    :param item: The name of a permanent item from your inventory,
    """
    if ctx.channel.id in [beyond_the_gates, the_meadow, general_chat, the_shop, raid_1, raid_2, raid_3,
                          testing_home, beyond_the_battlefield, heart_of_the_maw]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        legendary = Legendary()
        armors = Armors()

        # Shortcuts
        equippable = shortcut_return(equippable.title())

        if equippable in legendary.legends:
            if hero.equipment != equippable:
                await ctx.send(block_text(f"You do not have {equippable} equipped."))
                return

            if equippable == "Rod Of Lordly Might":
                # Get Mode
                mode = hero.equipment_mode

                del hero.sp_atk["Transform"]
                legendary.rod_of_lordly_might(mode_set=mode)

            elif equippable == "Natures Mantle":
                legendary.natures_mantle()

            elif equippable == "Vestige Blade":
                legendary.vestige_blade()

            elif equippable == "Chidori":
                legendary.chidori(hero)

            elif equippable == "Forbidden Fruit":
                legendary.forbidden_fruit(hero)

            elif equippable == "Yamatos Training Katana":
                legendary.yamatos_training_katana()

            else:
                await ctx.send(f"{equippable} not found, notify the admin")
                return

            hero.equipment = "None"
            hero.armory.append(equippable)

            legendary.unequip(hero)
            await ctx.send(block_text(f"{hero.name} has unattuned from the {equippable}!"))

        if equippable in armors.armors:
            if hero.armor != equippable:
                await ctx.send(block_text(f"You do not have {equippable} equipped."))
                return

            if equippable == "Cloth Armor":
                armors.cloth_armor()

            elif equippable == "Leather Armor":
                armors.leather_armor()

            elif equippable == "Mail Armor":
                armors.mail_armor()

            elif equippable == "Plate Armor":
                armors.plate_armor()

            elif equippable == "Bag Of Holding":
                if len(hero.inventory) > 10:
                    await ctx.send(block_text(f"You are carrying too many items to release the Bag of Holding!"))
                    return

                armors.bag_of_holding()

            else:
                await ctx.send(f"{equippable} not found, notify the admin")
                return

            armors.unequip(hero)
            await ctx.send(block_text(f"{hero.name} has removed their {equippable}."))

            hero.armor = "None"
            hero.armory.append(equippable)

    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        return

    else:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        legendary = Legendary()
        armors = Armors()

        # Shortcuts
        equippable = shortcut_return(equippable.title())

        if equippable in legendary.legends:
            if hero.equipment != equippable:
                await ctx.send(block_text(f"You do not have {equippable} equipped."))
                return

            if equippable == "Yamatos Training Katana":
                legendary.yamatos_training_katana()

            else:
                await ctx.send(f"{equippable} not found, notify the admin")
                return

            hero.equipment = "None"

            legendary.unequip(hero)
            await ctx.send(block_text(f"{hero.name} has unattuned from the {equippable}!"))

            hero.training_stage -= 1
            hero.training_complete = True

            await ctx.send(
                embed=standard_embed(
                    title="Neat!",
                    text="You will come across a large number of legendary pieces and "
                         "armor in the game. Feel free to play with them all. If you "
                         "haven't equipped/unequipped your armor yet, be sure to do that "
                         "before continuing on. Use the command: **.train** to finalize "
                         "your training and become a hunter!"
                )
            )

        if equippable in armors.armors:
            if hero.armor != equippable:
                await ctx.send(block_text(f"You do not have {equippable} equipped."))
                return

            if equippable == "Cloth Armor":
                armors.cloth_armor()

            else:
                await ctx.send(f"{equippable} not found, notify the admin")
                return

            armors.unequip(hero)
            await ctx.send(block_text(f"{hero.name} has removed their {equippable}."))

            hero.armor = "None"
            hero.training_stage -= 1
            hero.training_complete = True

            await ctx.send(
                embed=standard_embed(
                    title="Neat!",
                    text="You'll find armor very helpful as you work your way through "
                         "monster ranks. If you "
                         "haven't equipped/unequipped your Legendary Katana yet, "
                         "be sure to do that before continuing on. Use the command: "
                         "**.train** to finalize your training and become a hunter!"
                )
            )


# ITEM COMMANDS _______________________________________________________________________________________

# Set formatter to get item title from command


def get_item_from_command(command):
    ctx_to_list = command.split(".")
    ctx_to_item = ctx_to_list[1].split(" ")
    command_item = ctx_to_item[0]
    return shortcut_return(command_item.title())


def set_directory_from_channel(hero_name, channel_id):
    if channel_id in [beyond_the_gates, the_meadow, testing_home]:
        return MONSTER_LIST
    elif channel_id == beyond_the_battlefield:  # beyond the bf
        return MONSTER_LIST2
    elif channel_id == heart_of_the_maw:  # heart of the maw
        return MONSTER_LIST3
    elif channel_id in [raid_1, raid_2, raid_3]:
        return MASTER_RAID_DICT[hero_name].monsters
    else:
        print("Directory not set, channel information not included")
        return


@bot.command(aliases=["bt"])
async def bardic_tale(ctx, target_name):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item = get_item_from_command(ctx.message.content)

        if item == "Bardic_Tale":
            item = "Bardic Tale"

        target_name = target_name.title()

        if hero.raiding:
            await ctx.send(block_text("There is no time to speak to bards while raiding!"))
            return

        for char in target_name:
            if char.lower() not in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                                    "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]:
                await ctx.send(block_text(f"Your new name may only be alphabetical, names may not contain {char}"))
                return

        if check_if_taken(target_name):
            await ctx.send(block_text("That name is already taken. Try a new name."))
            return

        if check_if_banned(target_name):
            await ctx.send(block_text("Pick a different name."))
            return

        if target_name == hero.name:
            await ctx.send(block_text(f"{target_name} is currently your hero's name"))
            return

        # Hero has item
        in_possession = check_inventory(hero.inventory, item)
        if not in_possession:
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        with open(f"users/{hero.owner}.json", "r") as f:
            user_data = json.load(f)

        user_data["user_hero"] = target_name

        with open(f"users/{hero.owner}.json", "w") as f:
            json.dump(user_data, f, indent=2)

        old_name = hero.name
        hero.name = target_name

        os.remove(f"characters/{old_name}.json")

        result = f"It seems the Bards of the Maw have mixed up {hero.name}'s name as they were regaling " \
                 f"their tales..."

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["bd", "impbd", "improved_blood_dagger"])
async def blood_dagger(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        # Get item for shortcuts
        item = get_item_from_command(ctx.message.content)

        if item == "Blood_Dagger":
            item = "Blood Dagger"
        elif item == "Improved_Blood_Dagger":
            item = "Improved Blood Dagger"

        target = shortcut_return(target.title())

        # Hero has item
        in_possession = check_inventory(hero.inventory, item)
        if not in_possession:
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Blood Dagger":
            improved = True

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        await ctx.send(code_block(f"How deep do you cut? Max HP Sacrifice: {hero.current_hp - 1}"))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and \
                   int(msg.content) < hero.current_hp

        try:
            msg = await bot.wait_for("message", check=check, timeout=13)
        except TimeoutError:
            await ctx.send(code_block(f"{hero.name} has sheathed the blood dagger"))
            return

        dmg = math.ceil(int(msg.content) * 2.5)

        monster.current_hp -= dmg
        if monster.current_hp < 0:
            monster.current_hp = 0

        if hero.name not in monster.attacked_by:
            monster.attacked_by.append(hero.name)

        if hero.raiding:
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        # Remove sacrifice HP
        sacrifice = int(msg.content)

        bleeding = False
        if f"Bleeding" in monster.status:
            return_hp = random.randint(sacrifice // 2, sacrifice)
            hero.current_hp += return_hp
            if hero.current_hp > hero.max_hp + hero.bonus_hp:
                hero.current_hp = hero.max_hp + hero.bonus_hp
            bleeding = True
        else:
            hero.current_hp -= sacrifice

        # Improved effect block
        if improved:
            dmg *= 2
            floor_value = math.ceil(sacrifice / 3)
            returned_hp = random.randint(floor_value, sacrifice)
            hero.current_hp += returned_hp
            if hero.current_hp > hero.max_hp + hero.bonus_hp:
                hero.current_hp = hero.max_hp + hero.bonus_hp

            if bleeding:
                result = f"{hero.name} sacrifices **{sacrifice}** HP from the bleeding monster to catapult a Great Sanguine Blade for **{dmg}** damage at " \
                         f"**{monster.name}**!\n\n" \
                         f"**{hero.name}**\n" \
                         f"{hero.current_hp}/{hero.max_hp + hero.bonus_hp} HP\n" \
                         f"Vampiric: **{returned_hp}** HP returned.\n\n" \
                         f"**{monster.name}**\n" \
                         f"*{monster.current_hp}/{monster.max_hp}* HP"
            else:
                result = f"{hero.name} sacrificed **{sacrifice}** health to catapult a Great Sanguine Blade for **{dmg}** damage at " \
                         f"**{monster.name}**!\n\n" \
                         f"**{hero.name}**\n" \
                         f"{hero.current_hp}/{hero.max_hp + hero.bonus_hp} HP\n" \
                         f"Vampiric: {returned_hp} HP returned.\n\n" \
                         f"**{monster.name}**\n" \
                         f"*{monster.current_hp}/{monster.max_hp}* HP"
        else:
            if bleeding:
                result = f"{hero.name} sacrifices **{sacrifice}** HP from the bleeding monster to sling a Blood Dagger for **{dmg}** damage at " \
                         f"**{monster.name}**!\n\n" \
                         f"**{hero.name}**\n" \
                         f"{hero.current_hp}/{hero.max_hp + hero.bonus_hp} HP\n\n" \
                         f"**{monster.name}**\n" \
                         f"*{monster.current_hp}/{monster.max_hp}* HP"
            else:
                result = f"{hero.name} sacrificed **{sacrifice}** health to sling a Blood Dagger for **{dmg}** damage at " \
                         f"**{monster.name}**!\n\n" \
                         f"**{hero.name}**\n" \
                         f"{hero.current_hp}/{hero.max_hp + hero.bonus_hp} HP\n\n" \
                         f"**{monster.name}**\n" \
                         f"*{monster.current_hp}/{monster.max_hp}* HP"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["impbob", "bob", "improved_blood_of_berserker"])
async def blood_of_berserker(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item = get_item_from_command(ctx.message.content)

        if item == "Improved_Blood_Of_Berserker":
            item = "Improved Blood Of Berserker"
        elif item == "Blood_Of_Berserker":
            item = "Blood Of Berserker"

        if target is None:
            target = hero.name
        else:
            target = target.title()

        # Verify target hero present
        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        # Hero has item
        in_possession = check_inventory(hero.inventory, item)
        if not in_possession:
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Blood Of Berserker":
            improved = True

        # Cast item
        target_hero = get_hero(HERO_LIST, target)

        if improved:
            target_hero.status.append("Enraged Berserker")

        else:
            target_hero.status.append("Berserker")

        # Add item use to raid data
        if hero.raiding:
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        # Set result text
        if improved:
            if target_hero.name == hero.name:
                result = f"{target_hero.name} splashed themselves with Blood Of an Elder Berserker! Next " \
                         f"attack damage roll **tripled!**"
            else:
                result = f"{hero.name} splashed {target_hero.name} with Blood Of an Elder Berserker! " \
                         f"Next attack damage roll **tripled!**"
        else:
            if target_hero.name == hero.name:
                result = f"{target_hero.name} splashed themselves with Blood Of Berserker! Next " \
                         f"attack damage roll **doubled!**"
            else:
                result = f"{hero.name} splashed {target_hero.name} with Blood Of Berserker! Next " \
                         f"attack damage roll **doubled!**"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["impdb", "db", "improved_decay_bomb"])
async def decay_bomb(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        item = get_item_from_command(ctx.message.content)

        if item == "Decay_Bomb":
            item = "Decay Bomb"
        elif item == "Improved_Decay_Bomb":
            item = "Improved Decay Bomb"

        target = shortcut_return(target.title())

        # Hero has item
        in_possession = check_inventory(hero.inventory, item)
        if not in_possession:
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Decay Bomb":
            improved = True

        # Target is present
        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        if improved:
            reduction = monster.atk // 2
        else:
            reduction = monster.atk // 3

        selected = select_random_monster(2, current_mon_directory, monster.name)
        selected.append(monster)

        for mon_object in selected:
            if mon_object == "None":
                selected.remove(mon_object)
                continue
            mon_object.atk -= reduction

            if mon_object.atk < 0:
                mon_object.atk = 1

            mon_object.status.append("Decayed")

        # Add item use to raid data
        if hero.raiding:
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        affected = ', '.join([mon.name for mon in selected])

        if len(selected) == 1:
            result = f"{affected} is poisoned by a noxious cloud! Monster **attack** stats" \
                     f" reduced by **{reduction}** points\n"
        else:
            result = f"{affected} are poisoned by a noxious cloud! Monster **attack** stats" \
                     f" reduced by **{reduction}** points\n"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["ek", "impek", "improved_eldritch_keybox"])
async def eldritch_keybox(ctx, target_key):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item = get_item_from_command(ctx.message.content)

        if item == "Eldritch_Keybox":
            item = "Eldritch Keybox"
        elif item == "Improved_Eldritch_Keybox":
            item = "Improved Eldritch Keybox"

        target_key = shortcut_return(target_key.title())

        # Hero has item
        in_possession = check_inventory(hero.inventory, item)
        if not in_possession:
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Eldritch Keybox":
            improved = True

        if target_key not in ["Dimensional Key", "Tortoise Key", "Blood-Soaked Key", "Mountain Key"]:
            await ctx.send(code_block(f"{target_key} is not a valid key for the Eldritch Keybox"))
            return

        count = 0
        for key in hero.keys:
            if key == target_key:
                count += 1

        if improved and count < 2:
            await ctx.send(code_block(f"You need at least two {target_key}s to use the Improved Eldritch Keybox"))
            return

        elif count < 3:
            await ctx.send(code_block(f"You need at least three {target_key}s to use the Eldritch Keybox"))
            return

        keyring = ["Blood-Soaked Key", "Mountain Key", "Tortoise Key", "Dimensional Key"]
        for key in hero.keys:
            if key in keyring:
                keyring.remove(key)

        if improved:
            for i in range(2):
                hero.keys.remove(target_key)
            key_count = 2
            new_key = random.choice(keyring)
            hero.keys.append(new_key)

        else:
            for i in range(3):
                hero.keys.remove(target_key)
            key_count = 3
            new_key = random.choice(keyring)

            hero.keys.append(new_key)

        result = f"{hero.name} used {key_count} {target_key}s to open an Eldritch Keybox, and found a {new_key}!"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["impfs", "fs", "improved_fireball_scroll"])
async def fireball_scroll(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        item = get_item_from_command(ctx.message.content)

        if item == "Fireball_Scroll":
            item = "Fireball Scroll"
        elif item == "Improved_Fireball_Scroll":
            item = "Improved Fireball Scroll"

        target = shortcut_return(target.title())

        # Hero has item
        in_possession = check_inventory(hero.inventory, item)
        if not in_possession:
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Fireball Scroll":
            improved = True

        # Target is present
        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        # Roll improved or standard damage, remove from hp and save
        if improved:
            damage = math.ceil(monster.max_hp * 0.2)
        else:
            damage = math.ceil(monster.current_hp * 0.2)

        if monster.rank == "Apex":
            hp_calc = monster.max_hp
            damage = random.randint(math.ceil(hp_calc * 0.03), math.ceil(hp_calc * 0.04))

        monster.current_hp -= damage
        if monster.current_hp < 0:
            monster.current_hp = 0

        if hero.name not in monster.attacked_by:
            monster.attacked_by.append(hero.name)

        if hero.raiding:
            # Add item use to raid data
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        if improved:
            result = f"{hero.name} reads from an Improved Fireball Scroll, obliterating **{monster.name}** " \
                     f"and dealing **{damage}** damage! (20% max HP as damage)\n\n" \
                     f"**{monster.name}**\n" \
                     f"*{monster.current_hp}/{monster.max_hp}* HP"
        else:
            result = f"{hero.name} reads from a Fireball Scroll, blasting **{monster.name}** for **{damage}** " \
                     f"damage! (20% current HP as damage)\n\n" \
                     f"**{monster.name}**\n" \
                     f"*{monster.current_hp}/{monster.max_hp}* HP"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["gift", "impgift", "improved_gift_of_arawn"])
async def gift_of_arawn(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item = get_item_from_command(ctx.message.content)

        if item == "Gift_Of_Arawn":
            item = "Gift Of Arawn"
        elif item == "Improved_Gift_Of_Arawn":
            item = "Improved Gift Of Arawn"

        if target is None:
            target = hero.name
        else:
            target = target.title()

        # Verify target hero present
        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        # Hero has item
        in_possession = check_inventory(hero.inventory, item)
        if not in_possession:
            await ctx.send(block_text(f"{item} not found in inventory."))
            return

        # Item is improved
        improved = False
        if item == "Improved Gift Of Arawn":
            improved = True

        target_hero = get_hero(HERO_LIST, target)

        # Verify not already gifted
        if "Arawn's Gift" in target_hero.status:
            if item == "Improved Gift Of Arawn":
                pass
            else:
                await ctx.send(block_text(f"{target_hero.name} is already blessed by Arawn."))
                return

        target_hero.status.append("Arawn's Gift")

        if improved:
            target_hero.current_hp += 250

        # Add item use to raid data
        if hero.raiding:
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        if improved:
            if target == hero.name:
                result = f"{target_hero.name} has is vitalized by the Blessing of Arawn! HP restored and overhealed. " \
                         f"{target_hero.name} may now escape death.\n\n" \
                         f"*Prevents 1 instance of death from fighting/raiding*"
            else:
                result = f"{hero.name} has vitalized {target_hero.name} with a Blessing of Arawn! HP restored " \
                         f"and overhealed. {target_hero.name} may now escape death.\n\n" \
                         f"*Prevents 1 instance of death from fighting/raiding*"

        else:
            if target == hero:
                result = f"{hero.name} may now escape death.\n\n" \
                         f"*Prevents 1 instance of death from fighting/raiding*"
            else:
                result = f"{hero.name} has given {target_hero.name} the ability to escape death.\n\n" \
                         f"*Prevents 1 instance of death from fighting/raiding*"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["gb", "impgb", "improved_gravity_bomb"])
async def gravity_bomb(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        item = get_item_from_command(ctx.message.content)

        if item == "Gravity_Bomb":
            item = "Gravity Bomb"
        elif item == "Improved_Gravity_Bomb":
            item = "Improved Gravity Bomb"

        target = shortcut_return(target.title())

        # Hero has item
        if not check_inventory(hero.inventory, item):
            await ctx.send(block_text(f"{item} not found in inventory."))
            return

        # Item is improved
        improved = False
        if item == "Improved Gravity Bomb":
            improved = True

        # Target is present
        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        if monster.rank == "Apex":
            await ctx.send(block_text(f"The Apex is to powerful to be a target of {item}"))
            return

        # Roll damage
        if improved:
            dmg = math.ceil(monster.max_hp // 2)
        else:
            dmg = math.ceil(monster.max_hp // 4)

        mons_killed = []
        if hero.raiding:
            for secondary_monster in current_mon_directory:
                secondary_monster.current_hp -= dmg

                if secondary_monster.current_hp <= 0:
                    mons_killed.append(secondary_monster.name)
                    secondary_monster.current_hp = 0

            # Add item use to raid data
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        else:
            for secondary_monster in current_mon_directory:
                if secondary_monster.name == "Chest":
                    continue
                secondary_monster.current_hp -= dmg

                if secondary_monster.current_hp <= 0:
                    mons_killed.append(secondary_monster.name)
                    secondary_monster.current_hp = 0

        death_string = ", ".join(mons_killed)
        if not mons_killed:
            death_string = "No monsters killed"

        if improved:

            result = f"{monster.name} released a giant explosion of energy for **{dmg}** points of damage!\n\n" \
                     f"Monsters Killed: {death_string}"

        else:
            result = f"{monster.name} exploded for **{dmg}** points of damage, damaging other monsters of the Maw!\n\n" \
                     f"Monsters Killed: {death_string}"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["hpot", "imphpot", "improved_healing_potion"])
async def healing_potion(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item = get_item_from_command(ctx.message.content)

        if item == "Healing_Potion":
            item = "Healing Potion"
        elif item == "Improved_Healing_Potion":
            item = "Improved Healing Potion"

        if target is None:
            target = hero.name
        else:
            target = target.title()

        # Verify target hero present
        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        # Hero has item
        in_possession = check_inventory(hero.inventory, item)
        if not in_possession:
            await ctx.send(block_text(f"{item} not found in inventory."))
            return

        # Item is improved
        improved = False
        if item == "Improved Healing Potion":
            improved = True

        target_hero = get_hero(HERO_LIST, target)

        total_hp = target_hero.max_hp + target_hero.bonus_hp

        if improved:
            target_hero.current_hp += total_hp
            hp_gain = total_hp

        else:
            hp_gain = total_hp // 2
            target_hero.current_hp += hp_gain
            if target_hero.current_hp > total_hp and "Vital Tree" not in target_hero.status:
                reduced_healing = target_hero.current_hp - total_hp
                hp_gain -= reduced_healing
                target_hero.current_hp = total_hp
            elif "Vital Tree" in target_hero.status and target_hero.current_hp > total_hp * 2:
                target_hero.current_hp = (total_hp * 2)

        # Add item use to raid data
        if hero.raiding and target == hero.name:
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        if improved:
            if target_hero.name == hero.name:
                result = f"{hero.name} overcharges their vitality with an **Improved Healing Potion**, " \
                         f"instantly restoring **{hp_gain}** points of health \n\n" \
                         f"**{hero.name}\n**" \
                         f"{hero.current_hp}/{total_hp}"
            else:
                result = f"{hero.name} gave {target_hero.name} an **Improved Healing Potion**, overcharging their vitality " \
                         f"for **{hp_gain}** points of health!\n\n" \
                         f"**{target_hero.name}**\n" \
                         f"{target_hero.current_hp}/{total_hp}"
        else:
            if target_hero.name == hero.name:
                result = f"{hero.name} drank a **Healing Potion**, restoring **{hp_gain}** points of health!\n\n" \
                         f"**{hero.name}**\n" \
                         f"{hero.current_hp}/{total_hp}"
            else:
                result = f"{hero.name} gave {target_hero.name} a **Healing Potion**, restoring **{hp_gain}** points of health!\n\n" \
                         f"**{target_hero.name}**\n" \
                         f"{target_hero.current_hp}/{total_hp}"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)

    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        pass

    else:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item = get_item_from_command(ctx.message.content)

        if item == "Healing_Potion":
            item = "Healing Potion"
        elif item == "Improved_Healing_Potion":
            item = "Improved Healing Potion"

        if target is None:
            target = hero.name
        else:
            target = target.title()

        # Verify target hero present
        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        # Hero has item
        in_possession = check_inventory(hero.inventory, item)
        if not in_possession:
            await ctx.send(block_text(f"{item} not found in inventory."))
            return

        target_hero = get_hero(HERO_LIST, target)

        total_hp = target_hero.max_hp + target_hero.bonus_hp

        hp_gain = total_hp // 2

        hero.current_hp += hp_gain
        if hero.current_hp > total_hp:
            reduced_healing = hero.current_hp - total_hp
            hp_gain -= reduced_healing
            hero.current_hp = total_hp

        if target_hero.name == hero.name:
            result = f"{hero.name} drank a **Healing Potion**, restoring **{hp_gain}** points of health!\n\n" \
                     f"**{hero.name}**\n" \
                     f"{hero.current_hp}/{total_hp}"
        else:
            result = f"{hero.name} gave {target_hero.name} a **Healing Potion**, restoring **{hp_gain}** points of health!\n\n" \
                     f"**{target_hero.name}**\n" \
                     f"{target_hero.current_hp}/{total_hp}"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)

        items = bot.get_channel(id=897223062565560332)
        await ctx.send(
            embed=standard_embed(
                title="Ready For More!",
                text="There are quite a few different items in the game. If you are ever "
                     f"confused on how to use an item, or what it does, head over to {items.mention} "
                     f"for more information!\n\n"
                     f"Some items you target a monster. Some you target heroes. All you have to "
                     f"do is just input a target after the command: **(.hpot hero)**\n\n"
                     f"Some items you can also self-target. A quick way to self-target is to just cast "
                     f"the item without setting a target. Make sure "
                     f"you always have enough HP to fight or your hero becomes a hashtag. You can also "
                     f"recover health by using the **.rest** command.\n\n"
                     f"Now that you are healed up, lets see what else "
                     f"is out there! Use the command: **.monsters** to find out!"))


@bot.command(aliases=["mesmer", "impmesmer", "improved_mesmer_stone"])
async def mesmer_stone(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        item = get_item_from_command(ctx.message.content)

        if item == "Mesmer_Stone":
            item = "Mesmer Stone"
        elif item == "Improved_Mesmer_Stone":
            item = "Improved Mesmer Stone"

        target = shortcut_return(target.title())

        # Hero has item
        if not check_inventory(hero.inventory, item):
            await ctx.send(block_text(f"{item} not found in inventory."))
            return

        # No other monster to attack
        if len(current_mon_directory) < 2:
            await ctx.send(block_text(f"There is not enough monsters on the field for Mesmer Stone."))
            return

        # Item is improved
        improved = False
        if item == "Improved Mesmer Stone":
            improved = True

        # Target is present
        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        random_target = select_random_monster(1, current_mon_directory, monster.name)[0]

        chance = random.randint(1, 3)
        if chance == 1:
            monster_damage = math.ceil(monster.atk * 2)
            random_target_damage = math.ceil(random_target.atk * 2)
        else:
            monster_damage = random.randint(monster.atk//2, monster.atk)
            random_target_damage = random.randint(random_target.atk//2, monster.atk)

        if improved:
            monster_damage = round(monster_damage * 1.5)
            random_target_damage = round(monster_damage * 1.5)

        monster.current_hp -= random_target_damage
        if monster.current_hp < 0:
            monster.current_hp = 0

        random_target.current_hp -= monster_damage
        if random_target.current_hp < 0:
            random_target.current_hp = 0

        # Add item use to raid data
        if hero.raiding:
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        await ctx.send(embed=mesmer_stone_embed(hero.name, monster, random_target,
                                                monster_damage, random_target_damage, improved))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["scan", "impscan", "improved_monster_scanner"])
async def monster_scanner(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        item = get_item_from_command(ctx.message.content)
        target = shortcut_return(target.title())

        if item == "Monster_Scanner":
            item = "Monster Scanner"
        elif item == "Improved_Monster_Scanner":
            item = "Improved Monster Scanner"

        # Hero has item
        if not check_inventory(hero.inventory, item):
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Monster Scanner":
            improved = True

        # Target is present
        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        await ctx.send(embed=monster_scanner_embed(monster))

        hero.inventory.remove(item)

        # Add item use to raid data
        if hero.raiding:
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["scroll", "sos", "impscroll", "impsos", "improved_scroll_of_summoning"])
async def scroll_of_summoning(ctx, monster_rank):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        # Prevent item use in raid
        if hero.raiding:
            await ctx.send(block_text(f"You may not summon additional monsters while raiding."))
            return

        monster_rank = monster_rank.title()

        item = get_item_from_command(ctx.message.content)

        if item == "Scroll_Of_Summoning":
            item = "Scroll Of Summoning"
        elif item == "Improved_Scroll_Of_Summoning":
            item = "Improved Scroll Of Summoning"

        # Hero has item
        if not check_inventory(hero.inventory, item):
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Monster Scanner":
            improved = True

        # Rank target is accurate:
        if monster_rank not in ["1", "2", "3", "4", "5", "6", "7", "8", "Legendary"]:
            await ctx.send(block_text(f"{monster_rank} is not a summonable rank"))
            return

        if monster_rank in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            monster_rank = int(monster_rank)

        # Cast item
        if monster_rank == "Legendary" or monster_rank == "legendary":
            tier = "apex"
        elif monster_rank < 4:
            tier = 1
        elif 4 <= monster_rank <= 7:
            tier = 2
        elif monster_rank > 7:
            tier = 3
        else:
            return None

        # Set higher rate item
        x = Items()
        x.absolute_chance()

        random_item = x.random_item(monster_rank)

        mtr = MonsterBuilder(monster_rank)
        mtr.enraged_monster()
        mtr.item = random_item

        if improved:
            mtr.xp *= 2

        current_mon_directory.append(mtr)

        await ctx.send(embed=scroll_of_summoning_embed(mtr, improved))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["sms", "impsms", "improved_smelling_salts"])
async def smelling_salts(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item = get_item_from_command(ctx.message.content)

        if item == "Improved_Smelling_Salts":
            item = "Improved Smelling Salts"
        elif item == "Smelling_Salts":
            item = "Smelling Salts"

        if target is None:
            target = hero.name
        else:
            target = target.title()

        # Verify target hero present
        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        # Hero has item
        if not check_inventory(hero.inventory, item):
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Smelling Salts":
            improved = True

        target_hero = get_hero(HERO_LIST, target)

        if target_hero.resting == "Not Resting":
            await ctx.send(block_text(f"{target} is not currently resting!"))
            return

        if "Immense" in target_hero.status:
            target_hero.status.remove("Immense")
            target_hero.bonus_hp -= target_hero.immense_hp
            delattr(target_hero, "immense_hp")

        if "Apex" in target_hero.status:
            target_hero.status.remove("Apex")

        delattr(target_hero, "alarm_clock")

        hero.resting = "Not Resting"
        hero.current_hp = hero.max_hp + hero.bonus_hp
        hero.current_ep = hero.max_ep + hero.bonus_ep

        if improved:
            hero.status.append("Enraged Berserker")

        if improved:
            if target == hero.name:
                result = f"{hero.name} used smelling salts and woke up Enraged!"
            else:
                result = f"{hero.name} used smelling salts on {target} to wake them from their slumber, " \
                         f"leaving them Enraged!!"
        else:
            if target == hero:
                result = f"{hero.name} used smelling salts and woke up refreshed!"
            else:
                result = f"{hero.name} used smelling salts on {target}, waking them up refreshed!"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["sa", "impsa", "improved_sundering_axe"])
async def sundering_axe(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        item = get_item_from_command(ctx.message.content)

        if item == "Sundering_Axe":
            item = "Sundering Axe"
        elif item == "Improved_Sundering_Axe":
            item = "Improved Sundering Axe"

        target = shortcut_return(target.title())

        # Hero has item
        if not check_inventory(hero.inventory, item):
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Sundering Axe":
            improved = True

        # Target is present
        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        # Cast item
        if "Sundered" in monster.status or "Vulnerable" in monster.status:
            await ctx.send(block_text(f"{monster.name} has already been sundered!"))
            return

        # Reduces defense stat to zero
        if improved:
            monster.defense -= monster.defense * 2
            monster.status.append("Vulnerable")

            if "Normal" in monster.status:
                monster.status.remove("Normal")

        else:
            monster.defense = 0
            monster.status.append("Sundered")

            if "Normal" in monster.status:
                monster.status.remove("Normal")

        if hero.raiding:
            # Add item use to raid data
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        if improved:
            result = f"**{monster.name}** had its **armor shredded** and **constitution weakened** by the impact of an {item}!\n\n" \
                     f"*Monster now receives increased damage equal to its defense*"
        else:
            result = f"**{monster.name}** had its **armor shredded** by the impact of a {item}!\n\n" \
                     f"*Defense rating is now zero*"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["tome", "imptome", "improved_tome_of_wisdom"])
async def tome_of_wisdom(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item = get_item_from_command(ctx.message.content)

        if item == "Improved_Tome_Of_Wisdom":
            item = "Improved Tome Of Wisdom"
        elif item == "Tome_Of_Wisdom":
            item = "Tome Of Wisdom"

        if target is None:
            target = hero.name
        else:
            target = target.title()

        # Verify target hero present
        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        # Hero has item
        if not check_inventory(hero.inventory, item):
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Tome Of Wisdom":
            improved = True

        target_hero = get_hero(HERO_LIST, target)

        target_hero.status.append("Enlightened")

        if improved:
            target_hero.xp = math.ceil(target_hero.xp * 1.05)

        if improved:
            if target == hero.name:
                result = f"{target} has read from an **Ancient Tome Of Wisdom**! XP boosted 5%"
            else:
                result = f"{hero.name} has given {target_hero.name} a page from their **Ancient Tome Of Wisdom! " \
                         f"XP boosted **5%!**"
        else:
            if target == hero.name:
                result = f"{target} has read from their **Tome Of Wisdom**, next XP reward doubled!"
            else:
                result = f"{hero.name} has given {target} a page from their **Tome Of Wisdom**, next " \
                         f"XP reward doubled!"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["whet", "impwhet", "improved_whetstone"])
async def whetstone(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        item = get_item_from_command(ctx.message.content)

        if item == "Improved_Whetstone":
            item = "Improved Whetstone"
        elif item == "Whet":
            item = "Whetstone"

        if target is None:
            target = hero.name
        else:
            target = target.title()

        # Verify target hero present
        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        # Hero has item
        if not check_inventory(hero.inventory, item):
            await ctx.send(block_text(f"You do not have a {item}."))
            return

        # Item is improved
        improved = False
        if item == "Improved Whetstone":
            improved = True

        target_hero = get_hero(HERO_LIST, target)

        target_hero.status.append("Sharpened")

        if improved:
            target_hero.status.append("Enraged")

        if improved:
            if target == hero.name:
                result = f"{hero.name} sharpened their weapon to a razors edge, increasing potential **damage!** " \
                         f"Next attack guaranteed **critical.**"
            else:
                result = f"{hero.name} has sharpened **{target_hero.name}'s** weapon to a razors edge, " \
                         f"increasing potential **damage**! Next attack guaranteed **critical.**"
        else:
            if target == hero.name:
                result = f"{hero.name} sharpened their weapon. Next attack guaranteed **critical!**"
            else:
                result = f"{hero.name} sharpened **{target_hero.name}'s** weapon. Next attack " \
                         f"guaranteed **critical!**"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        # Add item use to raid data
        if hero.raiding:
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["ww", "impww", "improved_witchbolt_wand"])
async def witchbolt_wand(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw,
                          raid_1, raid_2, raid_3, testing_home]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        item = get_item_from_command(ctx.message.content)

        if item == "Witchbolt_Wand":
            item = "Witchbolt Wand"
        elif item == "Improved_Witchbolt_Wand":
            item = "Improved Witchbolt Wand"

        target = shortcut_return(target.title())

        # Hero has item
        if not check_inventory(hero.inventory, item):
            await ctx.send(block_text(f"{item} not found in inventory."))
            return

        # Item is improved
        improved = False
        if item == "Improved Witchbolt Wand":
            improved = True

        # Target is present
        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        cap_damage = math.ceil(monster.max_hp / 4)

        if improved:
            if monster.rank == "Apex":
                cap_floor = math.ceil(monster.max_hp / 70)
                cap_damage = math.ceil(monster.max_hp / 50)
            else:
                cap_floor = math.ceil(monster.max_hp / 5)
                cap_damage = math.ceil(monster.max_hp / 3)

            if monster.rank == "Apex":
                cap_floor = math.ceil(monster.max_hp / 80)
                cap_damage = math.ceil(monster.max_hp / 60)

            damage = random.randint(cap_floor, cap_damage)
            monster.status.append("Dazed")

        else:
            if monster.rank == "Apex":
                cap_damage = math.ceil(monster.max_hp / 70)

            damage = random.randint(1, cap_damage)

        monster.current_hp -= damage
        if monster.current_hp < 0:
            monster.current_hp = 0

        monster.status.append("Dazed")

        if "Normal" in monster.status:
            monster.status.remove("Normal")

            # Add item use to raid data
        if hero.raiding:
            MASTER_RAID_DICT[hero.name].items_used.append(item)

        if improved:
            result = f"A streak of lightning burns through the air from {hero.name}'s Witchbolt Wand, striking " \
                     f"**{monster.name}** for **{damage}** damage!\n\n" \
                     f"**__{monster.name}__**\n" \
                     f"{monster.current_hp}/{monster.max_hp} HP\n" \
                     f"*Dazed, Dazed*"
        else:
            result = f"A bolt of electricity crackles through the air from {hero.name}'s Witchbolt Wand, striking " \
                     f"**{monster.name}** for **{damage}** damage!\n\n" \
                     f"**__{monster.name}__**\n" \
                     f"{monster.current_hp}/{monster.max_hp} HP\n" \
                     f"*Dazed*"

        await ctx.send(embed=item_card_embed(hero.name, item, result))

        hero.inventory.remove(item)

        records = open_hero_records(hero.owner)
        records["records"]["items used"] += 1
        close_hero_records(records, hero.owner)


# ABILITY COMMANDS ____________________________________________________________________________________


@bot.command(aliases=["af"])
async def apex_form(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Apex Form"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Apex Form'."))
            return

        if hero.current_ep < 5:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Apex Form'."))
            return

        if "Apex" in hero.status:
            await ctx.send(block_text(f"{hero.name} must rest before assuming the Apex form again."))
            return

        hero.status.append("Apex")
        if "Normal" in hero.status:
            hero.status.remove("Normal")

        result = f"{hero.name} explodes with energy, taking the form of a Apex of the Maw. Abilities empowered, " \
                 f"and auras activated."

        await ctx.send(embed=ability_card_embed(hero, "Apex Form", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["aritual"])
async def apex_ritual(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Apex Ritual"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Apex Ritual'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Apex Ritual'."))
            return

        hero.current_ep -= 1

        base_crit = hero.crit_multiplier
        base_init = hero.initiative

        hero.crit_multiplier = round(hero.crit_multiplier * 1.25, 1)
        hero.initiative = math.ceil(hero.initiative * 1.25)

        hero.sp_atk["Apex Form"] = {
            "name": "Apex Form 5EP |af|",
            "text": "Now I am become death.",
            "dmg": 0,
            "effect": "apex_form",
            "description": "Empowers abilities, increases damage against Apex monsters, and adds aura effects "
                           "in combat."
        }

        hero.sp_atk.pop("Apex Ritual")

        result = f"**Behemoth Ritual Complete!**\n" \
                 f"Crit: {base_crit} -> {hero.crit_multiplier}\n" \
                 f"Initiative: {base_init} -> {hero.initiative}\n" \
                 f"Ability **Apex Form** added!\n\n" \
                 f"*The Old Ones were, the Old Ones are, and the Old Ones shall be. Incomprehensible. Unearthly. Raw power on " \
                 f"an unimaginable scale. {hero.name} has abandoned any form of humanity.*"

        await ctx.send(embed=ability_card_embed(hero, "Apex Ritual", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["ass"])
async def assassinate(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Assassinate"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Assassinate'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Assassinate'."))
            return

        # Get monster
        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        hero.current_ep -= 1

        fail_rate = hero.sp_atk["Assassinate"]["dmg"]

        # Check if hero is stalking
        if monster.rank == "Apex":
            fail_rate += 50

        if "Marked" in monster.status:
            fail_rate = math.ceil(fail_rate / 2)
            monster.status.remove("Marked")

        chance = random.randint(1, fail_rate)
        chance_percent = round(1 / fail_rate * 100)

        if chance == 1:
            monster.current_hp = 0
            monster.status.append("Mortal Wound")
            if "Normal" in monster.status:
                monster.status.remove("Normal")

            result = f"Your blade slides across the {target}'s throat. The {target} struggles for life.\n*Success Rate: {chance_percent}%*"
        else:
            result = f"You attempt to assassinate the {target} but were spotted in the shadows before you could strike!\n" \
                     f"*Success Rate: {chance_percent}%*"

        await ctx.send(embed=ability_card_embed(hero, "Assassinate", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)

    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        return

    else:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        hero.armory.append("Yamatos Training Katana")
        hero.armory.append("Cloth Armor")
        hero.equipment_training = True

        hero.training_stage += 1

        channel = bot.get_channel(id=897223260964528159)

        await ctx.send(embed=ability_card_embed(hero, "Assassinate",
                                                f"Your blade slides across the Test Dummy's throat. The Test Dummy struggles for life.\n*Success Rate: 100%*"))

        await sleep(3)

        await ctx.send(
            embed=standard_embed(
                title="Nice!",
                text="That is all there is to it!. You can check what "
                     "abilities you know by using the **.s** or **.stats** "
                     "command, which will also show you the command shortcut in "
                     "vertical bars. For Assassinate it would be **.ass**. "
                     f"To learn more about abilities, check out the {channel.mention} "
                     "channel. \n\nNow that you are an expert on abilities, "
                     "lets take a look at equipment. Here take these..."))

        await sleep(4)
        await ctx.send(embed=give_item_embed("Maw", "Yamatos Training Katana", hero.name))
        await sleep(1)
        await ctx.send(embed=give_item_embed("Maw", "Cloth Armor", hero.name))
        await sleep(1)
        await ctx.send(
            embed=standard_embed(
                title="Equipment",
                text=f'Equipment is pretty rare. You only receive equipment from '
                     f'defeating massive creatures called Apexes in the Apex Meadow. '
                     f'Armor is obtained at a pretty steep price from the shopkeep. '
                     f'\n\nNow that you have them, try the commands: **.equip "yamatos '
                     f'training katana"** *(.eq ytk for short)*, and **.equip '
                     f'"cloth armor"** *(.eq ca for short)*.'))


@bot.command(aliases=["bm"])
async def battlemage(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Battlemage"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Battlemage'."))
            return

        if hero.current_ep < 7:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to utilize 'Battlemage'."))
            return

        hero.current_ep -= 6

        if "Normal" in hero.status:
            hero.status.remove("Normal")

        hero.status.append("Battlemage")

        multiplier = hero.current_ep
        hero.current_ep = 0

        stat_mod = hero.sp_atk["Battlemage"]["dmg"]

        hero.battlemage_attack_mod = multiplier * (4 * stat_mod)
        hero.battlemage_defense_mod = multiplier * (1 * stat_mod)
        hero.battlemage_crit_mod = multiplier * 0.1

        prior_attack = hero.atk
        prior_defense = hero.defense
        prior_crit = hero.crit_multiplier

        hero.bonus_atk += hero.battlemage_attack_mod
        hero.bonus_def += hero.battlemage_defense_mod
        hero.bonus_crit += hero.battlemage_crit_mod

        result = f"{hero.name} surges with energy! Combat stats elevated. Battlemage status lost on spell cast, " \
                 f"or if damage taken.\n\n" \
                 f"**Attack**: {prior_attack} -> {hero.atk + hero.bonus_atk}\n" \
                 f"**Defense**: {prior_defense} -> {hero.defense + hero.bonus_def}\n" \
                 f"**Crit**: {prior_crit} -> {hero.crit_multiplier + hero.bonus_crit}"

        await ctx.send(embed=ability_card_embed(hero, "Battlemage", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["bi"])
async def become_immense(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Become Immense"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Become Immense'."))
            return

        if hero.current_ep < 3:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Become Immense'."))
            return

        if "Immense" in hero.status:
            await ctx.send(block_text(f"{hero.name} is already Immense!"))
            return

        hero.current_ep -= 3
        temp_max = hero.max_hp + hero.bonus_hp

        if "Apex" in hero.status:
            hero.immense_hp = 2 * hero.max_hp
        else:
            hero.immense_hp = hero.max_hp

        hero.bonus_hp += hero.immense_hp
        hero.current_hp += hero.immense_hp

        hero.status.append("Immense")
        if "Normal" in hero.status:
            hero.status.remove("Normal")

        if "Apex" in hero.status:
            result = f"{hero.name} has transformed into a behemoth! Base **Max HP tripled**.\n\n" \
                     f"**__{hero.name}__**\n" \
                     f"Max HP: {temp_max} -> {hero.max_hp + hero.bonus_hp}\n" \
                     f"*{hero.current_hp}/{hero.max_hp + hero.bonus_hp}* HP"
        else:
            result = f"{hero.name} has transformed into a behemoth! Base **Max HP doubled**.\n\n" \
                     f"**__{hero.name}__**\n" \
                     f"Max HP: {temp_max} -> {hero.max_hp + hero.bonus_hp}\n" \
                     f"*{hero.current_hp}/{hero.max_hp + hero.bonus_hp}* HP"

        await ctx.send(embed=ability_card_embed(hero, "Become Immense", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["britual"])
async def behemoth_ritual(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Behemoth Ritual"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Behemoth Ritual'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Behemoth Ritual'."))
            return

        hero.current_ep -= 1

        base_defense = hero.defense

        hero.defense = math.ceil(hero.defense * 1.25)

        hero.sp_atk["Become Immense"] = {
            "name": "Become Immense 3EP |bi|",
            "text": "Reaching the Apex is not simply done without mass",
            "dmg": 0,
            "effect": "become_immense",
            "description": "Target gains double current health pool. Cannot stack. Buff is removed upon resting."
        }

        hero.sp_atk.pop("Behemoth Ritual")

        result = f"**Behemoth Ritual Complete!**\n" \
                 f"Defense: {base_defense} + {math.ceil(base_defense * 0.25)}\n" \
                 f"Ability **Become Immense** added!\n\n" \
                 f"*Pack leaders are not found amongst the weak and frail. The corrupted energies of the " \
                 f"Maw steels your flesh.*"

        await ctx.send(embed=ability_card_embed(hero, "Behemoth Ritual", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["cc"])
async def celestial_consult(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if target is None:
            target = hero.name
        else:
            target = target.title()

        if not can_use_ability(hero, "Celestial Consult"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Celestial Consult'."))
            return

        if hero.current_ep < 3:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Celestial Consult'."))
            return

        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        hero.current_ep -= 3

        if "Light Domain" in hero.status:
            xp = random.randint(800, 1200)
            hero.xp += xp
            await ctx.send(embed=light_domain_xp_embed(hero.name, xp, "Celestial Consult"))

        enlighten_range = random.randint(1, 3)

        for _ in range(enlighten_range):
            hero.status.append("Enlightened")

        if enlighten_range > 2:
            enlighten_text = "profound"
        elif enlighten_range > 1:
            enlighten_text = "greater"
        else:
            enlighten_text = "weak"

        if target == hero.name:
            result = f"{hero.name} has consulted the pantheon and has been granted {enlighten_text} divine wisdom!"
        else:
            result = f"{hero.name} has consulted the pantheon on behalf of {target}, granting them {enlighten_text} divine wisdom!"

        await ctx.send(embed=ability_card_embed(hero, "Celestial Consult", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["cog"])
async def cognition(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Cognition"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Cognition'."))
            return

        aspects = []
        aspect_effects = []
        buffs = []
        skill_keys = list(hero.sp_atk.keys())
        for status in hero.status:
            if status[:11] == "Oath-Strong" or status in ["Enraged", "Sharpened", "Ambiguity", "Berserker",
                                                          "Enlightened", "Immense", "Apex"]:
                buffs.append(status)

            if "Rake Claws" in skill_keys:
                aspects.append("Aspect of the Predator")
                aspect_effects.append("Attack Boosted 25%")
            if "Become Immense" in skill_keys:
                aspects.append("Aspect of the Behemoth")
                aspect_effects.append("Defense Boosted 25%")
            if "Depraved Frenzy" in skill_keys:
                aspects.append("Aspect of the Legend")
                aspect_effects.append("HP boosted 25%")
            if "Apex Form" in skill_keys:
                aspects.append("Aspect of the Apex")
                aspect_effects.append("Crit/Initiative boosted 25%")

        aspect_complete = [f"{aspects[i]}: {aspect_effects[i]}" for i in range(len(aspects))]
        aspect_string_newlines = '\n'.join(aspect_complete)
        buff_string = f"**__Buffs__**\n{', '.join(buffs)}"
        aspect_string = f"**__Aspects__**\n{aspect_string_newlines}"

        result = f"{buff_string}\n{aspect_string}"
        await ctx.send(embed=ability_card_embed(hero, "Cognition", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["df"])
async def depraved_frenzy(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if target is None:
            target = hero.name
        else:
            target = target.title()

        if not can_use_ability(hero, "Depraved Frenzy"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Depraved Frenzy'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Depraved Frenzy'."))
            return

        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        target_hero = get_hero(HERO_LIST, target)

        if "Enraged" in target_hero.status and "Sharpened" in target_hero.status:
            await ctx.send(block_text(f"{target} is already Enraged and Sharpened."))
            return

        hero.current_ep -= 1

        if "Apex" in hero.status:
            pass
        else:
            target_hero.current_hp = math.ceil(target_hero.current_hp * 0.8)

        target_hero.status.extend(["Enraged", "Sharpened"])

        if "Apex" in hero.status:
            result = f"{target} absorbs power from the Maw and enters a depraved frenzy!\n\n" \
                     f"**__{target}__**\n" \
                     f"*{target_hero.current_hp}/{target_hero.max_hp + target_hero.bonus_hp}* HP\n" \
                     f"**Enraged** and **Sharpened** added!"
        else:
            result = f"{target} sacrifices blood to the Maw and enters a depraved frenzy!\n\n" \
                     f"**__{target}__**\n" \
                     f"*{target_hero.current_hp}/{target_hero.max_hp + target_hero.bonus_hp}* HP\n" \
                     f"**Enraged** and **Sharpened** added!"

        await ctx.send(embed=ability_card_embed(hero, "Depraved Frenzy", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["det"])
async def detonate(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Detonate"):
            await ctx.send(f"{hero.name} does not know the ability 'Detonate'.")
            return

        if hero.current_ep < 1:
            await ctx.send(f"{hero.name} does not have enough EP to use 'Detonate'.")
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {monster.name}."))
            return

        if monster.item is None:
            await ctx.send(f"{target} has no item to detonate.")
            return

        if monster.rank == "Apex":
            await ctx.send("The Apex is to powerful to be affected by this ability!")
            return

        hero.current_ep -= 1

        item_lists = Items()
        monster_item = monster.item

        if monster.item in item_lists.tier1_items:
            multiplier = 1
        elif monster.item in item_lists.tier2_items:
            multiplier = 2
        elif monster.item in item_lists.tier3_items:
            multiplier = 4
        else:
            multiplier = 6

        # Roll and apply damage, remove monster item
        det_dmg = random.randint(20, 50) * multiplier * hero.level
        monster.current_hp -= det_dmg

        if monster.current_hp < 0:
            monster.current_hp = 0

        monster.item = None

        result = f"{hero.name} detonated the {target}'s held {monster_item} for {det_dmg} damage!"
        await ctx.send(embed=ability_card_embed(hero, "Detonate", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["div"])
async def divinity(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Divinity"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Divinity'."))
            return

        await ctx.send(embed=divine_path_embed())

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and \
                   msg.content.lower() in ["ld", "wd"]

        try:
            msg = await bot.wait_for("message", check=check, timeout=120)
        except TimeoutError:
            await ctx.send(code_block(f"{hero.name} has declined to choose a path"))
            return

        if msg.content.lower() == "ld":
            domain = "Light Domain"
        else:
            domain = "War Domain"

        result = "Something went wrong selecting a domain"

        if domain == "Light Domain":

            hero.status.append("Light Domain")

            if "Normal" in hero.status:
                hero.status.remove("Normal")

            celestial_consult = {
                "Celestial Consult": {
                    "name": "Celestial Consult 3EP",
                    "text": f"Seek wisdom from me, and in faith you will be rewarded",
                    "dmg": 0,
                    "effect": "celestial consult",
                    "description": "Adds between 1 and 3 stacks of enlightened to target hero"
                }
            }

            hero.sp_atk.pop("Divinity")
            hero.sp_atk["Celestial Consult"] = celestial_consult["Celestial Consult"]
            hero_old_atk = hero.atk + hero.bonus_atk
            hero_old_def = hero.defense + hero.bonus_def
            hero_old_hp = hero.max_hp + hero.bonus_hp
            hero_old_maxep = hero.max_ep + hero.bonus_ep

            hero.atk = math.ceil(hero.atk * 0.9)
            hero.defense = math.ceil(hero.defense * 0.9)
            hero.max_hp = math.ceil(hero.max_hp * 0.9)
            hero.max_ep += 3
            hero.current_ep += 3

            result = f"**Light Domain Chosen**\n\n" \
                     f"Celestial Consult Added!\n" \
                     f"Spell XP Growth added!\n\n" \
                     f"**Attack**: {hero_old_atk} -> {hero.atk + hero.bonus_atk}\n" \
                     f"**Defense**: {hero_old_def} -> {hero.defense + hero.bonus_def}\n" \
                     f"**HP**: {hero_old_hp} -> {hero.max_hp + hero.bonus_hp}\n" \
                     f"**EP**: {hero_old_maxep} -> {hero.max_ep + hero.bonus_ep}\n"

        if domain == "War Domain":
            hero.sp_atk.pop("Regenerate")
            hero.sp_atk.pop("Divinity")
            hero_old_atk = hero.atk + hero.bonus_atk
            hero_old_def = hero.defense + hero.bonus_def
            hero_old_crit = hero.crit_multiplier + hero.bonus_crit
            hero_old_hp = hero.max_hp + hero.bonus_hp

            hero.atk = math.ceil(hero.atk * 1.5)
            hero.defense = math.ceil(hero.defense * 1.5)
            hero.crit_multiplier = round(hero.crit_multiplier * 1.5, 1)
            hero.max_hp = math.ceil(hero.max_hp * 1.5)

            result = f"**War Domain Chosen**\n\n" \
                     f"Regenerate ability removed!\n" \
                     f"Power of God and Anime Received!\n\n" \
                     f"**Attack**: {hero_old_atk} -> {hero.atk + hero.bonus_atk}\n" \
                     f"**Defense**: {hero_old_def} -> {hero.defense + hero.bonus_def}\n" \
                     f"**HP**: {hero_old_hp} -> {hero.max_hp + hero.bonus_hp}\n" \
                     f"**Crit**: {hero_old_crit} -> {hero.crit_multiplier + hero.bonus_crit}\n"

        await ctx.send(embed=ability_card_embed(hero, "Divinity", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["exe"])
async def executor(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home, raid_1,
                          raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Executor"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Executor'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Executor'."))
            return

        if "Executor" in hero.status:
            await ctx.send(block_text(f"{hero.name} is already an Executor."))
            return

        hero.current_ep -= 1

        hero.status.extend(["Executor", "Executor", "Executor"])

        result = f"{hero.name} stands ready to cull the weakened and frail."

        await ctx.send(embed=ability_card_embed(hero, "Executor", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["fb"])
async def fireball(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Fireball"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Fireball'."))
            return

        if hero.current_ep < 3:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Fireball'."))
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if hero.raiding:
            if monster.position_locked:
                await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {target}."))

        # Battlemage status block
        if "Battlemage" in hero.status:
            hero.status.remove("Battlemage")
            hero.bonus_atk -= hero.battlemage_attack_mod
            hero.defense -= hero.battlemage_defense_mod
            hero.crit_multiplier -= hero.battlemage_crit_mod
            await ctx.send(embed=battlemage_end_embed(hero.name, True))

        monster_hit_list = select_random_monster(2, current_mon_directory, monster.name)

        # Return target to hit list
        monster_hit_list.append(monster)
        if "None" in monster_hit_list:
            monster_hit_list.remove("None")

        # Roll fireball damage
        skill_dmg = hero.sp_atk["Fireball"]["dmg"]
        floor_dmg = skill_dmg // 2
        fb_dmg = random.randint(floor_dmg, skill_dmg)

        for fb_monster in monster_hit_list:

            if hero.name not in monster.attacked_by:
                fb_monster.attacked_by.append(hero.name)

            fb_monster.current_hp -= fb_dmg
            if fb_monster.current_hp < 0:
                fb_monster.current_hp = 0

        result = f"{hero.name} launched a blazing nova upon the battlefield for **{fb_dmg}** damage!\n" \
                 f"Hit: {', '.join([mon.name for mon in monster_hit_list])}"

        hero.current_ep -= 3

        await ctx.send(embed=ability_card_embed(hero, "Fireball", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["foc"])
async def focus(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if "Silenced" in hero.status:
            if hero.silenced_ability_name == "Focus":
                await ctx.send("This ability has been silenced! Kill the Apex to return it!")
                return

        if not can_use_ability(hero, "Focus"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Focus'."))
            return

        if hero.current_ep < 2:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Focus'."))
            return

        hero.current_ep -= 2

        if "Enraged" in hero.status:
            pass
        else:
            hero.status.append("Enraged")

        if "Sharpened" in hero.status:
            pass
        else:
            hero.status.append("Sharpened")

        result = f"{hero.name} has sharpened their mind and is ready for battle!"
        await ctx.send(embed=ability_card_embed(hero, "focus", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["hb"])
async def helmbreaker(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Helmbreaker"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Helmbreaker'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Helmbreaker'."))
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {target}."))
            return

        hero.current_ep -= 1

        monster.defense = monster.defense // 2
        monster.status.append("Armor Reduced")
        if "Normal" in monster.status:
            monster.status.remove("Normal")

        result = f"{hero.name} charges forward slashing the {target} and cleaving its hide. Armor reduced by half!"
        await ctx.send(embed=ability_card_embed(hero, "Helmbreaker", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)

    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        return

    else:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        hero.armory.append("Yamatos Training Katana")
        hero.armory.append("Cloth Armor")

        hero.training_stage += 1

        abil_channel = bot.get_channel(id=897223260964528159)

        await ctx.send(embed=ability_card_embed(hero, "Helmbreaker",
                                                f"{hero.name} charges forward slashing the Test Dummy and cleaving its hide. Armor reduced by half!"))
        await sleep(3)
        await ctx.send(
            embed=standard_embed(
                title="Nice!",
                text="That is the basics on ability use. You can check what abilities you know by "
                     "using the **.s** or **.stats** command, which will also "
                     "show you the shortcut in vertical bars. "
                     "For Helmbreaker it would be **.hb**. To learn more about abilities, "
                     f"check out the {abil_channel.mention} channel.\n\n"
                     f"Now that you are an expert on abilities, lets take a "
                     f"look at equipment. Here take these..."))
        await sleep(4)
        await ctx.send(embed=give_item_embed("Maw", "Yamatos Training Katana", hero.name))
        await sleep(1)
        await ctx.send(embed=give_item_embed("Maw", "Cloth Armor", hero.name))
        await sleep(1)
        await ctx.send(embed=standard_embed(title="Equipment",
                                            text=f'Equipment is pretty rare. You only receive equipment from '
                                                 f'defeating massive creatures called Apexes in the Apex Meadow. '
                                                 f'Armor is obtained at a pretty steep price from the shopkeep. '
                                                 f'\n\nNow that you have them, try the commands: **.equip "yamatos '
                                                 f'training katana"** *(.eq ytk for short)*, and **.equip '
                                                 f'"cloth armor"** *(.eq ca for short)*.'))


@bot.command(aliases=["int"])
async def intuition(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Intuition"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Intuition'."))
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(f"You must defeat lower level raid monsters before targeting {target}.")
            return

        if monster.item is not None:
            await ctx.send(block_text(f"{hero.name} knows {target} is holding a {monster.item}!."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Intuition'."))
            return

        hero.current_ep -= 1

        # Set failure
        chance = random.randint(1, 2)

        if monster.rank == "Legendary":
            chance = random.randint(1, 6)

        # Make a random item
        item_object = Items()
        item_object.absolute_chance()
        item = item_object.random_item(monster.rank)

        # Success
        if chance == 1:
            monster.item = item
            result = f"{hero.name} located a hidden {item} on the {target}"

        # Failure
        else:
            result = f"{hero.name} was unable to locate any hidden items on {target}."

        await ctx.send(embed=ability_card_embed(hero, "Intuition", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)

    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        return

    else:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        hero.armory.append("Yamatos Training Katana")
        hero.armory.append("Cloth Armor")

        hero.training_stage += 1

        abil_channel = bot.get_channel(id=897223260964528159)

        await ctx.send(embed=ability_card_embed(hero, "Intuition",
                                                f"{hero.name} located a hidden Witchbolt Wand on the Test Dummy!"))
        await sleep(3)
        await ctx.send(embed=standard_embed(title="Nice!", text="That is the basics on ability use. You can check what "
                                                                "abilities you know by using the **.s** or **.stats**"
                                                                " command, which will also show you the shortcut in "
                                                                "vertical bars. For Intuition it would be **.int**. "
                                                                "To learn more about abilities, check out the "
                                                                f"{abil_channel.mention} channel.\n\n"
                                                                "Now that you are an expert on abilities, "
                                                                "lets take a look at equipment. Here take these..."))
        await sleep(4)
        await ctx.send(embed=give_item_embed("Maw", "Yamatos Training Katana", hero.name))
        await sleep(1)
        await ctx.send(embed=give_item_embed("Maw", "Cloth Armor", hero.name))
        await sleep(1)
        await ctx.send(embed=standard_embed(title="Equipment",
                                            text=f'Equipment is pretty rare. You only receive equipment from '
                                                 f'defeating massive creatures called Apexes in the Apex Meadow. '
                                                 f'Armor is obtained at a pretty steep price from the shopkeep. '
                                                 f'\n\nNow that you have them, try the commands: **.equip "yamatos '
                                                 f'training katana"** *(.eq ytk for short)*, and **.equip '
                                                 f'"cloth armor"** *(.eq ca for short)*.'))


@bot.command(aliases=["lritual"])
async def legend_ritual(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Legend Ritual"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Legend Ritual'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Legend Ritual'."))
            return

        hero.current_ep -= 1

        base_hp = hero.max_hp

        hero.max_hp = math.ceil(hero.max_hp * 1.25)

        hero.sp_atk["Depraved Frenzy"] = {
            "name": "Depraved Frenzy |df|",
            "text": "Only the most ferocious monstrosities can claim the seat of legendary monsters.",
            "dmg": 0,
            "effect": "depraved_frenzy",
            "description": "Target hero HP reduced by 20% max health, grants Enraged and Sharpened status."
        }

        hero.sp_atk.pop("Legend Ritual")

        result = f"**Legend Ritual Complete!**\n" \
                 f"HP: {base_hp} + {math.ceil(base_hp * 0.25)}\n" \
                 f"Ability **Depraved Frenzy** added!\n\n" \
                 f"*Reason and Sanity slip away, leaving {hero.name} a hollow shell of death and ferocity.*"
        await ctx.send(embed=ability_card_embed(hero, "Legend Ritual", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["mm"])
async def magic_missile(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Magic Missile"):
            await ctx.send(f"{hero.name} does not know the ability 'Magic Missile'.")
            return

        if hero.current_ep < 1:
            await ctx.send(f"{hero.name} does not have enough EP to use 'Magic Missile'.")
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(f"{target} is not in the Maw.")
            return

        monster = get_monster(current_mon_directory, target)

        # Battlemage status block
        if "Battlemage" in hero.status:
            hero.status.remove("Battlemage")
            hero.bonus_atk -= hero.battlemage_attack_mod
            hero.defense -= hero.battlemage_defense_mod
            hero.crit_multiplier -= hero.battlemage_crit_mod
            await ctx.send(embed=battlemage_end_embed(hero.name, True))

        if monster.position_locked:
            await ctx.send(f"You must defeat lower level raid monsters before targeting {target}.")
            return

        hero.current_ep -= 1

        crit = hero.crit_multiplier

        sp_atk_dmg = hero.sp_atk["Magic Missile"]["dmg"]

        floor_dmg = round(sp_atk_dmg / 2)

        mm_dmg = random.randint(floor_dmg, sp_atk_dmg)

        chance = random.randint(1, 3)

        if chance == 1:
            mm_dmg = round(mm_dmg * crit)

        monster.current_hp -= mm_dmg
        if monster.current_hp < 0:
            monster.current_hp = 0

        # Set damage record
        records = open_hero_records(hero.owner)
        if mm_dmg > records["records"]["highest damage"]:
            records["records"]["highest damage"] = mm_dmg
            close_hero_records(records, hero.owner)

        # Set result if crit or not crit
        if chance == 1:
            result = f"{hero.name} lands an explosive missile on {target} for {mm_dmg} damage!\n*{monster.current_hp}/{monster.max_hp}* HP"
        else:
            result = f"{target} is wounded by a magic missile for {mm_dmg} damage!\n*{monster.current_hp}/{monster.max_hp}* HP"

        await ctx.send(embed=ability_card_embed(hero, "Magic Missile", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["mc"])
async def mass_casualty(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if not can_use_ability(hero, "Mass Casualty"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Mass Casualty'."))
            return

        if hero.current_ep < 3:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Mass Casualty'."))
            return

        hero.current_ep -= 3

        casualties = []
        for monster in current_mon_directory:

            if monster.name == "Chest":
                continue

            if monster.rank == "Legendary" or hero.raiding:
                fail_rate = 4
            elif monster.rank == "Apex":
                fail_rate = 100
            else:
                fail_rate = 2

            chance = random.randint(1, fail_rate)

            if chance == 1:

                casualties.append(monster.name)
                monster.current_hp = 0
                monster.status.append("Mortal Wound")

                if "Normal" in monster.status:
                    monster.status.remove("Normal")

        if casualties:
            result = f"{hero.name} has assassinated {', '.join(casualties)}."
        else:
            result = f"{hero.name} was unable to assassinate a target this night."

        await ctx.send(embed=ability_card_embed(hero, "Mass Casualty", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["mo"])
async def maw_oath(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Maw Oath"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Maw Oath'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Maw oath'."))
            return

        if "Oath-Strong" in hero.status:
            await ctx.send(block_text(f"{hero.name} has already affirmed their oath to the Maw."))
            return

        hero.current_ep -= 1

        if "Apex" in hero.status:
            percentage_hp = (hero.max_hp + hero.bonus_hp) // 2
        else:
            percentage_hp = (hero.max_hp + hero.bonus_hp) // 4

        hero.current_hp += percentage_hp
        if hero.current_hp > hero.max_hp + hero.bonus_hp:
            hero.current_hp = hero.max_hp + hero.bonus_hp

        # Add Oath Strong counter for 25% def increase
        hero.status.extend(["Oath-Strong", "Oath-Strong", "Oath-Strong"])

        result = f"{hero.name} affirms their oath to the Maw!\n\n" \
                 f"**__{hero.name}__**\n" \
                 f"{hero.current_hp}/{hero.max_hp + hero.bonus_hp} HP\n" \
                 f"Oath-Strong status added\n" \
                 f"25% increase defense in combat for three rounds"

        await ctx.send(embed=ability_card_embed(hero, "Maw Oath", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["obs"])
async def obsecrate(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if target is None:
            target = hero.name
        else:
            target = target.title()

        if not can_use_ability(hero, "Obsecrate"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Obsecrate'."))
            return

        if hero.current_ep < 2:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Obsecrate'."))
            return

        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        hero.current_ep -= 2

        if "Light Domain" in hero.status:
            xp = random.randint(400, 800)
            hero.xp += xp
            await ctx.send(embed=light_domain_xp_embed(hero.name, xp, "Obsecrate"))

        target_hero = get_hero(HERO_LIST, target)

        result = f"Obsecrate command failed to match a boon"

        blessings = ["Blessing of Arawn", "Blessing of Tempus", "Blessing of Estanna", "Blessing of Baal",
                     "Blessing of Tymora"]
        chance = random.choices(blessings, weights=(1, 10, 10, 10, 10), k=1)
        chance = " ".join(chance)

        if chance == "Blessing of Arawn":

            if "Arawn's Gift" not in target_hero.status:
                target_hero.status.append("Arawn's Gift")

            result = f"{target} has been given the {chance}.\n*Death is merely an obstacle.*"

        if chance == "Blessing of Tempus":

            if "Enraged" not in target_hero.status:
                target_hero.status.append("Enraged")

            result = f"{target} has been given the {chance}.\n*Attack force multiplied.*"

        if chance == "Blessing of Estanna":

            if "Speed Rest" not in target_hero.status:
                target_hero.status.append("Speed Rest")

            result = f"{target} has been given the {chance}.\n*Restful sleep has never been so swift.*"

        if chance == "Blessing of Baal":

            if "Sharpened" not in target_hero.status:
                target_hero.status.append("Sharpened")

            result = f"{target} has been given the {chance}.\n*A clever strike is better than a wild attack.*"

        if chance == "Blessing of Tymora":
            ranks = ["Legendary", "1", "5", "8"]
            random_rank = random.choices(ranks, weights=(1, 10, 10, 10), k=1)

            if random_rank[0] in ["1", "5", "8"]:
                random_rank = int(random_rank[0])
            else:
                random_rank = "Legendary"

            item = Items()
            item.absolute_chance()
            random_item = item.random_item(random_rank)

            if random_item in ["Mountain Key", "Tortoise Key", "Blood-Soaked Key", "Dimensional Key"]:
                target_hero.keys.append(random_item)

                result = f"{target} has received the {random_item}!"

            else:
                target_hero.inventory.append(random_item)

                result = f"{target} has been given the {chance}.\n*{random_item} received!*"

        await ctx.send(embed=ability_card_embed(hero, "Obsecrate", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["pritual"])
async def predator_ritual(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Predator Ritual"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Predator Ritual'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Predator Ritual'."))
            return

        hero.current_ep -= 1

        base_attack = hero.atk

        hero.atk = math.ceil(hero.atk * 1.25)

        hero.sp_atk["Rake Claws"] = {
            "name": "Rake Claws |rc|",
            "text": "The Maw has a way of bringing out the most destructive traits possible.",
            "dmg": 0,
            "effect": "rake_claws",
            "description": "Deals damage equal to max attack stat to target monster and inflicts bleeding for 2 turns."
        }

        hero.sp_atk.pop("Predator Ritual")

        result = f"**Predator Ritual Complete!**\n" \
                 f"**Attack**: {base_attack} + {round(base_attack * 0.25)}\n" \
                 f"Ability **Rake Claws** added!\n\n" \
                 f"*The thirst for blood is inescapable. The Maw evolves even the most peaceful of beings to a constructs of " \
                 f"death.*"

        await ctx.send(embed=ability_card_embed(hero, "Predator Ritual", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["rc"])
async def rake_claws(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Rake Claws"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Rake Claws'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Rake Claws'."))
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {target}."))

        hero.current_ep -= 1

        rc_dmg = hero.atk

        monster.current_hp -= rc_dmg

        monster.status.append("Bleeding")

        if monster.current_hp < 0:
            monster.current_hp = 0

        if "Apex" in hero.status and len(current_mon_directory) > 1:
            random_target = select_random_monster(1, current_mon_directory, target)[0]

            random_target.current_hp -= rc_dmg

            if random_target.current_hp < 0:
                random_target.current_hp = 0

            random_target.status.append("bleeding")

            result = f"Apex {hero.name} cleaves **{rc_dmg}** damage through **{target}** and **{random_target.name}**. Both creatures " \
                     f"afflicted with **bleeding**."

        else:
            result = f"{hero.name} slashes the **{target}** for **{rc_dmg}** damage! **{target}** is now **Bleeding**!"

        await ctx.send(embed=ability_card_embed(hero, "Rake Claws", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["reg"])
async def regenerate(ctx, target=None):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if target is None:
            target = hero.name
        else:
            target = target.title()

        if not can_use_ability(hero, "Regenerate"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Regenerate'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Regenerate'."))
            return

        if not hero_target_present(target, HERO_LIST):
            await ctx.send(block_text(f"{target} is not a registered hero."))
            return

        hero.current_ep -= 1

        if "Light Domain" in hero.status:
            xp = random.randint(280, 400)
            hero.xp += xp
            await ctx.send(embed=light_domain_xp_embed(hero.name, xp, "Regenerate"))

        target_hero = get_hero(HERO_LIST, target)

        hp_regen = math.ceil((target_hero.max_hp + target_hero.bonus_hp) * 0.75)

        target_hero.current_hp += hp_regen
        if target_hero.current_hp > target_hero.max_hp + target_hero.bonus_hp:
            target_hero.current_hp = target_hero.max_hp + target_hero.bonus_hp

        result = f"{target} regenerated {hp_regen} HP!\n\n**{target}**\n*{target_hero.current_hp}/{target_hero.max_hp + target_hero.bonus_hp}* HP"

        await ctx.send(embed=ability_card_embed(hero, "Regenerate", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)

    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        return

    else:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        hero.armory.append("Yamatos Training Katana")
        hero.armory.append("Cloth Armor")

        hero.training_stage += 1

        abil_channel = bot.get_channel(id=897223260964528159)

        await ctx.send(embed=ability_card_embed(hero, "Regenerate",
                                                f"Maw is engulfed in a healing spell!\n\n**__Maw__**\n*Mortally Wounded -> Healthy*"))
        await sleep(3)
        await ctx.send(
            embed=standard_embed(
                title="Nice!",
                text="That is the basics on ability use. You can check what "
                     "abilities you know by using the **.s** or **.stats** "
                     "command, which will also show you the shortcut in "
                     "vertical bars. For Regenerate it would be **.reg**. "
                     f"To learn more about abilities, check out the {abil_channel.mention} "
                     "channel.\n\nNow that you are an expert on abilities, "
                     "lets take a look at equipment. Here take these..."))
        await sleep(4)
        await ctx.send(embed=give_item_embed("Maw", "Yamatos Training Katana", hero.name))
        await sleep(1)
        await ctx.send(embed=give_item_embed("Maw", "Cloth Armor", hero.name))
        await sleep(1)
        await ctx.send(
            embed=standard_embed(
                title="Equipment",
                text=f'Equipment is pretty rare. You only receive equipment from '
                     f'defeating massive creatures called Apexes in the Apex Meadow. '
                     f'Armor is obtained at a pretty steep price from the shopkeep. '
                     f'\n\nNow that you have them, try the commands: **.equip "yamatos '
                     f'training katana"** *(.eq ytk for short)*, and **.equip '
                     f'"cloth armor"** *(.eq ca for short)*.'))


@bot.command(aliases=["rec"])
async def recharge(ctx, recover_target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Recharge"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Recharge'."))
            return

        # Check if target_value is numerical
        try:
            recover_target = int(recover_target)
        except ValueError:
            await ctx.send(block_text("You must select a numerical target to recover, try .recharge 1"))
            return

        # Check not over ep
        if recover_target > hero.max_ep + hero.bonus_ep - hero.current_ep:
            return f"You cannot recover more than your maximum EP"

        ten_percent_of_max = (hero.max_hp + hero.bonus_hp) * 0.1

        # Check if hero has enough health
        price = math.floor(recover_target * ten_percent_of_max)
        maximum = hero.current_hp // ten_percent_of_max
        if price > hero.current_hp:
            await ctx.send(
                block_text(f"You are not strong enough to recover {recover_target} EP (Max Recoverable: {maximum})"))
            return

        # Reduce HP by 10% for each recovered EP
        hero.current_hp -= price
        hero.current_ep += recover_target

        if hero.current_hp <= 0:
            hero.current_hp = 1

        result = f"{hero.name} sacrifices their mortal being for power\n*{hero.current_hp}/{hero.max_hp + hero.bonus_hp}* HP\n" \
                 f"{hero.current_ep}/{hero.max_ep + hero.bonus_ep} EP"

        await ctx.send(embed=ability_card_embed(hero, "Recharge", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["sb"])
async def shieldbash(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Shieldbash"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Shieldbash'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Shieldbash'."))
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(f"You must defeat lower level raid monsters before targeting {target}.")
            return

        hero.current_ep -= 1

        monster.status.append("Dazed")

        if "Normal" in monster.status:
            monster.status.remove("Normal")

        result = f"The {target} is dazed from a thunderous shield strike!"
        await ctx.send(embed=ability_card_embed(hero, "Shieldbash", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)

    elif ctx.channel.id in [welcome, general_chat, the_shop, bugs, ideas_features]:
        return

    else:
        if target != "Dummy":
            pass

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        hero.armory.append("Yamatos Training Katana")
        hero.armory.append("Cloth Armor")

        hero.training_stage = 5

        abil_channel = bot.get_channel(id=897223260964528159)

        await ctx.send(
            embed=ability_card_embed(
                hero, "Shieldbash", f"The Test Dummy is dazed from a thunderous shield strike!"))
        await sleep(3)
        await ctx.send(
            embed=standard_embed(
                title="Nice!",
                text="That is the basics on ability use. You can check what "
                     "abilities you know by using the **.s** or **.stats** "
                     "command, which will also show you the shortcut in "
                     "vertical bars. For Shieldbash it would be **.sb**.\n\n"
                     f"To learn more about abilities check out the {abil_channel.mention} channel"
                     "\n\nNow that you are an expert on abilities, lets take a "
                     "look at equipment. Here take these..."))
        await sleep(4)
        await ctx.send(embed=give_item_embed("Maw", "Yamatos Training Katana", hero.name))
        await sleep(1)
        await ctx.send(embed=give_item_embed("Maw", "Cloth Armor", hero.name))
        await sleep(1)
        await ctx.send(
            embed=standard_embed(
                title="Equipment",
                text=f'Equipment is pretty rare. You only receive equipment from '
                     f'defeating massive creatures called Apexes in the Apex Meadow. '
                     f'Armor is obtained at a pretty steep price from the shopkeep. '
                     f'\n\nNow that you have them, try the commands: **.equip "yamatos '
                     f'training katana"** *(.eq ytk for short)*, and **.equip '
                     f'"cloth armor"** *(.eq ca for short)*.'))


@bot.command(aliases=["ss"])
async def spearsling(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if "Silenced" in hero.status:
            if hero.silenced_ability_name == "Spearsling":
                await ctx.send("This ability has been silenced! Kill the Apex to return it!")
                return

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Spearsling"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Spearsling'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Spearsling'."))
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(block_text(f"You must defeat lower level raid monsters before targeting {target}."))
            return

        if "Bleeding" in monster.status:
            await ctx.send(block_text(f"{target} is already bleeding!"))
            return

        hero.current_ep -= 1

        dmg = random.randint(60, 150)

        # Deal initial damage
        monster.current_hp -= dmg
        if monster.current_hp < 0:
            monster.current_hp = 0

        # Assign Bleeding Status
        monster.status.extend(["Bleeding", "Bleeding", "Bleeding"])

        if "Normal" in monster.status:
            monster.status.remove("Normal")

        result = f"God's Spear is propelled from your hand with a hellish force so powerful it penetrates through the {target}. " \
                 f"The {target} takes **{dmg}** damage and begins a torrential **bleed**."
        await ctx.send(embed=ability_card_embed(hero, "Spearsling", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["sta"])
async def stalk(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Stalk"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Stalk'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Stalk'."))
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(f"You must defeat lower level raid monsters before targeting {target}.")
            return

        hero.current_ep -= 1

        monster.status.append("Marked")

        if "Normal" in monster.status:
            monster.status.remove("Normal")

        result = f"{hero.name} has started hunting the {target}"

        await ctx.send(embed=ability_card_embed(hero, "Stalk", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["tin"])
async def tinker(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Tinker"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Tinker'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Tinker'."))
            return

        unimproved_list = [item for item in hero.inventory if
                           item[:8] != "Improved" and item not in ["Monster Scanner", "Bardic Tale"]]

        if not unimproved_list:
            await ctx.send(block_text(f"Your inventory has no items left to improve!"))
            return

        tink_item = random.choice(unimproved_list)

        hero.inventory.remove(tink_item)

        hero.inventory.append(f"Improved {tink_item}")

        hero.current_ep -= 1

        result = f"{tink_item} has been upgraded!"
        await ctx.send(embed=ability_card_embed(hero, "Tinker", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["tra"])
async def transform(ctx, target_mode):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        target_mode = target_mode.lower()

        if not can_use_ability(hero, "Transform"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Transform'."))
            return

        if hero.raiding:
            await ctx.send(block_text("The Last Bastion prevents your Rod Of Lordly Might from transforming!"))
            return

        if target_mode not in ["battleaxe", "barrier", "spear"]:
            await ctx.sen("That is not a valid configuration for the Rod Of Lordly Might\n"
                          "Valid Configurations: Battleaxe, Spear, Barrier")
            return

        legendary = Legendary()

        # Unequip Rod Mode
        mode = hero.equipment_mode

        legendary.rod_of_lordly_might(mode_set=mode)

        legendary.unequip(hero)

        # Equip New Rod
        new_legendary = Legendary()

        new_legendary.rod_of_lordly_might(mode_set=target_mode)

        # Send data before updating stats
        await ctx.send(embed=rolm_embed(new_legendary, hero, target_mode))

        new_legendary.equip(hero)

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["med"])
async def meditate(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Meditate"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Meditate'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Meditate'."))
            return

        available_points = hero.meditate_score

        if hero.meditate_score == 0:
            await ctx.send(block_text(f"You have no meditation points to spend!"))
            return

        def end_meditation_embed(hero_object, available_points, attack_mod=0, def_mod=0, hp_mod=0):
            base = discord.Embed(
                title=f"Hero Stats",
                colour=discord.Colour.teal(),
                description=f"{hero.name} has **{available_points}** points remaining.\n"
                            f"Attack: *{hero_object.atk + hero_object.bonus_atk - attack_mod} + {attack_mod}*\n"
                            f"Defense: *{hero_object.defense + hero_object.bonus_def - def_mod} + {def_mod}*\n"
                            f"HP: *{hero_object.max_hp + hero_object.bonus_hp - hp_mod} + {hp_mod}*")
            base.set_thumbnail(url="https://i.pinimg.com/originals/ee/3e/57/ee3e57634e49ce45ac127974c1ec6f7d.jpg")
            base.set_author(name=f"{hero_object.name} Insight",
                            icon_url="https://i.pinimg.com/originals/da/35/1f/da351f5d362be9249f11309dab48d545.gif")
            return base

        def meditate_embed(hero_object, available_points):
            base = discord.Embed(
                title=f"Hero Stats",
                colour=discord.Colour.teal(),
                description=f"{hero.name} has **{available_points}** points available to spend.\n\n"
                            f"**Current Stats**\n"
                            f"Attack: *{hero_object.atk + hero_object.bonus_atk}*\n"
                            f"Defense: *{hero_object.defense + hero_object.bonus_def}*\n"
                            f"HP: *{hero_object.max_hp + hero_object.bonus_hp}*")
            base.set_thumbnail(url="https://i.pinimg.com/originals/ee/3e/57/ee3e57634e49ce45ac127974c1ec6f7d.jpg")
            base.set_author(name=f"{hero_object.name} Insight",
                            icon_url="https://i.pinimg.com/originals/da/35/1f/da351f5d362be9249f11309dab48d545.gif")
            return base

        def check_med_msg(msg):
            try:
                return msg.author == ctx.author and msg.channel == ctx.channel and isinstance(int(msg.content), int) \
                       and int(msg.content) <= available_points
            except ValueError:
                return False

        await ctx.send(embed=meditate_embed(hero, available_points))

        # Get attack change
        await ctx.send(block_text(f"Allocate Attack Points: (Number between 0 and {available_points})"))
        try:
            msg = await bot.wait_for("message", check=check_med_msg, timeout=45)
        except TimeoutError:
            await ctx.send(block_text("Meditation canceled"))
            return

        attack_mod = int(msg.content)
        hero.meditate_score -= attack_mod
        hero.atk += attack_mod
        available_points -= attack_mod

        if available_points == 0:
            await ctx.send(embed=end_meditation_embed(hero, available_points, attack_mod))
            return

        # Get defense change
        await ctx.send(block_text(f"Allocate Defense Points: (Number between 0 and {available_points})"))
        try:
            msg = await bot.wait_for("message", check=check_med_msg, timeout=45)
        except TimeoutError:
            await ctx.send(embed=end_meditation_embed(hero, available_points, attack_mod))
            return

        defense_mod = int(msg.content)
        hero.meditate_score -= defense_mod
        hero.defense += defense_mod
        available_points -= defense_mod

        if available_points == 0:
            await ctx.send(embed=end_meditation_embed(hero, available_points, attack_mod, defense_mod))
            return

        # Get hp change
        await ctx.send(block_text(f"Max Health Points: (Number between 0 and {available_points})"))
        try:
            msg = await bot.wait_for("message", check=check_med_msg, timeout=45)
        except TimeoutError:
            await ctx.send(embed=end_meditation_embed(hero, available_points, attack_mod, defense_mod))
            return

        health_mod = int(msg.content)
        hero.meditate_score -= health_mod
        hero.max_hp += health_mod
        available_points -= health_mod

        await ctx.send(embed=end_meditation_embed(hero, available_points, attack_mod, defense_mod, health_mod))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["dk"])
async def dragon_kick(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Dragon Kick"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Dragon Kick'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Dragon Kick'."))
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)
        secondary_monster = select_random_monster(1, current_mon_directory, target)[0]

        if monster.position_locked:
            await ctx.send(f"You must defeat lower level raid monsters before targeting {target}.")
            return

        hero.current_ep -= 1

        if monster.rank == "Apex":
            kick_damage = math.ceil(monster.max_hp * 0.05)
        else:
            kick_damage = math.ceil(monster.max_hp * 0.2)

        secondary_damage = math.ceil(monster.max_hp * 0.3)

        monster.current_hp -= kick_damage
        if monster.current_hp < 0:
            monster.current_hp = 0

        if secondary_monster != "None":
            striking_target = secondary_monster.name
            secondary_monster.current_hp -= secondary_damage
            if secondary_monster.current_hp < 0:
                secondary_monster.current_hp = 0
        else:
            striking_target = "Boulder"
            secondary_damage = kick_damage
            monster.current_hp -= kick_damage
            if monster.current_hp < 0:
                monster.current_hp = 0

        ki_explosion = False
        if "Ki Bomb" in monster.status and len(current_mon_directory) > 1:
            monster.status.remove("Ki Bomb")
            ki_explosion = True

        if not monster.status:
            monster.status.append("Normal")

        result = f"{hero.name} obliterates **{target}** with a fierce dragon kick for **{kick_damage}** damage!.\n\n" \
                 f"{target} is launched into a **{striking_target}** for **{secondary_damage}** damage!\n\n" \
                 f"**__{target}__**\n" \
                 f"*{monster.current_hp}/{monster.max_hp}* HP" \
 \
            # Ki bomb activate
        if ki_explosion:
            exploded_monsters = select_random_monster(2, current_mon_directory, target)

            if exploded_monsters:
                # Roll Ki Bomb damage
                skill_dmg = hero.sp_atk["Ki Bomb"]["dmg"]
                floor_dmg = skill_dmg // 2
                kb_dmg = random.randint(floor_dmg, skill_dmg)

                for target_struck in exploded_monsters:
                    target_struck.current_hp -= kb_dmg
                    if target_struck.current_hp < 0:
                        target_struck.current_hp = 0

                result = f"{hero.name} obliterates **{target}** with a fierce dragon kick for **{kick_damage}** damage!.\n\n" \
                         f"{target} is launched into a **{secondary_monster.name}** for **{secondary_damage}** damage!\n\n" \
                         f"**Ki Bomb Activated!**\n" \
                         f"**{target}** detonates for **{kb_dmg}** damage striking: **{', '.join([mon.name for mon in exploded_monsters])}**."

        await ctx.send(embed=ability_card_embed(hero, "Dragon Kick", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["kb"])
async def ki_bomb(ctx, target):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        # Assign directory for channel
        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)

        if target is not None:
            target = shortcut_return(target.title())
        else:
            await ctx.send(block_text("You must designate a target."))
            return

        if not can_use_ability(hero, "Ki Bomb"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Ki Bomb'."))
            return

        if hero.current_ep < 1:
            await ctx.send(block_text(f"{hero.name} does not have enough EP to use 'Ki Bomb'."))
            return

        if not monster_present(target, current_mon_directory):
            await ctx.send(block_text(f"{target} is not in the Maw."))
            return

        monster = get_monster(current_mon_directory, target)

        if monster.position_locked:
            await ctx.send(f"You must defeat lower level raid monsters before targeting {target}.")
            return

        if "Ki Bomb" in monster.status:
            await ctx.send(block_text(f"{monster.name} is already afflicted with a Ki Bomb!"))
            return

        hero.current_ep -= 1

        monster.status.append("Ki Bomb")

        if "Normal" in monster.status:
            monster.status.remove("Normal")

        result = f"{hero.name} has placed a Ki Bomb within {target}."

        await ctx.send(embed=ability_card_embed(hero, "Ki Bomb", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


@bot.command(aliases=["mp"])
async def monastic_pilgrimage(ctx):
    if ctx.channel.id in [beyond_the_gates, the_meadow, beyond_the_battlefield, heart_of_the_maw, testing_home,
                          raid_1, raid_2, raid_3]:

        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        if not can_use_ability(hero, "Monastic Pilgrimage"):
            await ctx.send(block_text(f"{hero.name} does not know the ability 'Monastic Pilgrimage'."))
            return

        med_atk = hero.atk - 1
        med_def = hero.defense - 1
        med_hp = hero.max_hp - 90

        hero.atk = 1
        hero.defense = 1
        hero.max_hp = 90

        if hero.current_hp > hero.max_hp + hero.bonus_hp:
            hero.current_hp = hero.max_hp + hero.bonus_hp

        returned_med = med_atk + med_def + med_hp
        hero.meditate_score += returned_med

        del hero.sp_atk["Monastic Pilgrimage"]

        result = f"{hero.name} has completed a Monastic Pilgrimage!\n" \
                 f"Attack, Max Health, and Defense reset to **1**\n" \
                 f"{returned_med} meditation points returned.\n\n" \
                 f"Ability **Monastic Pilgrimage** removed."

        await ctx.send(embed=ability_card_embed(hero, "Monastic Pilgrimage", result))

        records = open_hero_records(hero.owner)
        records["records"]["abilities used"] += 1
        close_hero_records(records, hero.owner)


# MOD COMMANDS ________________________________________________________________________________________


@bot.command()
async def give_gold(ctx, target, amount=100):
    if ctx.message.author.id == admin:
        hero = get_hero(HERO_LIST, target.title())
        hero.gold += int(amount)
        await ctx.send(block_text(f"{target.title()} received {amount} gold!"))


@bot.command()
async def clear(ctx, amount=1):
    if ctx.message.author.id == admin or ctx.message.author.id == 895349269060542474:
        await ctx.channel.purge(limit=amount)
    else:
        await ctx.send(block_text("No."))


@bot.command()
async def save(ctx):
    if ctx.message.author.id == admin:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)
        save_hero(hero)
        await ctx.send(block_text(f"{hero.name} has been saved."))


@bot.command()
async def show_hero(ctx, hero_name, attributes=False):
    if ctx.message.author.id == admin:
        if hero_name == "all":
            for hero in HERO_LIST:
                await ctx.send(embed=show_hero_embed(hero))
                return

        for hero in HERO_LIST:

            if hero.name == hero_name.title():

                if not attributes:
                    await ctx.send(embed=show_hero_embed(hero))
                    return
                else:
                    await ctx.send(hero.__dict__)
                    return

        await ctx.send(block_text("Hero not found"))


@bot.command()
async def shutdown(ctx):
    if ctx.message.author.id == admin:
        for hero in HERO_LIST:
            with open(f"characters/{hero.name}.json", "w") as f:
                json.dump(hero.__dict__, f, indent=2)

        await ctx.send(block_text("HERO LIST SAVED"))

        for raid in MASTER_RAID_DICT:
            with open(f"raids/{MASTER_RAID_DICT[raid].raider}.pickle", "wb") as f:
                pickle.dump(MASTER_RAID_DICT[raid], f)

        await ctx.send(block_text("RAID LIST SAVED"))

        with open("leaderboards/leaderboard.pickle", "wb") as f:
            pickle.dump(LEADERBOARD, f)

        await ctx.send(block_text("LEADERBOARDS SAVED"))

        await ctx.send(block_text("Goodbye World"))
        await bot.close()


@bot.command()
async def show_monsters(ctx, list, target=None):
    if ctx.message.author.id == admin:
        hero_name = set_hero_user(ctx.message.author.id)
        hero = get_hero(HERO_LIST, hero_name)

        monster_string = []
        if list == "1":
            for monster in MONSTER_LIST:
                monster_string.append(f"{monster.rank}: {monster.name}\n")
        if list == "2":
            for monster in MONSTER_LIST2:
                monster_string.append(f"{monster.rank}: {monster.name}\n")
        if list == "3":
            for monster in MONSTER_LIST3:
                monster_string.append(f"{monster.rank}: {monster.name}\n")

        current_mon_directory = set_directory_from_channel(hero.name, ctx.channel.id)
        if target is not None:
            mon = get_monster(current_mon_directory, target)
            await ctx.send(f"defense :{mon.defense}")
            return

        await ctx.send(code_block(f"{''.join(monster_string)}"))


@bot.command()
async def show_leaderboards(ctx):
    if ctx.message.author.id == admin:
        await ctx.send(block_text(LEADERBOARD.__dict__))


@bot.command()
async def show_raids(ctx):
    if ctx.message.author.id == admin:
        await ctx.send(block_text(list(MASTER_RAID_DICT.keys())))


@bot.command(aliases=["stat"])
async def set_stat(ctx, target, stat, value):
    if ctx.message.author.id == admin:
        hero = get_hero(HERO_LIST, target.title())
        value = int(value)
        if stat.lower() not in ["atk", "def", "maxhp", "curhp", "maxep", "curep", "init"]:
            await ctx.send(block_text(f"I think something is spelled wrong here, tray again with the following stat:\n"
                                      f"'atk' - attack\n"
                                      f"'def' - defense\n"
                                      f"'maxhp' - max hp\n"
                                      f"'curhp' - current hp\n"
                                      f"'maxep' - max ep\n"
                                      f"'curep' - current ep\n"
                                      f"'init' - initiative"))
            return

        stat = stat.lower()
        if stat == "atk":
            hero.atk = value
        elif stat == "def":
            hero.defense = value
        elif stat == "maxhp":
            hero.max_hp = value
        elif stat == "curhp":
            hero.current_hp = value
        elif stat == "maxep":
            hero.max_ep = value
        elif stat == "curep":
            hero.current_ep = value
        elif stat == "init":
            hero.initiative = value

        await ctx.send(block_text(f"{stat} set to {value}"))


@bot.command()
async def add_item(ctx, target, item):
    if ctx.message.author.id == admin:
        if target.title() not in [hero.name for hero in HERO_LIST]:
            await ctx.send(block_text("Target not found"))
            return

        hero = get_hero(HERO_LIST, target.title())
        item = shortcut_return(item.title())
        item_list = Items()
        if item in item_list.master:
            hero.inventory.append(item)
            await ctx.send(block_text(f"{item} added to {hero.name} inventory."))
        else:
            await ctx.send(block_text(f"{item} not found in the item master list."))


@bot.command()
async def add_key(ctx, target, key):
    if ctx.message.author.id == admin:
        if ctx.message.author.id == admin:
            if target.title() not in [hero.name for hero in HERO_LIST]:
                await ctx.send(block_text("Target not found"))
                return
        hero = get_hero(HERO_LIST, target.title())
        key = shortcut_return(key.title())
        item_list = Items()
        if key in item_list.keys:
            hero.keys.append(key)
            await ctx.send(block_text(f"{key} added to {hero.name} keyring."))
        else:
            await ctx.send(block_text(f"{key} not found in the item master list."))


@bot.command()
async def add_armory(ctx, target, equipment):
    if ctx.message.author.id == admin:
        if ctx.message.author.id == admin:
            if target.title() not in [hero.name for hero in HERO_LIST]:
                await ctx.send(block_text("Target not found"))
                return
        hero = get_hero(HERO_LIST, target.title())
        equipment = shortcut_return(equipment.title())
        arms = Armors()
        legs = Legendary()

        master = []
        for i in range(len(arms.armors)):
            master.append(arms.armors[i])
        for i in range(len(legs.legends)):
            master.append(legs.legends[i])

        if equipment not in master:
            await ctx.send(block_text(f"{equipment} not found in master armor or legend list"))
            return

        hero.armory.append(equipment)

        await ctx.send(block_text(f"{equipment} added"))
        return


@bot.command()
async def add_level(ctx, target, number_of_levels):
    if ctx.message.author.id == admin:
        if target.title() not in [hero.name for hero in HERO_LIST]:
            await ctx.send(block_text("Target not found"))
            return
    hero = get_hero(HERO_LIST, target.title())

    for _ in range(int(number_of_levels)):
        level_up(hero)

    await ctx.send(block_text(f"{hero.name} was boosted {number_of_levels} levels."))
    return


@bot.command()
async def show_global_status(ctx):
    if ctx.message.author.id == admin:
        await ctx.send(block_text(GLOBAL_STATUS_DICT))

@bot.command()
async def add_ability(ctx, target, ability):
    if ctx.message.author.id == admin:
        hero = get_hero(HERO_LIST, target.title())
        ability = ability.title()
        level_abilities = {
        "Martyr": {
            "name": "Martyr",
            "text": f"{hero.name} charges to defend an ally from massive damage in their next fight",
            "dmg": 0,
            "effect": "martyr",
            "description": f"Passive buff: Creates a perpetual 33% chance to block a critical strike in any hero's fight or raid event, rewards XP on success."
            },
        "Stalk": {
            "name": "Stalk |sta|",
            "text": f"{hero.name} studies the weaknesses of their next prey",
            "dmg": 0,
            "effect": "stalk",
            "description": f"Greatly reduced failure rate of your next assassination attempt."
            },
        "Obsecrate": {
            "name": "Obsecrate 2EP |obs|",
            "text": f"{hero.name} beseeches the pantheon",
            "dmg": 0,
            "effect": "obsecrate",
            "description": "Applies a random effect to target hero"
            },
        "Executor": {
            "name": "Executor |exe|",
            "text": f"{hero.name} senses weakened prey",
            "dmg": 0,
            "effect": "executor",
            "description": "Doubles damage against monsters with hp ratings at or lower than 'severely injured'."
            },
        "Tinker": {
            "name": "Tinker |tin|",
            "text": f"Artificers have a way with inventories.",
            "dmg": 0,
            "effect": "tinker",
            "description": "Improves a random inventory item to heighten effects"
            },
        "Fireball": {
            "name": "Fireball 3EP |fb|",
            "text": f"A blazing sphere of death",
            "dmg": 100,
            "effect": "fireball",
            "description": "Strikes a target creature and three random monsters on the field."
        },
        "Battlemage": {
            "name": "Battlemage 7EP |bm|",
            "text": f"The physical manifestation of pure energy",
            "dmg": 1,
            "effect": "battlemage",
            "description": "Exchanges all EP over cost for Attack/Defense/Crit until struck by monster critical."
        },
        "Detonate": {
            "name": "Detonate |det|",
            "text": "What's yours is mine... to detonate",
            "dmg": 100,
            "effect": "detonate",
            "description": "Destroys a target monsters item to deal massive damage to its holder"
        },
        "Mass Casualty": {
            "name": "Mass Casualty 3EP |mc|",
            "text": "In a field of opposition, the options are endless",
            "dmg": 0,
            "effect": "mass casualty",
            "description": f"{hero.name} attempts to assassinate every monster on the field"
        },
        "Art Of War": {
            "name": "Art Of War",
            "text": "If this body isn't strong enough to stop my blade, perhaps the adjacent one is.",
            "dmg": 0,
            "effect": "art of war",
            "description": "Passive buff: Damage exceeding the current targets HP extends to a random target on the "
                           "battefield as true damage"
        },
        "Retribution": {
            "name": "Retribution",
            "text": "With armor this strong, might as well put spikes on it",
            "dmg": 0,
            "effect": "retribution",
            "description": "Passive buff: Reflects damage received back at the attacker."
        },
        "Plane Shift": {
            "name": "Plane Shift |ps| Rank-EP",
            "text": "I could simply snap my fingers. They would all cease to exist.",
            "dmg": 0,
            "effect": "plane_shift",
            "description": "Warp out current main board field monsters for monsters from desired numerical rank. "
                           "Does not work while raiding."
        },
        "Divinity": {
            "name": "Divinity |div|",
            "text": f"In faith, a forked path is always inevitable.",
            "dmg": 0,
            "effect": "divinity",
            "description": "Allows you to choose a divine path"
        },
        "Meditate": {
            "name": "Meditate |med|",
            "text": f"Knowing oneself is the true path to success",
            "dmg": 0,
            "effect": "meditate",
            "description": "Allows you to spend meditate points to augment your attack/defense/HP stats at will"
        },
        "Dragon Kick": {
            "name": "Dragon Kick |dk|",
            "text": f"The kick practiced 10,000 times",
            "dmg": 0,
            "effect": "dragon kick",
            "description": "Deals 20% of targets max HP as damage to itself, and 100% to another random target."
        },
        "Ki Bomb": {
            "name": "Ki Bomb |kb|",
            "text": f"There is now power like the control of vital energies",
            "dmg": 100,
            "effect": "dragon kick",
            "description": "Plants an energy bomb on the target, exploding on target death or Dragon Kick dealing moderate"
                           " damage to two other random targets."
        },
        "Monastic Pilgrimage": {
            "name": "Monastic Pilgrimage |mp|",
            "text": f"Rest young one. Tomorrow you grow stronger.",
            "dmg": 0,
            "effect": "monastic pilgrimage",
            "description": "Returns all spent meditation points and resets attack, defense and max health."
        },
        "Shieldbash": {
            "name": "Shieldbash |sb|",
            "text": f"{hero.name} strikes the foe with a thunderous shield bash!",
            "dmg": 15,
            "effect": "dazed",
            "description": "Dazes a monster, causing them to miss their next attack."
                    },
        "Helmbreaker": {
            "name": "Helmbreaker |hb|",
            "text": f"{hero.name} raises their sword to the air and cleaves the earth with a forceful slash!",
            "dmg": 15,
            "effect": "sunder",
            "description": "Reduces target armor by half"
            },
        "Assassinate": {
            "name": "Assassinate |ass|",
            "text": f"{hero.name} slips into the shadows and explodes above the monster with a lunging strike!",
            "dmg": 7,
            "effect": "guillotine",
            "description": "Chance to instantly kill target monster, scaling success rate with leveling."
            },
        "Regenerate": {
            "name": "Regenerate |reg|",
            "text": f"{hero.name} casts a healing aura!",
            "dmg": 15,
            "effect": "regenerate",
            "description": "Heals a target hero for 75% of their max HP"
            },
        "Intuition": {
            "name": "Intuition |int|",
            "text": f"{hero.name} checks for hidden items.",
            "dmg": 0,
            "effect": "alchemy",
            "description": "Chance for monster without an item to hold one, or for held item to increase one tier."
            },
        "Recharge": {
            "name": "Recharge |rec|",
            "text": f"With power, comes sacrifice",
            "dmg": 0,
            "effect": "recharge",
            "description": "Sacrifices HP for EP"
        },
        "Magic Missile": {
            "name": "Magic Missile |mm|",
            "text": f"{hero.name} creates three glowing darts that seek out monsters.",
            "dmg": 15,
            "effect": "missile",
            "description": "Deals moderate damage, chance of critical damage."
            }

    }
    hero.sp_atk[ability] = level_abilities[ability]
    await ctx.send(f"{hero.name} now knows {ability}")

# Run the bot with the token
bot.run(config["token"])




