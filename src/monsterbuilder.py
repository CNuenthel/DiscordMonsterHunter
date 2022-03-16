from items import Items
from equipment import Legendary
import random
import json
import math

RANK1_MAX_DMG = 20
RANK2_MAX_DMG = 50
RANK3_MAX_DMG = 80
RANK4_MAX_DMG = 110
RANK5_MAX_DMG = 140
RANK6_MAX_DMG = 170
RANK7_MAX_DMG = 200
RANK8_MAX_DMG = 230
LEGENDARY_MAX_DAMAGE = 260
APEX_MAX_DAMAGE = 300

with open("tier monsters/rank1.json", "r") as file:
    tier1_list = json.load(file)
with open("tier monsters/rank2.json", "r") as file:
    tier2_list = json.load(file)
with open("tier monsters/rank3.json", "r") as file:
    tier3_list = json.load(file)
with open("tier monsters/rank4.json", "r") as file:
    tier4_list = json.load(file)
with open("tier monsters/rank5.json", "r") as file:
    tier5_list = json.load(file)
with open("tier monsters/rank6.json", "r") as file:
    tier6_list = json.load(file)
with open("tier monsters/rank7.json", "r") as file:
    tier7_list = json.load(file)
with open("tier monsters/rank8.json", "r") as file:
    tier8_list = json.load(file)
with open("tier monsters/legendary.json", "r") as file:
    legendary_list = json.load(file)
with open("tier monsters/apex.json", "r") as file:
    key_list = json.load(file)

