from main import Card, Minion, Player
import random

# Game mechanics
def choose_one(effect_one, effect_two):
    print("1. Effect one.")
    print("2. Effect two.")
    print("3. Cancel.")
    choose = input()
    try:
        choose = int(choose)
        if choose == 1:
            effect_one()
        elif choose == 2:
            effect_two()
        elif choose == 3:
            # added following logic inside main.py:
            # return is not enough. need to not remove the card from the hand and not remove mana from player
            return False
        else:
            print("Choose a valid index.")
    except ValueError:
        print("Choose a valid index.")

# Card effects

def minion_no_effect(player: Player, opponent: Player):
    pass

# Battlecries

def bloodsail_corsair(player: Player, opponent: Player):
    if opponent.weapon is not None:
        opponent.weapon_durability -= 1
        if opponent.weapon_durability == 0:
            opponent.weapon = None

# Druid

def innervate(player: Player, opponent: Player):
    player.mana += 2


def moonfire(player: Player, opponent: Player):
    opponent.health -= 1


def claw(player: Player, opponent: Player):
    player.attack += 2
    player.armor += 2


# choose one effect. think about implementation
def nourish(player: Player, opponent: Player):
    # choose one
    def one():
        player.max_mana += 2
        player.mana = min(player.mana + 2, 10)
    def two():
        player.draw(3)
    if choose_one(one, two) == False:
        return False
    


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


# Hunter

def arcane_shot(player: Player, opponent: Player):
    opponent.health -= 2


# secrets
def explosive_trap(player: Player, opponent: Player):
    pass


def freezing_trap(player: Player, opponent: Player):
    pass


def misdirection(player: Player, opponent: Player):
    pass


def snake_trap(player: Player, opponent: Player):
    pass


def gladiators_longbow(player: Player, opponent: Player):
    player.weapon_durability += 2
    player.attack += 5


# currently-implemented cards
card_names = ["innervate", "moonfire", "healing_touch", "wildfire_growth", "starfire"]

innervate_card = Card(cost=0, effect=innervate, name="Innervate", description="Gain 2 Mana Crystals this turn only.")

moonfire_card = Card(cost=0, effect=moonfire, name="Moonfire", description="Deal 1 damage")

claw_card = Card(cost=1, effect=claw, name="Claw", description="Give your hero 2 attack this turn. Gain 2 armor.")

nourish_card = Card(cost=5, effect=nourish, name="Nourish", description="Choose one - Gain 2 Mana Crystals; or Draw 3 cards.")

healing_touch_card = Card(cost=3, effect=healing_touch, name="Healing Touch", description="Restore 8 Health.")

wildfire_growth_card = Card(cost=2, effect=wildfire_growth, name="Wildfire Growth", description="Gain an empty Mana Crystal.")

starfire_card = Card(cost=6, effect=starfire, name="Starfire", description="Deal 5 damage. Draw a card.")

bite_card = Card(cost=4, effect=bite, name="Bite", description="Give your hero 4 Attack this turn. Gain 4 armor.")

# neutrals

wisp_card = Minion(cost=0, attack=1, health=1, effect=minion_no_effect, name="Wisp", description="")

murloc_raider_card = Minion(cost=1, attack=2, health=1, effect=minion_no_effect, name="Murloc Raider", description="")

bloodsail_corsair_card = Minion(cost=1, attack=1, health=2, effect=bloodsail_corsair, name="Bloodsail Corsair", description="")

cards = [
    innervate_card,
    moonfire_card,
    claw_card,
    nourish_card,
    healing_touch_card,
    wildfire_growth_card,
    starfire_card,
    bite_card,
    wisp_card,
    murloc_raider_card,
    bloodsail_corsair_card
]

neutral_cards = [
    wisp_card,
    murloc_raider_card,
    bloodsail_corsair_card
]

def get_random_deck():
    random_deck = []
    for card in cards:
        for _ in range(2):
            random_deck.append(card)
    random.shuffle(random_deck)
    return random_deck
