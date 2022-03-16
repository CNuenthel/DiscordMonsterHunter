import random
import json
import math
from herobuilder import HeroBuilder

from os.path import exists

HERO_CRIT_CHANCE = 6
MON_CRIT_CHANCE = 10


def add_user_data(user_object, hero_name):
    new_data = {"user_name": user_object.name,
                "user_id": user_object.id,
                "user_hero": hero_name,
                "records": {
            "highest damage": 0,
            "total monsters killed": 0,
            "total damage done": 0,
            "times rested": 0,
            "legendary monsters killed": 0,
            "key monsters killed": 0,
            "items used": 0,
            "combats initiated": 0,
            "abilities used": 0,
            "keys collected": 0,
            "gold pieces": 0,
            "highest raid complete": 0,
            "apexes slaughtered": 0
        }
    }

    with open(f"users/{user_object.id}.json", "w") as file:
        json.dump(new_data, file, indent=4)
    print(f"New user added: {user_object.name}")


def apex_status_afflict(hero, apex):
    aura = apex.aura

    if aura == "Silencer":
        if "Silenced" not in hero.status:
            hero.status.append("Silenced")

            # Select random hero skill
            ability_list = list(hero.sp_atk.keys())

            if "Transform" in ability_list:
                ability_list.remove("Transform")

            random_ability = random.choice(ability_list)
            silenced_ability = hero.sp_atk[random_ability]

            # Record silenced ability
            hero.silenced_ability = silenced_ability
            hero.silenced_ability_name = random_ability

            # Remove ability
            del hero.sp_atk[random_ability]

            return ["Silencer",
                    f"{hero.name}'s **{random_ability}** ability has been silenced! "
                    f"Kill the Apex to remove the silence!",
                    ]

    elif aura == "Barbed":
        barb_damage = random.randint(15, 30)
        hero.current_hp -= barb_damage
        if hero.current_hp <= 0:
            hero.current_hp = 1

        return ["Barbed",
                f"{hero.name} suffers **{barb_damage}** points of damage from fighting in the Meadow's barbs!",
                ]

    if aura == "Drainer":
        if "Drained" not in hero.status:
            hero.status.append("Drained")
            hero.drained_ep = hero.max_ep

        # Drain max ep, or health if out of max ep
        if hero.max_ep != 0:
            hero.max_ep -= 1
            if hero.current_ep > hero.max_ep:
                hero.current_ep = hero.max_ep
            result = f"{hero.name} has had their max energy sapped by the meadow (max ep reduced by 1)"
        else:
            hp_damage = math.ceil(hero.max_hp * 0.1)
            hero.current_hp -= hp_damage
            result = f"The meadow saps {hero.name}'s life force for **{hp_damage}** points of damage!"
            if hero.current_hp < 0:
                hero.current_hp = 1

        return ["Drainer", result]

    if aura == "Absorbing":
        recovered_health = random.randint(50, 400)
        apex.current_hp += recovered_health

        if apex.current_hp > apex.max_hp:
            apex.current_hp = apex.max_hp

        return ["Absorbing",
                f"{apex.name} has absorbed **{recovered_health}** points of health from the Meadow!",
                ]

    if aura == "Caustic":
        if "Corrosive" not in hero.status:
            hero.status.append("Corrosive")

            # Record removed defense
            removed_defense = hero.defense // 2
            hero.defense -= removed_defense
            hero.caustic_defense = removed_defense

            if hero.armor != "None":
                from equipment import Armors
                armor = Armors()

                if hero.armor == "Cloth Armor":
                    armor.cloth_armor()
                elif hero.armor == "Leather Armor":
                    armor.leather_armor()
                elif hero.armor == "Mail Armor":
                    armor.mail_armor()
                elif hero.armor == "Plate Armor":
                    armor.plate_armor()

                armor.unequip(hero.name)

                result = f"{hero.name}'s **{hero.armor}** has **dissolved** from fighting in the caustic Meadow, " \
                         f"armor reduced by **{removed_defense}**!!"

                hero.armor = "None"

            else:
                result = f"As {hero.name} fights in the caustic Meadow, armor reduced by **{removed_defense}**!"

            return ["Caustic", result]

    if aura == "Breaker":
        if "Fractured" not in hero.status:
            hero.status.append("Fractured")

            hero.fractured_crit = hero.crit_multiplier
            hero.crit_multiplier = 0

            return ["Breaker",
                    f"{hero.name} has been crushed by the Apex! {hero.name} will deal no damage on **critical "
                    f"rolls**, taking small return damage instead"]

    return "no effect"


