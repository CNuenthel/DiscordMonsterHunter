
class Leaderboard:

    def __init__(self):
        self.leaders = []
        self.tank_leaders = []
        self.fighter_leaders = []
        self.assassin_leaders = []
        self.cleric_leaders = []
        self.artificer_leaders = []
        self.mage_leaders = []
        self.dark_druid_leaders = []
        self.monk_leaders = []

    def check_leaderboard(self, raid, hero, time):

        def class_checks(board, raid, hero_stats):
            if len(board) < 10:
                board.append(hero_stats)
                board.sort(key=lambda x: x[1], reverse=False)
            else:
                for hero in board:
                    if raid.difficulty > hero.difficulty:
                        board.append(hero_stats)
                        board.sort(key=lambda x: x[1], reverse=False)
                        return True
            return False

        def chop_tail(board):
            board.remove(board[-1])

        append_list = [hero.name, raid.difficulty, hero.class_]

        if hero.class_ == "Tank":
            chop = class_checks(self.tank_leaders, raid, append_list)
            if chop:
                chop_tail(self.tank_leaders)

        elif hero.class_ == "Fighter":
            chop = class_checks(self.fighter_leaders, raid, append_list)
            if chop:
                chop_tail(self.fighter_leaders)

        elif hero.class_ == "Assassin":
            chop = class_checks(self.assassin_leaders, raid, append_list)
            if chop:
                chop_tail(self.assassin_leaders)

        elif hero.class_ == "Cleric":
            chop = class_checks(self.cleric_leaders, raid, append_list)
            if chop:
                chop_tail(self.cleric_leaders)

        elif hero.class_ == "Mage":
            chop = class_checks(self.mage_leaders, raid, append_list)
            if chop:
                chop_tail(self.mage_leaders)

        elif hero.class_ == "Artificer":
            chop = class_checks(self.artificer_leaders, raid, append_list)
            if chop:
                chop_tail(self.artificer_leaders)

        elif hero.class_ == "Dark Druid":
            chop = class_checks(self.dark_druid_leaders, raid, append_list)
            if chop:
                chop_tail(self.tank_leaders)

        elif hero.class_ == "Monk":
            chop = class_checks(self.monk_leaders, raid, append_list)
            if chop:
                chop_tail(self.monk_leaders)

        if len(self.leaders) < 10:
            self.leaders.append(append_list)
            self.leaders.sort(key=lambda x: x[1], reverse=False)
        else:
            for hero in self.leaders:
                if raid.difficulty > hero.difficulty:
                    self.leaders.append(append_list)
                    self.leaders.sort(key=lambda x: x[1], reverse=False)
                    self.leaders.remove(self.leaders[-1])

