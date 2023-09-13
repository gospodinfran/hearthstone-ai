import unittest
from main import Mage, Warrior, Priest, Hunter, Paladin, Druid, Rogue, Shaman, Warlock, Player, silver_hand_recruit, wicked_knife, basic_totems, moonfire_card, card_factory


class TestPlayerInit(unittest.TestCase):

    def test_default_init(self):
        player = Player()
        self.assertEqual(player.max_health, 30,
                         "Player default max_health should be 30.")
        self.assertEqual(player.health, 30,
                         "Player default health should be 30.")
        self.assertIsInstance(player.hero_class, Mage)
        self.assertTrue(player. hero_power)
        self.assertEqual(player.armor, 0)
        self.assertEqual(player.mana, 0)
        self.assertEqual(player.max_mana, 0)
        self.assertIsNone(player.weapon)
        self.assertEqual(player.weapon_durability, 0)
        self.assertFalse(player.attacked)
        self.assertEqual(player.attack, 0)
        self.assertEqual(player.fatigue, 0)
        self.assertIsNone(player.persistent_effects, None)
        self.assertEqual(player.end_of_turn_effects,
                         [], "EOT effects should be empty.")
        self.assertListEqual(player.one_of_effects, [])
        self.assertListEqual(player.hand, [])
        self.assertListEqual(player.board, [])
        self.assertDictEqual(player.played, {})
        self.assertDictEqual(player.destroyed, {})
        self.assertEqual(player.deck, [moonfire_card for _ in range(30)])


class TestPlayerTakeDamage(unittest.TestCase):

    def test_take_damage(self):
        player = Player()
        player.take_damage(5)
        self.assertEqual(player.health, 25)
        self.assertEqual(player.armor, 0)

        player.armor = 10
        player.take_damage(10)
        self.assertEqual(player.health, 25)
        self.assertEqual(player.armor, 0)

        player.armor = 15
        player.take_damage(10)
        self.assertEqual(player.health, 25)
        self.assertEqual(player.armor, 5)

        player.armor = 15
        player.take_damage(20)
        self.assertEqual(player.health, 20)
        self.assertEqual(player.armor, 0)


class TestPlayerDraw(unittest.TestCase):
    # also relies on take_damage method

    def test_play_draw(self):
        player = Player()
        # create game variable because draw method checks for if 'game' in locals()
        game = True
        player.draw()
        self.assertListEqual(player.hand, [moonfire_card])
        self.assertEqual(len(player.hand), 1)

        player.draw(9)
        self.assertEqual(len(player.hand), 10)

        player.draw(20)
        self.assertTrue(player.health == 30)

        player.draw()
        self.assertTrue(player.health == 29)

        player.draw(5)
        self.assertTrue(player.health == 9)
        self.assertEqual(len(player.hand), 10)


class TestMage(unittest.TestCase):

    def test_use_power(self):
        player = Player(hero_class=Mage(), starting_mana=2)
        opp = Player()

        player.use_hero_power(player, opp, opp)

        self.assertEqual(opp.health, opp.max_health - 1,
                         "Mage Hero Power does not work properly.")


class TestWarrior(unittest.TestCase):

    def test_use_power(self):
        player = Player(hero_class=Warrior(), starting_mana=2)

        player.use_hero_power(player)

        self.assertEqual(player.armor, 2,
                         "Warrior Hero Power does not work properly.")


class TestPriest(unittest.TestCase):

    def test_use_power(self):
        player = Player(hero_class=Priest(), starting_mana=2)
        player.health -= 3

        player.use_hero_power(player, target=player)

        self.assertEqual(player.health, 29,
                         "Priest Hero Power does not work properly.")


class TestHunter(unittest.TestCase):

    def test_use_power(self):
        player = Player(hero_class=Hunter(), starting_mana=2)
        opp = Player()

        player.use_hero_power(player, opp)

        self.assertEqual(opp.health, opp.max_health - 2,
                         "Hunter Hero Power does not work properly.")


class TestPaladin(unittest.TestCase):

    def test_use_power(self):
        player = Player(hero_class=Paladin(), starting_mana=2)

        player.use_hero_power(player)

        self.assertEqual(player.board[0].name, card_factory(silver_hand_recruit).name,
                         "Paladin Hero Power does not work properly.")


class TestDruid(unittest.TestCase):

    def test_use_power(self):
        player = Player(hero_class=Druid(), starting_mana=2)

        player.use_hero_power(player)

        self.assertEqual(player.armor, 1,
                         "Druid Hero Power does not work properly.")
        self.assertEqual(
            player.attack, 1, "Druid Hero Power does not work properly.")


class TestRogue(unittest.TestCase):

    def test_use_power(self):
        player = Player(hero_class=Rogue(), starting_mana=2)

        player.use_hero_power(player)

        self.assertEqual(player.weapon, wicked_knife,
                         "Rogue Hero Power does not work properly.")


class TestShaman(unittest.TestCase):

    def test_use_power(self):
        player = Player(hero_class=Shaman(), starting_mana=2)

        player.use_hero_power(player)
        token = player.board[0]

        self.assertIn(token, basic_totems,
                      "Shaman Hero Power does not work properly.")


class TestWarlock(unittest.TestCase):

    def test_use_power(self):
        player = Player(hero_class=Warlock(), starting_mana=2)
        handsize = len(player.hand)

        player.use_hero_power(player)

        self.assertEqual(player.health, player.max_health - 2,
                         "Warlock Hero Power does not work properly.")
        self.assertEqual(len(player.hand), handsize + 1,
                         "Warlock Hero Power does not work properly.")


if __name__ == "__main__":
    unittest.main()