def apex_status_cure(hero, aura):

    if aura == "Silencer":
        if "Silenced" in hero.status:
            hero.status.remove("Silenced")
            return_ability = hero.silenced_ability_name
            ability = hero.silenced_ability

            hero.sp_atk[return_ability] = ability
            return

    elif aura == "Drainer":
        if "Drained" in hero.status:
            hero.status.remove("Drained")
            hero.max_ep = hero.drained_ep
            return

    elif aura == "Caustic":
        if "Corrosive" in hero.status:
            hero.defense += hero.caustic_defense

    elif aura == "Breaker":
        if "Fractured" in hero.status:
            hero.status.remove("Fractured")
            hero.crit_multiplier += hero.fractured_crit
            delattr(hero, "fractured_crit")


def can_use_ability(hero, ability_name):
    if ability_name in list(hero.sp_atk.keys()):
        return True
    return False


def close_hero_records(data, discord_id):
    with open(f"users/{discord_id}.json", "w") as file:
        json.dump(data, file, indent=4)


def inventory_capped(hero):
    if len(hero.inventory) >= 10 and "Organized" not in hero.status:
        return True
    elif len(hero.inventory) >= 15 and "Organized" in hero.status:
        return True
    return False


def check_if_banned(name):
    name = name.lower()
    banned_list = ['anal', 'anus', 'arse', 'ass', 'ballsack', 'balls', 'bastard', 'bitch', 'biatch',
                     'bloody', 'blowjob', 'blow job', 'bollock', 'bollok', 'boner', 'boob', 'bugger', 'bum',
                     'butt', 'buttplug', 'clitoris', 'cock', 'coon', 'crap', 'cunt', 'damn', 'dick',
                     'dildo', 'dyke', 'fag', 'feck', 'fellate', 'fellatio', 'felching', 'fuck', 'f u c k',
                     'fudgepacker', 'fudge packer', 'flange', 'Goddamn', 'God damn', 'hell', 'homo', 'jerk',
                     'jizz', 'knobend', 'knob end', 'labia', 'lmao', 'lmfao', 'muff', 'nigger', 'nigga',
                     'omg', 'penis', 'piss', 'poop', 'prick', 'pube', 'pussy', 'queer', 'scrotum', 'sex',
                     'shit', 's hit', 'sh1t', 'slut', 'smegma', 'spunk', 'tit', 'tosser', 'turd', 'twat',
                     'vagina', 'wank', 'whore', 'wtf']

    if name in banned_list:
        return True
    return False


def check_if_taken(name):
    if exists(f"characters/{name}.json"):
        return True
    return False


def check_inventory(inventory_list, object_to_verify):
    if object_to_verify in inventory_list:
        return True
    return False


def check_xp(hero):
    level_list = [0, 145, 300, 500, 900, 1200, 1700, 2200, 2700, 3200, 3800, 4500, 6002, 8683, 12570,
                  18207, 26379, 38230, 55413, 80328, 116455, 168840, 244798, 354937, 514638, 746205,
                  1081977, 1568847, 2274808, 3298451]
    if hero.level == 30:
        return False
    elif hero.xp > level_list[hero.level]:
        return True
    return False


def get_hero(hero_list, hero_name):
    for hero in hero_list:
        if hero.name == hero_name:
            return hero
    return False


def get_monster(monster_list, monster_name: str):
    for monster in monster_list:
        if monster_name == monster.name:
            return monster
    return False


def get_owner_name(owner_id):
    with open(f"users/{owner_id}", "r") as f:
        user_data = json.load(f)
        return user_data["user_name"]


def get_raid(hero_name, raid_dict):
    for raid in list(raid_dict.keys()):
        if raid == hero_name:
            return raid_dict[raid]


def gp_set(rank):
    if rank == "Apex":
        return 25000
    elif rank == "Legendary":
        return 250
    else:
        return rank*10


def hero_target_present(target, hero_list):
    master_list = ["None"]
    [master_list.append(hero.name) for hero in hero_list]

    if target in master_list:
        return True
    return False