class MonsterBuilder(Items):
    """
    Generates a monster and saves monster information in json format within directory /monsters
    """

    def __init__(self, rank: int or str):
        """
        Creates a monster randomly selected based on rank (1 to 3, hardest to easiest), randomly rolls HP/Atk/Def
        based on rank windows and saves monster to a text file.

        :param rank: 1, 2, 3 or Legendary
        """

        super().__init__()
        self.legends = Legendary()
        print("Getting Monster...")
        if rank == 1:
            monster = random.choice(tier1_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(25, 50)
            self.atk = random.randint(RANK1_MAX_DMG//2, RANK1_MAX_DMG)
            self.defense = random.randint(1, 3)
            self.initiative = 7
            self.item = self.random_item(rank)
            self.xp = random.randint(50, 75)
            print(f"{monster[0]} Created")

        elif rank == 2:
            monster = random.choice(tier2_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(45, 75)
            self.defense = random.randint(2, 4)
            self.initiative = 8
            self.item = self.random_item(rank)
            self.atk = random.randint(RANK2_MAX_DMG//2, RANK2_MAX_DMG)
            self.xp = random.randint(100, 150)
            print(f"{monster[0]} Created")

        elif rank == 3:
            monster = random.choice(tier3_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(70, 125)
            self.atk = random.randint(RANK3_MAX_DMG//2, RANK3_MAX_DMG)
            self.defense = random.randint(3, 6)
            self.initiative = 9
            self.item = self.random_item(rank)
            self.xp = random.randint(150, 200)
            print(f"{monster[0]} Created")

        elif rank == 4:
            monster = random.choice(tier4_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(120, 175)
            self.atk = random.randint(RANK4_MAX_DMG//2, RANK4_MAX_DMG)
            self.defense = random.randint(6, 9)
            self.initiative = 10
            self.item = self.random_item(rank)
            self.xp = random.randint(200, 250)
            print(f"{monster[0]} Created")

        elif rank == 5:
            monster = random.choice(tier5_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(170, 225)
            self.atk = random.randint(RANK5_MAX_DMG//2, RANK5_MAX_DMG)
            self.defense = random.randint(9, 12)
            self.initiative = 11
            self.item = self.random_item(rank)
            self.xp = random.randint(250, 300)
            print(f"{monster[0]} Created")

        elif rank == 6:
            monster = random.choice(tier6_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(220, 275)
            self.atk = random.randint(RANK6_MAX_DMG//2, RANK6_MAX_DMG)
            self.defense = random.randint(12, 15)
            self.initiative = 12
            self.item = self.random_item(rank)
            self.xp = random.randint(300, 350)
            print(f"{monster[0]} Created")

        elif rank == 7:
            monster = random.choice(tier7_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(270, 325)
            self.atk = random.randint(RANK7_MAX_DMG//2, RANK7_MAX_DMG)
            self.defense = random.randint(15, 18)
            self.initiative = 13
            self.item = self.random_item(rank)
            self.xp = random.randint(350, 400)
            print(f"{monster[0]} Created")

        elif rank == 8:
            monster = random.choice(tier8_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(320, 375)
            self.atk = random.randint(RANK8_MAX_DMG//2, RANK8_MAX_DMG)
            self.defense = random.randint(18, 21)
            self.initiative = 14
            self.item = self.random_item(rank)
            self.xp = random.randint(400, 450)
            print(f"{monster[0]} Created")

        elif rank == "Legendary":
            monster = random.choice(legendary_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(500, 600)
            self.atk = random.randint(LEGENDARY_MAX_DAMAGE//2, LEGENDARY_MAX_DAMAGE)
            self.defense = random.randint(21, 30)
            self.initiative = 15
            self.item = self.random_item(rank)
            self.xp = random.randint(600, 750)
            print(f"{monster[0]} Created")

        elif rank == "Apex":
            monster = random.choice(key_list)
            self.name = monster[0]
            self.sp_atk = monster[1]
            self.link = monster[2]
            self.max_hp = random.randint(12000, 16000)
            self.atk = random.randint(APEX_MAX_DAMAGE//2, APEX_MAX_DAMAGE)
            self.defense = random.randint(30, 45)
            self.initiative = 20
            self.item = random.choice(self.legends.legends)
            self.xp = random.randint(10000, 15000)
            print(f"{monster[0]} Created")

        self.current_hp = self.max_hp
        self.rank = rank
        self.status = ["Normal"]
        self.attacked_by = []
        self.empowered = 0
        self.aura = None
        self.position_locked = False
    
    def empower(self):
        self.atk = math.ceil(self.atk * 1.3)
        self.defense = math.ceil(self.defense * 1.3)
        self.max_hp = math.ceil(self.max_hp * 1.3)
        self.current_hp = self.max_hp
        self.xp = math.ceil(self.xp * 1.5)
        self.empowered += 1

    def enraged_monster(self):
        self.max_hp = math.ceil(self.max_hp * 1.5)
        self.current_hp = self.max_hp
        self.name = "Enraged " + self.name
        self.atk = math.ceil(self.atk * 1.5)
        self.defense = math.ceil(self.defense * 1.5)
        self.xp *= 5

        # If Legendary Summoned, bypasses rank count disagreement
        try:
            self.rank += 1
        except TypeError:
            pass

    def raid_monster(self, difficulty):
        difficulty_modifier = 1 + (difficulty * 0.1)
        self.max_hp = round(self.max_hp * difficulty_modifier)
        self.current_hp = self.max_hp
        self.atk = round(self.atk * difficulty_modifier)
        self.defense = round(self.defense * difficulty_modifier)
        self.xp = round(self.xp * (4 * difficulty_modifier))

class Chest(Items):

    def __init__(self):
        super().__init__()
        self.rarity = random.choice(["Exotic", "Rare", "Uncommon", "Common"])
        self.name = "Chest"
        self.rank = "Chest"

        if self.rarity == "Exotic":
            self.contents = random.choice(self.tier3_items)
        elif self.rarity == "Rare":
            self.contents = random.choice(self.tier2_items)
        elif self.rarity == "Uncommon":
            self.contents = random.choice(self.tier1_items)
        else:
            self.contents = random.randint(50, 100)

class Raid:
    def __init__(self, hero_name):
        self.raider = hero_name
        self.difficulty = 0
        self.monsters = []
        self.gold_bank = 0
        self.xp_bank = 0
        self.item_bank = []
        self.key_bank = "No Key"
        self.items_used = []
        self.raider_equipment = "None"
        self.raider_armor = "None"

    def set_difficulty(self, raid_difficulty):
        self.difficulty = raid_difficulty

    def set_equipment(self, hero):
        self.raider_equipment = hero.equipment
        self.raider_armor = hero.armor

    def add_monster(self, monster):
        self.monsters.append(monster)

    def reward_raid(self, hero):
        hero.xp += self.xp_bank
        hero.gold += self.gold_bank
        if self.key_bank != "No Key":
            hero.keys.append(self.key_bank)
        if self.item_bank:
            hero.inventory.extend(self.item_bank)
        hero.raiding = False
        hero.last_raid_completed = self.difficulty


