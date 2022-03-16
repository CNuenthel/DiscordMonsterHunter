import random
from items import Items
from equipment import Armors


class Shop(Items):

    def __init__(self):
        """
        Initializes a variable as the master item list to manipulate
        """
        super().__init__()
        self.armor_closet = Armors()
        self.armors = self.armor_closet.armors
        self.for_sale = []
        self.shop = []

    def shop_items(self):
        """
        Sets 3 tier1, 2 tier2, 1, tier3 items into the shop
        """
        for_sale = [random.choices(self.tier1_items, k=3), random.choices(self.tier2_items, k=2),
                    random.choices(self.tier3_items, k=1), random.choices(self.tier4_items, k=1),
                    random.choices(self.armors, weights=(40, 40, 40, 40, 1), k=1)]
        return for_sale

    def set_cost(self, for_sale_list):
        """
        Identifies cost of item param
        """
        def check_item_tier(item):
            if item in self.tier1_items:
                cost = random.randint(200, 400)
            elif item in self.tier2_items:
                cost = random.randint(400, 600)
            elif item in self.tier3_items:
                cost = random.randint(800, 1200)
            elif item in self.tier4_items:
                cost = random.randint(8000, 12000)
            elif item in self.armors:
                cost = random.randint(5000, 6000)
                if item == "Bag Of Holding":
                    cost = random.randint(15000, 20000)
            else:
                raise ValueError(f"{item} not found in tier lists")
            return cost

        def check_lists(for_sale_list):
            master = []
            for tier in for_sale_list:
                for item in tier:
                    master.append([item, check_item_tier(item)])
            return master

        return check_lists(for_sale_list)