def increment_dark_druid(dark_druid, mtr_rank):
    if mtr_rank == "Apex":
        mtr_rank = 11
    if mtr_rank == "Legendary":
        mtr_rank = 10

    if mtr_rank == 11:
        dark_druid.hunt_data['apex_aspect'] += 1
        if dark_druid.hunt_data['apex_aspect'] == 1:
            dark_druid.sp_atk["Apex Ritual"] = {
                "name": "Apex Ritual |aritual|",
                "text": f"All hail the demon god, {dark_druid.name}",
                "dmg": 0,
                "effect": "apex_ritual",
                "description": "Evolves aspect of the Apex, giving Apex Form ability and permanently "
                               "increases critical multiplier and initiative by 25%"
            }

            return [True,
                    f"Final Dominance complete! Apex Ritual can now be conducted. Check abilities for more information.",
                    "Apex"]

    elif mtr_rank == 10:
        dark_druid.hunt_data['legend_aspect'] += 1
        if dark_druid.hunt_data['legend_aspect'] == 15:
            dark_druid.sp_atk["Legend Ritual"] = {
                "name": "Legend Ritual |lritual|",
                "text": "You join the ranks of the old ones, your flesh defiled by the blood of the maw.",
                "dmg": 0,
                "effect": "legend_ritual",
                "description": "Evolves Aspect of the Legend, giving Depraved Frenzy ability and permanently "
                               "increases max HP by 25%"
            }

            return [True,
                    f"Third Dominance complete! Legend Ritual can now be conducted. Check abilities for more information",
                    "Legend"]

    elif 4 < mtr_rank < 9:
        dark_druid.hunt_data['behemoth_aspect'] += 1
        if dark_druid.hunt_data['behemoth_aspect'] == 25:
            dark_druid.sp_atk["Behemoth Ritual"] = {
                "name": "Behemoth Ritual |britual|",
                "text": "The crucible of unthinkable monsters hardens those who survive.",
                "dmg": 0,
                "effect": "behemoth_ritual",
                "description": "Evolves Aspect of the Behemoth, giving Become Immense ability and permanently "
                               "increases defense power by 25%."
            }

            return [True,
                    f"Second Dominance complete! Behemoth Ritual can now be conducted. Check abilities for more information",
                    "Behemoth"]

    elif mtr_rank < 5:
        dark_druid.hunt_data['predator_aspect'] += 1
        if dark_druid.hunt_data['predator_aspect'] == 25:
            dark_druid.sp_atk["Predator Ritual"] = {
                "name": "Predator Ritual |pritual|",
                "text": "In the blood you find strength",
                "dmg": 0,
                "effect": "predator_ritual",
                "description": "Evolves Aspect of the Predator, giving Rake Claws ability and permanently "
                               "increases attack power by 25%"
            }

            return [True,
                    f"First Dominance complete! Predator Ritual can now be conducted. Check abilities for more information",
                    "Predator"]

    return [False]


def entomb(hero):
    with open(f"deceased/{hero.name}.json", "w") as f:
        json.dump(hero.__dict__, f, indent=2)


