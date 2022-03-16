import math
import random

class Fight:
    def __init__(self, hero, monster):
        self.first_attacker = None
        self.hero = hero
        self.monster = monster

        self.hero_attack = hero.atk + hero.bonus_atk
        self.hero_damage = 0
        self.hero_damage_mitigated = False
        self.hero_status_damage = 0
        self.hero_defense = hero.defense + hero.bonus_def
        self.retribution_damage = 0

        self.monster_attack = monster.atk
        self.monster_damage = 0
        self.monster_damage_mitigated = False
        self.monster_status_damage = 0
        self.monster_defense = monster.defense
        self.monster_bleed_damage = 0

        self.overkill = 0
        self.monster_crit = False
        self.hero_crit = False
        self.monster_status_in_play = []
        self.hero_status_in_play = []

    def status_handler(self, hero, monster):
        if "Enraged" in hero.status:
            self.hero_status_in_play.append(["Enraged", "Base Attack x2"])
            hero.status.remove("Enraged")
            self.hero_attack *= 2

        if "Dazed" in monster.status:
            self.monster_status_in_play.append(["Dazed", "Auto Crit/Mitigate"])
            self.monster_damage_mitigated = True
            monster.status.remove("Dazed")
            self.hero_crit = True
        elif "Marked" in monster.status and hero.class_ == "Assassin":
            self.monster_status_in_play.append(["Marked", "Auto Crit"])
            monster.status.remove("Marked")
            self.hero_crit = True
        elif "Sharpened" in hero.status:
            self.hero_status_in_play.append(["Sharpened", "Auto Crit"])
            hero.status.remove("Sharpened")
            self.hero_crit = True

        if "Disarming" in hero.status:
            atk_reduction = monster.atk // hero.sp_atk["Disarming Blows"]["dmg"]
            def_reduction = monster.defense // hero.sp_atk["Disarming Blows"]["dmg"]
            monster.atk = monster.atk - atk_reduction
            monster.defense = monster.defense - def_reduction
            if "Disarmed" not in monster.status:
                monster.status.append("Disarmed")
            if "Normal" in monster.status:
                monster.status.remove("Normal")
            self.monster_status_in_play.append(["Disarming", f"{atk_reduction} Atk Lost"])
            self.monster_status_in_play.append(["Disarming", f"{def_reduction} Def Lost"])

        if "Sundered" in monster.status:
            self.monster_status_in_play.append(["Sundered", "No Defense"])
            
        if "Ambiguity" in hero.status:
            if random.randint(1, 3) == 1:
                self.hero_status_in_play.append(["Ambiguity", "Damage Mitigated"])
                self.monster_damage_mitigated = True

        if "Bleeding" in monster.status:
            self.monster_status_in_play.append(["Bleeding", "10% Life Drain"])
            monster.status.remove("Bleeding")
            self.monster_status_damage += math.ceil(monster.current_hp * 0.1)

        if "Oath-Strong" in hero.status:
            defense_modifier = math.ceil(hero.defense * 0.25)
            self.hero_status_in_play.append(["Oath-Strong", f"Defense +{defense_modifier}"])
            hero.status.remove("Oath-Strong")
            self.hero_defense += defense_modifier

        if "Vulnerable" in monster.status:
            self.monster_status_in_play.append(["Vulnerable", "Negative Defense"])
            self.monster_status_damage += abs(self.monster.defense)

        if "Apex" in hero.status and monster.rank == "Apex":
            self.hero_status_in_play.append(["Apex", "Apex Damage x2"])
            self.hero_damage = math.ceil(self.hero_damage * 2)
        elif "Apex" in hero.status:
            aura = random.choice(["Silencer", "Barbed", "Drainer", "Absorbing", "Caustic", "Breaker"])
            if aura == "Silencer":
                if monster.initiative >= 5:
                    monster.initiative -= 5
                    self.hero_status_in_play.append(["Silencer", "Mon Init -5"])
            elif aura == "Barbed":
                barb_damage = math.ceil(monster.current_hp * 0.1)
                self.hero_status_in_play.append(["Barbed", f"{barb_damage} Status Damage"])
                self.monster_status_damage += barb_damage
            elif aura == "Drainer":
                self.hero_status_in_play.append(["Drainer", f"1EP Drained"])
                hero.current_ep += 1
                if hero.current_ep > hero.max_ep + hero.bonus_ep:
                    hero.current_ep = hero.max_ep + hero.bonus_ep
            elif aura == "Absorbing":
                absorbed_hp = math.ceil((self.hero.max_hp + self.hero.bonus_hp) * 0.2)
                self.hero_status_in_play.append(["Absorbing", f"{absorbed_hp} HP Absorbed"])
                hero.current_hp += absorbed_hp
                if hero.current_hp > hero.max_hp + hero.bonus_hp:
                    hero.current_hp = hero.max_hp + hero.bonus_hp
            elif aura == "Caustic":
                caustic_reduction = math.floor(monster.defense * 0.5)
                self.hero_status_in_play.append(["Caustic", f"Mon defense -{caustic_reduction}" ])
                monster.defense -= caustic_reduction
            elif aura == "Breaker":
                breaker_reduction = math.floor(monster.atk * 0.3)
                self.hero_status_in_play.append(["Breaker", f"Mon attack -{breaker_reduction}"])
                monster.atk -= breaker_reduction


    def martyr_mitigation(self):
        self.monster_damage_mitigated = True

    def post_damage_status_handler(self, hero, monster):
        if "Berserker" in hero.status:
            self.hero_status_in_play.append(["Berserker", "Damage x2"])
            hero.status.remove("Berserker")
            self.hero_damage *= 2
            print(f"Post Berserker Multiplier {self.hero_damage}")

        elif "Enraged Berserker" in hero.status:
            self.hero_status_in_play.append(["Enraged Berserker", "Damage x3"])
            hero.status.remove("Enraged Berserker")
            self.hero_damage *= 3
            print(f"Post EnBerserker Multiplier {self.hero_damage}")

        if "Executor" in hero.status and monster.current_hp // monster.max_hp < 0.41:
            self.hero_status_in_play.append(["Executor", "Damage x2"])
            hero.status.remove("Executor")
            self.hero_damage *= 2
            print(f"Executor {self.hero_damage}")

        if "Retribution" in hero.status:
            self.hero_status_in_play.append(["Retribution", "Thorn Damage"])
            self.monster_status_damage += self.monster_damage // 2

    def fractured_damage(self):
        if "Fractured" in self.hero.status:
            if self.hero_crit:
                self.hero_damage = 0
                self.hero_damage_mitigated = True
                fractured_damage = random.randint(25, 40)
                self.hero_status_damage += fractured_damage
                self.hero_status_in_play.append(["Fractured", f"Crit Denied"])
                return fractured_damage

    def roll_hero_damage(self):
        self.hero_damage = random.randint(self.hero_attack//2, self.hero_attack)

        if random.randint(1, 6) == 1 or self.hero_crit:
            self.hero_crit = True
            self.hero_status_in_play.append(["Hero Crit", f"Damage x{self.hero.crit_multiplier + self.hero.bonus_crit}"])

        if self.hero_crit:
            self.hero_damage = math.ceil(self.hero_damage * (self.hero.crit_multiplier + self.hero.bonus_crit))

    def roll_monster_damage(self):
        self.monster_damage = random.randint(self.monster_attack//2, self.monster_attack)

        if random.randint(1, 6) == 1:
            self.monster_crit = True
            self.monster_status_in_play.append(["Monster Crit", "Base Attack Increased"])

        if self.monster_crit:
            floor_damage = self.monster_attack - self.monster_attack // 8
            self.monster_damage = random.randint(floor_damage, self.monster_attack)

    def set_attack_order(self, hero, monster):
        if hero.initiative > monster.initiative:
            self.first_attacker = "Hero"
        elif "Flash" in hero.status:
            self.first_attacker = "Hero"
        else:
            self.first_attacker = "Monster"

    def check_damage_mitigation(self):
        if self.hero_damage <= self.monster_defense:
            self.hero_damage_mitigated = True
            self.monster_status_in_play.append(["Mitigated", "Hero Damage Defended"])
            self.hero_damage = 0

        if self.monster_damage <= self.hero_defense or\
                self.first_attacker == "Hero" and self.hero_damage >= self.monster.current_hp or self.monster.current_hp <= 0 or self.monster_damage_mitigated:
            self.monster_damage_mitigated = True
            self.monster_status_in_play.append(["Mitigated", "Monster Damage Defended"])
            self.monster_damage = 0

    def apply_damage(self, hero, monster):
        monster.current_hp -= self.monster_status_damage
        hero.current_hp -= self.hero_status_damage

        if not self.hero_damage_mitigated:
            self.hero_damage -= self.monster_defense
            monster.current_hp -= self.hero_damage
            if monster.current_hp < 0:
                self.overkill = abs(monster.current_hp)
                monster.current_hp = 0
        else:
            print("hero_damage_mitiaged")

        if not self.monster_damage_mitigated:
            self.monster_damage -= self.hero_defense
            hero.current_hp -= self.monster_damage
        else:
            print("monster damage mitigated")

