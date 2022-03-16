import random
from equipment import Legendary, Armors


class Items:
    def __init__(self):

        self.tier1_random_item_chance = 4  # 25% CHANCE
        self.tier2_random_item_chance = 4  # 25% CHANCE
        self.tier3_random_item_chance = 4  # 25% CHANCE
        self.key_drop_chance = 4  # 25% CHANCE

        self.tier1_items = [
            "Monster Scanner",
            "Fireball Scroll",
            "Healing Potion",
            "Whetstone",
            "Smelling Salts"
        ]

        self.tier2_items = [
            "Blood Of Berserker",
            "Witchbolt Wand",
            "Blood Dagger",
            "Tome Of Wisdom",
            "Decay Bomb"
        ]

        self.tier3_items = [
            "Scroll Of Summoning",
            "Gravity Bomb",
            "Mesmer Stone",
            "Gift Of Arawn",
            "Sundering Axe"
        ]

        self.tier4_items = [
            "Eldritch Keybox",
            "Bardic Tale"
        ]

        self.keys = [
            "Blood-Soaked Key",
            "Mountain Key",
            "Dimensional Key",
            "Tortoise Key"
        ]

        self.improved = [
            "Improved Monster Scanner",
            "Improved Fireball Scroll",
            "Improved Healing Potion",
            "Improved Whetstone",
            "Improved Blood Of Berserker",
            "Improved Witchbolt Wand",
            "Improved Blood Dagger",
            "Improved Tome Of Wisdom",
            "Improved Decay Bomb",
            "Improved Scroll Of Summoning",
            "Improved Gravity Bomb",
            "Improved Mesmer Stone",
            "Improved Gift Of Arawn",
            "Improved Sundering Axe",
            "Improved Eldritch Keybox",
            "Improved Bardic Tale"

        ]

        self.master = [
            "Monster Scanner",
            "Fireball Scroll",
            "Healing Potion",
            "Whetstone",
            "Smelling Salts",
            "Blood Of Berserker",
            "Witchbolt Wand",
            "Blood Dagger",
            "Tome Of Wisdom",
            "Decay Bomb",
            "Scroll Of Summoning",
            "Gravity Bomb",
            "Mesmer Stone",
            "Gift Of Arawn",
            "Sundering Axe",
            "Eldritch Keybox",
            "Bardic Tale",
            "Improved Monster Scanner",
            "Improved Fireball Scroll",
            "Improved Healing Potion",
            "Improved Whetstone",
            "Improved Blood Of Berserker",
            "Improved Witchbolt Wand",
            "Improved Blood Dagger",
            "Improved Tome Of Wisdom",
            "Improved Decay Bomb",
            "Improved Scroll Of Summoning",
            "Improved Gravity Bomb",
            "Improved Mesmer Stone",
            "Improved Gift Of Arawn",
            "Improved Sundering Axe",
            "Improved Eldritch Keybox"
        ]

    def random_item(self, mon_rank):
        """
        Creates a random item from the inventory tracker class
        _____
        return: item object
        """
        if mon_rank == "Legendary":
            key_chance = random.randint(1, self.key_drop_chance)

            if key_chance == 1:
                rand_item = random.choice(self.keys)
            else:
                rand_item = None

        elif mon_rank < 4:
            tier1_chance = random.randint(1, self.tier1_random_item_chance)

            if tier1_chance == 1:
                rand_item = random.choice(self.tier1_items)
            else:
                rand_item = None

        elif 4 <= mon_rank <= 7:
            tier2_chance = random.randint(1, self.tier2_random_item_chance)

            if tier2_chance == 1:
                rand_item = random.choice(self.tier2_items)
            else:
                rand_item = None

        elif mon_rank > 7:
            tier3_chance = random.randint(1, self.tier3_random_item_chance)

            if tier3_chance == 1:
                rand_item = random.choice(self.tier3_items)
            else:
                rand_item = None

        else:
            raise AttributeError(f"Monster rank not found: {mon_rank}")

        return rand_item

    def modulate_chances(self, tier):
        if tier == "Legendary":
            self.key_drop_chance -= 2
        elif tier == 1:
            self.tier1_random_item_chance -= 2
        elif tier == 2:
            self.tier2_random_item_chance -= 2
        elif tier == 3:
            self.tier2_random_item_chance -= 2

    def absolute_chance(self):
        self.key_drop_chance = 1
        self.tier1_random_item_chance = 1
        self.tier2_random_item_chance = 1
        self.tier3_random_item_chance = 1

    def return_item(self, item):
        arms = Armors()
        legends = Legendary()

        if item in self.tier1_items or item in self.tier2_items or item in self.tier3_items or item in self.tier4_items or item in self.improved:
            return "inventory"
        elif item in self.keys:
            return "keys"
        elif item in arms.armors or item in legends.legends:
            return "armory"
        else:
            return None