def level_up(hero):
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
        }
    }

    if hero.class_ == "Tank":
        old_hp = hero.max_hp
        old_atk = hero.atk
        old_def = hero.defense
        old_crit = hero.crit_multiplier
        old_init = hero.initiative

        hp = random.randint(10, 15)
        attack = random.randint(3, 6)
        defense = random.randint(3, 4)

        hero.max_hp += hp
        hero.atk += attack
        hero.defense += defense
        hero.initiative += 1
        hero.crit_multiplier += 0.1
        hero.crit_multiplier = round(hero.crit_multiplier, 1)
        hero.level += 1

        if hero.level % 4 == 0:
            hero.max_ep += 1
            hero.current_ep += 1

        level_skill = False
        ability_added = None

        # Add Retribution
        if hero.level == 10:
            hero.sp_atk["Retribution"] = level_abilities["Retribution"]
            hero.status.append("Retribution")
            if "Normal" in hero.status:
                hero.status.remove("Normal")
            level_skill = True
            ability_added = level_abilities["Retribution"]

        # Add Martyr
        if hero.level == 15:
            hero.sp_atk["Martyr"] = level_abilities["Martyr"]
            level_skill = True
            ability_added = level_abilities["Martyr"]

        level_list = [hero, [old_hp, hp], [old_atk, attack], [old_def, defense], [old_crit, 0.1], [level_skill, ability_added], [old_init, 1]]
        return level_list

    elif hero.class_ == "Fighter":
        old_hp = hero.max_hp
        old_atk = hero.atk
        old_def = hero.defense
        old_crit = hero.crit_multiplier
        old_init = hero.initiative

        hp = random.randint(6, 12)
        attack = random.randint(5, 10)
        defense = random.randint(2, 3)

        hero.max_hp += hp
        hero.atk += attack
        hero.defense += defense
        hero.initiative += 1
        hero.crit_multiplier += 0.1
        hero.crit_multiplier = round(hero.crit_multiplier, 1)
        hero.level += 1

        if hero.level % 4 == 0:
            hero.max_ep += 1
            hero.current_ep += 1

        level_skill = False
        ability_added = None

        # Add Executor
        if hero.level == 10:
            hero.sp_atk["Executor"] = level_abilities["Executor"]
            level_skill = True
            ability_added = level_abilities["Executor"]

        # Add Art of War
        if hero.level == 15:
            hero.sp_atk["Art Of War"] = level_abilities["Art Of War"]
            hero.status.append("Art Of War")
            if "Normal" in hero.status:
                hero.status.remove("Normal")
            level_skill = True
            ability_added = level_abilities["Art Of War"]

        level_list = [hero, [old_hp, hp], [old_atk, attack], [old_def, defense], [old_crit, 0.1], [level_skill, ability_added]]
        return level_list

    elif hero.class_ == "Assassin":
        old_hp = hero.max_hp
        old_atk = hero.atk
        old_def = hero.defense
        old_crit = hero.crit_multiplier
        old_init = hero.initiative

        hp = random.randint(4, 8)
        attack = random.randint(6, 12)
        defense = random.randint(1, 2)

        hero.max_hp += hp
        hero.atk += attack
        hero.defense += defense
        hero.initiative += 1
        hero.crit_multiplier += random.choice([0.1, 0.2])
        hero.crit_multiplier = round(hero.crit_multiplier, 1)
        hero.level += 1

        if hero.level % 4 == 0:
            hero.max_ep += 1
            hero.current_ep += 1

        if hero.level % 5 == 0:
            hero.sp_atk["Assassinate"]["dmg"] -= 1

        level_skill = False
        ability_added = None

        # Add Stalk
        if hero.level == 10:
            hero.sp_atk["Stalk"] = level_abilities["Stalk"]
            level_skill = True
            ability_added = level_abilities["Stalk"]

        # Add Mass Casualty
        if hero.level == 15:
            hero.sp_atk["Mass Casualty"] = level_abilities["Mass Casualty"]
            level_skill = True
            ability_added = level_abilities["Mass Casualty"]

        level_list = [hero, [old_hp, hp], [old_atk, attack], [old_def, defense], [old_crit, 0.2], [level_skill, ability_added]]
        return level_list

    elif hero.class_ == "Cleric":
        old_hp = hero.max_hp
        old_atk = hero.atk
        old_def = hero.defense
        old_crit = hero.crit_multiplier
        old_init = hero.initiative

        hp = random.randint(6, 12)
        attack = random.randint(3, 8)
        defense = random.randint(1, 2)

        hero.max_hp += hp
        hero.atk += attack
        hero.defense += defense
        hero.initiative += 1
        hero.crit_multiplier += 0.1
        hero.crit_multiplier = round(hero.crit_multiplier, 1)
        hero.level += 1

        if hero.level % 4 == 0:
            hero.max_ep += 1
            hero.current_ep += 1

        level_skill = False
        ability_added = None

        # Add Obsecrate
        if hero.level == 10:
            hero.sp_atk["Obsecrate"] = level_abilities["Obsecrate"]
            level_skill = True
            ability_added = level_abilities["Obsecrate"]

        # Add Divinity
        if hero.level == 15:
            hero.sp_atk["Divinity"] = level_abilities["Divinity"]
            level_skill = True
            ability_added = level_abilities["Divinity"]

        level_list = [hero, [old_hp, hp], [old_atk, attack], [old_def, defense], [old_crit, 0.2], [level_skill, ability_added]]
        return level_list

    elif hero.class_ == "Artificer":
        old_hp = hero.max_hp
        old_atk = hero.atk
        old_def = hero.defense
        old_crit = hero.crit_multiplier
        old_init = hero.initiative

        hp = random.randint(12, 15)
        attack = random.randint(4, 6)
        defense = random.randint(2, 3)

        hero.max_hp += hp
        hero.atk += attack
        hero.defense += defense
        hero.initiative += 1
        hero.crit_multiplier += random.choice([0.1, 0.2])
        hero.crit_multiplier = round(hero.crit_multiplier, 1)
        hero.level += 1

        if hero.level % 4 == 0:
            hero.max_ep += 1
            hero.current_ep += 1

        level_skill = False
        ability_added = None

        # Add Tinker
        if hero.level == 10:
            hero.sp_atk["Tinker"] = level_abilities["Tinker"]
            level_skill = True
            ability_added = level_abilities["Tinker"]

        # Add Detonate
        if hero.level == 15:
            hero.sp_atk["Detonate"] = level_abilities["Detonate"]
            level_skill = True
            ability_added = level_abilities["Detonate"]

        level_list = [hero, [old_hp, hp], [old_atk, attack], [old_def, defense], [old_crit, 0.1], [level_skill, ability_added]]
        return level_list

    if hero.class_ == "Mage":
        old_hp = hero.max_hp
        old_atk = hero.atk
        old_def = hero.defense
        old_crit = hero.crit_multiplier
        old_init = hero.initiative

        hp = random.randint(5, 10)
        attack = random.randint(2, 3)
        defense = random.randint(1, 2)

        hero.max_hp += hp
        hero.atk += attack
        hero.defense += defense
        hero.initiative += 1
        hero.crit_multiplier += 0.1
        hero.crit_multiplier = round(hero.crit_multiplier, 1)
        hero.level += 1

        if hero.level % 2 == 0:
            hero.max_ep += 1
            hero.current_ep += 1

        for ability in hero.sp_atk:
            if ability == "Recharge":
                pass
            elif ability == "Battlemage":
                hero.sp_atk[ability]["dmg"] += 1
            else:
                hero.sp_atk[ability]["dmg"] = math.ceil(hero.sp_atk[ability]["dmg"] * 1.12)

        level_skill = False
        ability_added = None

        # Add Fireball
        if hero.level == 5:
            hero.sp_atk["Fireball"] = level_abilities["Fireball"]
            level_skill = True
            ability_added = level_abilities["Fireball"]

        # Add Battlemage
        if hero.level == 10:
            hero.sp_atk["Battlemage"] = level_abilities["Battlemage"]
            level_skill = True
            ability_added = level_abilities["Battlemage"]

        level_list = [hero, [old_hp, hp], [old_atk, attack], [old_def, defense], [old_crit, 0.1], [level_skill, ability_added]]
        return level_list

    elif hero.class_ == "Dark Druid":
        old_hp = hero.max_hp
        old_atk = hero.atk
        old_def = hero.defense
        old_crit = hero.crit_multiplier
        old_init = hero.initiative

        hp = random.randint(8, 12)
        attack = random.randint(7, 10)
        defense = random.randint(2, 3)

        hero.max_hp += hp
        hero.atk += attack
        hero.defense += defense
        hero.initiative += 1
        hero.crit_multiplier += 0.1
        hero.crit_multiplier = round(hero.crit_multiplier, 1)
        hero.level += 1

        if hero.level % 4 == 0:
            hero.max_ep += 1
            hero.current_ep += 1

        level_skill = False
        ability_added = None

        level_list = [hero, [old_hp, hp], [old_atk, attack], [old_def, defense], [old_crit, 0.1], [level_skill, ability_added]]
        return level_list

    elif hero.class_ == "Monk":
        old_hp = hero.max_hp
        old_atk = hero.atk
        old_def = hero.defense
        old_crit = hero.crit_multiplier
        old_init = hero.initiative

        hp = 0
        attack = 0
        defense = 0

        hero.initiative += 1
        hero.crit_multiplier = round(hero.crit_multiplier + 0.1, 1)
        hero.level += 1

        if hero.level % 5 == 0:
            hero.max_ep += 1
            hero.current_ep += 1
            hero.sp_atk["Disarming Blows"]["dmg"] -= 2

        more_score = random.randint(15, 20)
        hero.meditate_score += more_score

        if hero.level > 10:
            hero.sp_atk["Ki Bomb"]["dmg"] += 40

        level_skill = False
        ability_added = None

        # Add Meditate
        if hero.level == 2:
            hero.sp_atk["Meditate"] = level_abilities["Meditate"]
            level_skill = True
            ability_added = level_abilities["Meditate"]

        # Add Ki Bomb
        if hero.level == 10:
            hero.sp_atk["Ki Bomb"] = level_abilities["Ki Bomb"]
            level_skill = True
            ability_added = level_abilities["Ki Bomb"]

        # Add Dragon Kick
        if hero.level == 15:
            hero.sp_atk["Dragon Kick"] = level_abilities["Dragon Kick"]
            level_skill = True
            ability_added = level_abilities["Dragon Kick"]

        # Add Pilgrimage
        if hero.level in [8, 16, 20, 30]:
            hero.sp_atk["Monastic Pilgrimage"] = level_abilities["Monastic Pilgrimage"]
            level_skill = True
            ability_added = level_abilities["Monastic Pilgrimage"]

        level_list = [hero, [old_hp, hp], [old_atk, attack], [old_def, defense], [old_crit, 0.1], [level_skill, ability_added]]
        return level_list

    else:
        raise KeyError("Character 'class' is not found, [level_up, staticfunctions]")


