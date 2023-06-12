from main import Card, Player
import random


def innervate(player: Player, opponent: Player):
    player.mana += 2


def moonfire(player: Player, opponent: Player):
    opponent.health -= 1


def healing_touch(player: Player, opponent: Player):
    player.health = min(30, player.health + 8)


def wildfire_growth(player: Player, opponent: Player):
    player.max_mana += 1


def starfire(player: Player, opponent: Player):
    opponent.health -= 5
    player.draw()


def bite(player: Player, opponent: Player):
    player.attack += 4
    player.armor += 4


card_names = ["innervate", "moonfire", "healing_touch", "wildfire_growth", "starfire"]

innervate_card = Card(cost=0, effect=innervate, name="Innervate")

moonfire_card = Card(cost=0, effect=moonfire, name="Moonfire")

healing_touch_card = Card(cost=3, effect=healing_touch, name="Healing Touch")

wildfire_growth_card = Card(cost=2, effect=wildfire_growth, name="Wildfire Growth")

starfire_card = Card(cost=6, effect=starfire, name="Starfire")

bite_card = Card(cost=4, effect=bite, name="Bite")

cards = [
    innervate_card,
    moonfire_card,
    healing_touch_card,
    wildfire_growth_card,
    starfire_card,
    bite_card,
]


def get_random_deck():
    random_deck = []
    for card in cards:
        for _ in range(4):
            random_deck.append(card)
    random.shuffle(random_deck)
    return random_deck
