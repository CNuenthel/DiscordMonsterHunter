import random
import json


class HeroBuilder:
    """
    Generates a hero and saves hero information in json format within directory /characters
    """

    def __init__(self):
        """
        Creates a character with a given name of a desired class, randomizes HP/Atk/Def based on class type and saves
        character to a text file.

         :param name: The name of your character
         :param class_: 'tank', 'fighter',or 'assassin'
        """

        self.class_ = ""
        self.max_hp = 0
        self.current_hp = self.max_hp
        self.bonus_hp = 0
        self.atk = 0
        self.bonus_atk = 0
        self.defense = 0
        self.bonus_def = 0
        self.initiative = 0
        self.status = []
        self.max_ep = 2
        self.current_ep = 2
        self.bonus_ep = 0
        self.crit_multiplier = 1.5
        self.bonus_crit = 0
        self.sp_atk = {}
        self.link = ""
        self.hunt_data = {}
        self.owner = ""
        self.name = ""
        self.level = 1
        self.resting = "Not Resting"
        self.xp = 0
        self.inventory = []
        self.armory = []
        self.keys = []
        self.equipment = "None"
        self.armor = "None"
        self.gold = 0
        self.ascended = False
        self.ascended_xp = 0
        self.ascended_classes = []
        self.last_raid_completed = None
        self.raiding = False
        self.shop_lock = False
        self.immense_hp = 0
        self.raid_cooldown = "Dec 1 2000 at 10:29AM"
        self.alarm_clock = ""
        self.last_raid_complete = 1

    def new_class_set(self, class_, name, owner):
        class_ = class_.lower()
        name = name.title()

        if class_ == "tank":
            self.class_ = "Tank"
            self.max_hp = random.randint(80, 100)
            self.current_hp = self.max_hp
            self.atk = random.randint(10, 16)
            self.defense = random.randint(10, 16)
            self.initiative = 5
            self.status = ["Normal"]
            self.sp_atk = {
                "Shieldbash": {
                    "name": "Shieldbash |sb|",
                    "text": f"{name} strikes the foe with a thunderous shield bash!",
                    "dmg": 15,
                    "effect": "dazed",
                    "description": "Dazes a monster, causing them to miss their next attack."
                    }
                }
            self.link = "https://i.ibb.co/yRPmqJ6/0000.jpg"

        elif class_ == "fighter":
            self.class_ = "Fighter"
            self.max_hp = random.randint(65, 85)
            self.current_hp = self.max_hp
            self.atk = random.randint(16, 20)
            self.defense = random.randint(6, 8)
            self.initiative = 6
            self.status = ["Normal"]
            self.sp_atk = {
                "Helmbreaker": {
                    "name": "Helmbreaker |hb|",
                    "text": f"{name} raises their sword to the air and cleaves the earth with a forceful slash!",
                    "dmg": 15,
                    "effect": "sunder",
                    "description": "Reduces target armor by half"
                    }
                }
            self.link = "https://i.ibb.co/yRPmqJ6/0000.jpg"

        elif class_ == "assassin":
            self.class_ = "Assassin"
            self.max_hp = random.randint(50, 70)
            self.current_hp = self.max_hp
            self.atk = random.randint(22, 28)
            self.defense = random.randint(4, 7)
            self.initiative = 7
            self.status = ["Normal"]
            self.sp_atk = {
                "Assassinate": {
                    "name": "Assassinate |ass|",
                    "text": f"{name} slips into the shadows and explodes above the monster with a lunging strike!",
                    "dmg": 7,
                    "effect": "guillotine",
                    "description": "Chance to instantly kill target monster, scaling success rate with leveling."
                        }
                }
            self.link = "https://i.ibb.co/yRPmqJ6/0000.jpg"

        elif class_ == "cleric":
            self.class_ = "Cleric"
            self.max_hp = random.randint(65, 85)
            self.current_hp = self.max_hp
            self.atk = random.randint(12, 18)
            self.defense = random.randint(8, 12)
            self.initiative = 8
            self.status = ["Normal"]
            self.sp_atk = {
                "Regenerate": {
                    "name": "Regenerate |reg|",
                    "text": f"{name} casts a healing aura!",
                    "dmg": 15,
                    "effect": "regenerate",
                    "description": "Heals a target hero for 75% of their max HP"
                        }
                }
            self.link = "https://i.ibb.co/yRPmqJ6/0000.jpg"

        elif class_ == "artificer":
            self.class_ = "Artificer"
            self.max_hp = random.randint(80, 105)
            self.current_hp = self.max_hp
            self.atk = random.randint(12, 18)
            self.defense = random.randint(6, 10)
            self.initiative = 7
            self.status = ["Normal"]
            self.sp_atk = {
                "Intuition": {
                    "name": "Intuition |int|",
                    "text": f"{name} checks for hidden items.",
                    "dmg": 0,
                    "effect": "alchemy",
                    "description": "Chance for monster without an item to hold one, or for held item to increase one tier."
                    }
                }
            self.link = "https://i.ibb.co/yRPmqJ6/0000.jpg"

        elif class_ == "monk":
            self.class_ = "Monk"
            self.max_hp = 90
            self.current_hp = self.max_hp
            self.atk = random.randint(16, 24)
            self.defense = random.randint(8, 14)
            self.initiative = 7
            self.meditate_score = 0
            self.base_score = (self.atk - 1) + (self.defense - 1)
            self.status = ["Disarming"]
            self.sp_atk = {
                "Disarming Blows": {
                    "name": "Disarming Blows",
                    "text": f"",
                    "dmg": 16,
                    "effect": "disarming blows",
                    "description": "Passive Buff: Each strike on a single target reduces monster attack and defense, no "
                                   "effect on Apex monsters."
                    }
                }
            self.link = "https://i.ibb.co/yRPmqJ6/0000.jpg"

        elif class_ == "mage":
            self.class_ = "Mage"
            self.max_hp = random.randint(40, 60)
            self.current_hp = self.max_hp
            self.atk = random.randint(10, 16)
            self.defense = random.randint(4, 8)
            self.initiative = 9
            self.status = ["Normal"]
            self.max_ep = 4
            self.current_ep = 4
            self.sp_atk = {
                "Recharge": {
                    "name": "Recharge |rec|",
                    "text": f"With power, comes sacrifice",
                    "dmg": 0,
                    "effect": "recharge",
                    "description": "Sacrifices HP for EP"
                },
                "Magic Missile": {
                    "name": "Magic Missile |mm|",
                    "text": f"{name} creates three glowing darts that seek out monsters.",
                    "dmg": 15,
                    "effect": "missile",
                    "description": "Deals moderate damage, chance of critical damage."
                    }
                }
            self.link = "https://i.ibb.co/yRPmqJ6/0000.jpg"

        elif class_ == "dark druid":
            self.class_ = "Dark Druid"
            self.max_hp = random.randint(65, 85)
            self.current_hp = self.max_hp
            self.atk = random.randint(18, 22)
            self.defense = random.randint(8, 12)
            self.initiative = 6
            self.status = ["Normal"]
            self.max_ep = 2
            self.current_ep = 2
            self.sp_atk = {
                "Maw Oath": {
                    "name": "Maw Oath |mo|",
                    "text": f"text",
                    "dmg": 1,
                    "effect": "maw_oath",
                    "description": f"Recover 25% health and add 25% base defense boost"
                    },
                "Cognition": {
                    "name": "Cognition |cog|",
                    "text": f"text",
                    "dmg": 1,
                    "effect": "cognition",
                    "description": f"Provides information on evolution bonuses"
                    }
                }
            self.link = "https://i.ibb.co/yRPmqJ6/0000.jpg"
            self.hunt_data = {
                "predator_aspect": 0,
                "behemoth_aspect": 0,
                "legend_aspect": 0,
                "apex_aspect": 0
            }
        else:
            raise ValueError(f"The class you selected does not exist. Class selected: {class_}")

        self.owner = owner
        self.name = name
        self.level = 1
        self.crit_multiplier = 1.5
        self.resting = "Not Resting"
        self.xp = 0
        self.inventory = []
        self.armory = []
        self.keys = []
        self.equipment = "None"
        self.gold = 0
        self.ascended = False
        self.ascended_xp = 0
        self.ascended_classes = []
        self.ascensions = 0
        self.last_raid_completed = None
        self.raiding = False
        self.armor = "None"
        print(f"{self.name} has been summoned by {self.owner}")

