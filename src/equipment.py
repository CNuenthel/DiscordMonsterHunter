import math

class Legendary:

    def __init__(self):
        self.legends = ["Rod Of Lordly Might", "Natures Mantle", "Vestige Blade", "Chidori",
                        "Yamatos Training Katana", "Forbidden Fruit"]
        self.status_mod = False
        self.status = None
        self.atk_mod = 0
        self.def_mod = 0
        self.hp_mod = 0
        self.ep_mod = 0
        self.crit_mod = 0
        self.special_ability_mod = False
        self.equipment_ability_name = None
        self.special_ability = None
        self.mode_set = False
        self.mode = None

    def rod_of_lordly_might(self, mode_set):
        self.mode_set = True

        if mode_set == "battleaxe":
            self.atk_mod = 100
            self.crit_mod = 1
            self.def_mod = 7
            self.mode = "battleaxe"

        elif mode_set == "spear":
            self.atk_mod = 50
            self.crit_mod = 2
            self.special_ability_mod = True
            self.equipment_ability_name = "Spearsling"

            self.special_ability = {
                "name": "Spearsling |ss|",
                "text": "As you launch your Rod of Lordly Might it seamlessly transforms into a razor sharp spear, "
                        "propelling itself across the field, embedding deep into the monster's chest!",
                "dmg": 50,
                "effect": "spearsling",
                "description": "Reduces monster HP and inflicts Bleeding status for 3 turns"
            }

            self.mode = "spear"

        elif mode_set == "barrier":
            self.atk_mod = 25
            self.crit_mod = 2
            self.def_mod = 65
            self.hp_mod = 300
            self.ep_mod = 1
            self.mode = "barrier"

    def natures_mantle(self):
        self.status_mod = True
        self.status = "Ambiguity"
        self.atk_mod = 40
        self.crit_mod = 1
        self.def_mod = 15
        self.hp_mod = 200
        self.ep_mod = 2

    def vestige_blade(self):
        self.status_mod = True
        self.status = "Spirit Trace"
        self.atk_mod = 60
        self.crit_mod = 1
        self.def_mod = 10
        self.hp_mod = 50
        self.ep_mod = 1

    def chidori(self, hero):
        self.status_mod = True
        self.status = "Flash"

        try:
            self.atk_mod = hero.chidori_atk_mod
            self.def_mod = hero.chidori_def_mod
            self.hp_mod = hero.chidori_hp_mod
            delattr(hero, "chidori_atk_mod")
            delattr(hero, "chidori_def_mod")
            delattr(hero, "chidori_hp_mod")

        except AttributeError:
            self.atk_mod = math.ceil((hero.atk + hero.bonus_atk) * 0.6)
            self.def_mod = math.ceil((hero.defense + hero.bonus_def) * -0.5)
            self.hp_mod = math.ceil(((hero.max_hp + hero.bonus_hp) + hero.bonus_hp) * -0.5)
            hero.chidori_atk_mod = self.atk_mod
            hero.chidori_def_mod = self.def_mod
            hero.chidori_hp_mod = self.hp_mod

    def forbidden_fruit(self, hero):
        try:
            self.hp_mod = hero.fruit_hp_mod
            self.def_mod = hero.fruit_def_mod
            delattr(hero, "fruit_hp_mod")
            delattr(hero, "fruit_def_mod")
            print("from try")
        except AttributeError:
            self.hp_mod = math.ceil((hero.max_hp + hero.bonus_hp) * 0.75)
            self.def_mod = math.ceil((hero.defense + hero.bonus_def) * 0.25)
            hero.fruit_hp_mod = self.hp_mod
            hero.fruit_def_mod = self.def_mod

        self.status_mod = True
        self.status = "Vital Tree"

    def yamatos_training_katana(self):
        self.atk_mod = 50
        self.crit_mod = 2
        self.special_ability_mod = True
        self.equipment_ability_name = "Focus"

        self.special_ability = {
            "name": "Focus |foc| 2EP",
            "text": "This discarded katana flows with a millenia of experience and untold martial skill.",
            "dmg": 50,
            "effect": "focus",
            "description": "Grants Enraged and Sharpened status."
        }

    def equip(self, hero):
        if self.status_mod:
            hero.status.append(self.status)
        if self.special_ability_mod:
            hero.sp_atk[self.equipment_ability_name] = self.special_ability
        if self.mode_set:
            hero.equipment_mode = self.mode

        hero.bonus_atk += self.atk_mod
        hero.bonus_def += self.def_mod
        hero.bonus_hp += self.hp_mod
        hero.current_hp += self.hp_mod

        if hero.current_hp > hero.max_hp + hero.bonus_hp:
            hero.current_hp = hero.max_hp + hero.bonus_hp

        hero.bonus_ep += self.ep_mod
        hero.current_ep += self.ep_mod
        hero.bonus_crit += self.crit_mod

    def unequip(self, hero):
        if self.status_mod:
            hero.status.remove(self.status)
        if self.special_ability_mod:
            del hero.sp_atk[self.equipment_ability_name]
        if self.mode_set:
            delattr(hero, "equipment_mode")

        hero.bonus_atk -= self.atk_mod
        hero.bonus_def -= self.def_mod
        hero.bonus_hp -= self.hp_mod
        hero.current_hp -= self.hp_mod

        if hero.current_hp < 1:
            hero.current_hp = 1
        elif hero.current_hp > hero.max_hp + hero.bonus_hp:
            hero.current_hp = hero.max_hp + hero.bonus_hp

        hero.bonus_ep -= self.ep_mod
        hero.current_ep -= self.ep_mod

        if hero.current_ep < 0:
            hero.current_ep = 0
        elif hero.current_ep > hero.max_ep + hero.bonus_ep:
            hero.current_ep = hero.max_ep + hero.bonus_ep

        hero.bonus_crit -= self.crit_mod


