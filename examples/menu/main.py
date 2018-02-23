#!/usr/bin/python
"""

A simple nested menu example.

For something of this complexity, event system is hardly useful, so only entry
point system is showcased.

"""

import mofloc


def main():
    """ Main procedure. """
    mofloc.execute(TopLevel(), START)


FRUIT = ["apple", "orange", "banana"]
VEGETABLE = ["tomato", "cucumber"]
SPICE = ["salt", "pepper"]
START = "start"
CONTINUE = "continue"
OTHER_CAT = "from_other_category"


class TopLevel(mofloc.Flow):
    """ The top level menu, for choosing a category. """

    def __init__(self):
        super().__init__()
        self.register_entry_point(START, self.start)
        self.register_entry_point(CONTINUE, self.cont)
        self.categories = {
            "fruit": Fruit(),
            "vegetable": Vegetable(),
            "spice": Spice()
            }

    def start(self):
        """ Start from scratch. """
        print("Hello. This is a dumb menu program. Choose a category:")
        self.choose()

    def cont(self, old_cat, old_item):
        """ Continue from descending into a menu. """
        print(f"You've chosen: {old_item} from {old_cat}")
        print("Welcome back to the top level menu")
        print("Choose a category:")
        self.choose()

    def choose(self):
        """ Choose a category. """
        for cat in self.categories:
            print("* ", cat)
        while True:
            s = input("Category: ")
            if s not in self.categories:
                print("This is not in the list!")
                continue
            raise mofloc.ChangeFlow(self.categories[s], START)


class Fruit(mofloc.Flow):
    """ Fruit selecition. """

    def __init__(self):
        super().__init__()
        self.register_entry_point(START, self.start)
        self.register_entry_point(OTHER_CAT, self.from_other_category)

    def start(self):
        """ Pick a fruit. """
        print("Following fruit are available:")
        for fruit in FRUIT:
            print("* ", fruit)
        while True:
            s = input("Pick a fruit: ")
            if s not in FRUIT:
                if s in VEGETABLE:
                    print("This is not a fruit, but a vegetable. Changing the menu to vegetables...")
                    raise mofloc.ChangeFlow(Vegetable(), OTHER_CAT, s, self)
                if s in SPICE:
                    print("This is not a fruit, but a spice. Changing the menu to spices...")
                    raise mofloc.ChangeFlow(Spice(), OTHER_CAT, s, self)
                print("This is not in the list, try again.")
                continue
            print(f"Here's your fruit: {s}")
            raise mofloc.ChangeFlow(TopLevel(), CONTINUE, "fruit", s)

    def from_other_category(self, fruit, prev_menu):
        """ Pick a fruit requested from a different menu. """
        print(f"Do you want {fruit}? (yes/no)")
        while True:
            s = input()
            if s == "yes":
                print("Here we go then.")
                raise mofloc.ChangeFlow(TopLevel(), CONTINUE, "fruit", fruit)
            if s == "no":
                print("OK, taking you to the previous menu...")
                raise mofloc.ChangeFlow(prev_menu, START)
            print("yes/no only, please.")


class Vegetable(mofloc.Flow):
    """ Vegetable selecition. """

    def __init__(self):
        super().__init__()
        self.register_entry_point(START, self.start)
        self.register_entry_point(OTHER_CAT, self.from_other_category)

    def start(self):
        """ Pick a vegetable. """
        print("Following vegetables are available:")
        for veg in VEGETABLE:
            print("* ", veg)
        while True:
            s = input("Pick a vegetable: ")
            if s not in VEGETABLE:
                if s in FRUIT:
                    print("This is not a vegetable, but a fruit. Changing the menu to fruit...")
                    raise mofloc.ChangeFlow(Fruit(), OTHER_CAT, s, self)
                if s in SPICE:
                    print("This is not a vegetable, but a spice. Changing the menu to spices...")
                    raise mofloc.ChangeFlow(Spice(), OTHER_CAT, s, self)
                print("This is not in the list, try again.")
                continue
            print(f"Here's your vegetable: {s}")
            raise mofloc.ChangeFlow(TopLevel(), CONTINUE, "vegetables", s)

    def from_other_category(self, veg, prev_menu):
        """ Pick a vegetable requested from a different menu. """
        print(f"Do you want {veg}? (yes/no)")
        while True:
            s = input()
            if s == "yes":
                print("Here we go then.")
                raise mofloc.ChangeFlow(TopLevel(), CONTINUE, "vegetables", veg)
            if s == "no":
                print("OK, taking you to the previous menu...")
                raise mofloc.ChangeFlow(prev_menu, START)
            print("yes/no only, please.")


class Spice(mofloc.Flow):
    """ Spice selecition. """

    def __init__(self):
        super().__init__()
        self.register_entry_point(START, self.start)
        self.register_entry_point(OTHER_CAT, self.from_other_category)

    def start(self):
        """ Pick a spice. """
        print("Following spices are available:")
        for spice in SPICE:
            print("* ", spice)
        while True:
            s = input("Pick a spice: ")
            if s not in SPICE:
                if s in FRUIT:
                    print("This is not a spice, but a fruit. Changing the menu to fruit...")
                    raise mofloc.ChangeFlow(Fruit(), OTHER_CAT, s, self)
                if s in VEGETABLE:
                    print("This is not a spice, but a vegetable. Changing the menu to vegetables...")
                    raise mofloc.ChangeFlow(Vegetable(), OTHER_CAT, s, self)
                print("This is not in the list, try again.")
                continue
            print(f"Here's your spice: {s}")
            raise mofloc.ChangeFlow(TopLevel(), CONTINUE, "spice", s)

    def from_other_category(self, spice, prev_menu):
        """ Pick a spice requested from a different menu. """
        print(f"Do you want {spice}? (yes/no)")
        while True:
            s = input()
            if s == "yes":
                print("Here we go then.")
                raise mofloc.ChangeFlow(TopLevel(), CONTINUE, "spice", spice)
            if s == "no":
                print("OK, taking you to the previous menu...")
                raise mofloc.ChangeFlow(prev_menu, START)
            print("yes/no only, please.")


if __name__ == "__main__":
    main()