def load_hero(hero_name: str):
    """
    Loads hero dictionary from json file

    :hero_name: Hero name string
    """

    with open(f"characters/{hero_name}.json", "w") as file:
        data = json.load(file)

    hero = HeroBuilder()

    hero.__dict__ = data

    return hero


def monster_present(target, monster_directory):
    master = [monster.name for monster in monster_directory if monster.name != "Chest"]
    if target in master:
        return True
    return False


def open_hero_records(discord_id):
    with open(f"users/{discord_id}.json", "r") as file:
        data = json.load(file)
    return data


def save_hero(hero_object):
    """
    Unnecessary to run: In-class method split for organization.
    Saves character information to .txt file in json format

    :hero_object: Class HeroBuilder object
    """

    with open(f"characters/{hero_object.name}.json", "w") as file:
        json.dump(hero_object.__dict__, file, indent=2)


def select_random_monster(number, monster_list, target_name=None):
    master = [monster for monster in monster_list if monster.name not in ["Chest", target_name]]

    random_monsters = []
    temp_holding = []
    for _ in range(number):
        if not master:
            break
        else:
            temp = random.choice(master)
            temp_holding.append(temp)
            master.remove(temp)
            random_monsters.append(temp)
    
    for temp_mon in temp_holding:
        master.append(temp_mon)
        
    if not random_monsters:
        return ["None"]
    return random_monsters