class Armors:

    def __init__(self):
        self.armors = ["Cloth Armor", "Leather Armor", "Mail Armor", "Plate Armor", "Bag Of Holding"]
        self.atk_mod = 0
        self.def_mod = 0
        self.crit_mod = 0
        self.ep_mod = 0
        self.status_mod = False
        self.status = None

    def cloth_armor(self):
        self.ep_mod = 2

    def leather_armor(self):
        self.ep_mod = 1
        self.def_mod = 0.1

    def mail_armor(self):
        self.def_mod = 0.2

    def plate_armor(self):
        self.def_mod = 0.3
        self.atk_mod = -0.1
        self.crit_mod = -0.3

    def bag_of_holding(self):
        self.status_mod = True
        self.status = "Organized"

    def equip(self, hero):
        hero.armor_defense_bonus = math.ceil((hero.defense + hero.bonus_def) * self.def_mod)
        hero.armor_attack_detriment = math.ceil((hero.atk + hero.bonus_atk) * self.atk_mod)
        hero.armor_crit_detriment = round((hero.crit_multiplier + hero.bonus_crit) * self.crit_mod, 1)
        hero.armor_bonus_ep = self.ep_mod

        hero.bonus_def += hero.armor_defense_bonus
        hero.bonus_atk += hero.armor_attack_detriment
        hero.bonus_crit += hero.armor_crit_detriment
        hero.bonus_ep += self.ep_mod

        if self.status_mod:
            hero.status.append(self.status)

    def unequip(self, hero):
        hero.bonus_def -= hero.armor_defense_bonus
        hero.bonus_atk -= hero.armor_attack_detriment
        hero.bonus_crit -= hero.armor_crit_detriment
        hero.bonus_ep -= self.ep_mod

        delattr(hero, "armor_defense_bonus")
        delattr(hero, "armor_attack_detriment")
        delattr(hero, "armor_crit_detriment")

        if self.status_mod:
            hero.status.remove(self.status)

