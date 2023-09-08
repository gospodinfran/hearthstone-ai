import unittest
from main import Mage, Warrior, Priest, Hunter, Paladin, Druid, Rogue, Shaman, Warlock, Player, silver_hand_recruit, wicked_knife, basic_totems


class TestMage(unittest.TestCase):

    def test_use_power(self):
        p = Player(hero_class=Mage(), starting_mana=2)
        opp = Player()

        p.use_hero_power(p, opp, opp)

        self.assertEqual(opp.health, opp.max_health - 1,
                         "Mage Hero Power does not work properly.")


class TestWarrior(unittest.TestCase):

    def test_use_power(self):
        p = Player(hero_class=Warrior(), starting_mana=2)

        p.use_hero_power(p)

        self.assertEqual(p.armor, 2,
                         "Warrior Hero Power does not work properly.")


class TestPriest(unittest.TestCase):

    def test_use_power(self):
        p = Player(hero_class=Priest(), starting_mana=2)
        p.health -= 3

        p.use_hero_power(p, target=p)

        self.assertEqual(p.health, 29,
                         "Priest Hero Power does not work properly.")


class TestHunter(unittest.TestCase):

    def test_use_power(self):
        p = Player(hero_class=Hunter(), starting_mana=2)
        opp = Player()

        p.use_hero_power(p, opp)

        self.assertEqual(opp.health, opp.max_health - 2,
                         "Hunter Hero Power does not work properly.")


class TestPaladin(unittest.TestCase):

    def test_use_power(self):
        p = Player(hero_class=Paladin(), starting_mana=2)

        p.use_hero_power(p)

        self.assertEqual(p.board, [silver_hand_recruit],
                         "Paladin Hero Power does not work properly.")


class TestDruid(unittest.TestCase):

    def test_use_power(self):
        p = Player(hero_class=Druid(), starting_mana=2)

        p.use_hero_power(p)

        self.assertEqual(p.armor, 1,
                         "Druid Hero Power does not work properly.")
        self.assertEqual(
            p.attack, 1, "Druid Hero Power does not work properly.")


class TestRogue(unittest.TestCase):

    def test_use_power(self):
        p = Player(hero_class=Rogue(), starting_mana=2)

        p.use_hero_power(p)

        self.assertEqual(p.weapon, wicked_knife,
                         "Rogue Hero Power does not work properly.")


class TestShaman(unittest.TestCase):

    def test_use_power(self):
        p = Player(hero_class=Shaman(), starting_mana=2)

        p.use_hero_power(p)
        token = p.board[0]

        self.assertIn(token, basic_totems,
                      "Shaman Hero Power does not work properly.")


class TestWarlock(unittest.TestCase):

    def test_use_power(self):
        p = Player(hero_class=Warlock(), starting_mana=2)
        handsize = len(p.hand)

        p.use_hero_power(p)

        self.assertEqual(p.health, p.max_health - 2,
                         "Warlock Hero Power does not work properly.")
        self.assertEqual(len(p.hand), handsize + 1,
                         "Warlock Hero Power does not work properly.")


if __name__ == "__main__":
    unittest.main()