def set_hero_user(discord_id):
    with open(f"users/{discord_id}.json", "r") as file:
        data = json.load(file)
    return data["user_hero"]


def shortcut_return(short_argument):
    with open("shortcuts/item_shortcuts.json", "r") as file:
        itemcuts_dict = json.load(file)
        itemcuts = list(itemcuts_dict.keys())
    with open("shortcuts/monster_shortcuts.json", "r") as file:
        moncuts_dict = json.load(file)
        moncuts = list(moncuts_dict.keys())
    with open("shortcuts/ability_shortcuts.json", "r") as file:
        abilicuts_dict = json.load(file)
        abilicuts = list(abilicuts_dict.keys())
    with open("shortcuts/permanent_shortcuts.json", "r") as file:
        permacuts_dict = json.load(file)
        permacuts = list(permacuts_dict.keys())

    shorts_dict = {
        "Item": itemcuts_dict,
        "Monster": moncuts_dict,
        "Ability": abilicuts_dict,
        "Permanent": permacuts_dict
    }

    shortcuts_list = [itemcuts, moncuts, abilicuts, permacuts]
    for shortcut in shortcuts_list:
        if short_argument in shortcut:
            return shorts_dict[shortcut[0]][short_argument]
    return short_argument


# Editing Functions __________________________________________________


def block_text(string):
    return str(f"""```asciidoc\n{string}```""")


def code_block(string):
    return str(f"```{string}```")
