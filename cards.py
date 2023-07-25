from main import Card, Minion, Player, Weapon
from enum import Enum


def choose_one(effect_one, effect_two, desc1, desc2):
    print(f"1. {desc1}")
    print(f"2. {desc2}")
    choose = input()
    try:
        choose = int(choose)
        if choose == 1:
            effect_one()
        elif choose == 2:
            effect_two()
        else:
            print("Choose a valid index (1 or 2).")
    except ValueError:
        print("Choose a valid index (1 or 2).")


def choose_target_enemy(player: Player, opponent: Player) -> Player | Minion:
    print("0. Opponent")
    for i, minion in enumerate(opponent.board):
        print(i + 1, minion.name)

    while True:
        index = int(input())
        if index == 0:
            return opponent
        elif 0 < index <= len(opponent.board):
            return opponent.board[index - 1]


def choose_target_any(player: Player, opponent: Player) -> Player | Minion:
    print("0. Opponent")
    for i, minion in enumerate(opponent.board):
        print(f"{i+1}. {minion.name}")
    l = len(opponent.board) + 1
    print("------Allied:------")
    print(f"{l}. Your Hero")
    for i, minion in enumerate(player.board):
        print(f"{i+1+l}. {minion.name}")

    while True:
        index = int(input())
        if index == 0:
            return opponent
        elif 0 < index < l:
            return opponent.board[index - 1]
        elif index == l:
            return player
        elif l < index < len(player.board) + l:
            return player.board[index - 1 - l]


def destroyed_check(player: Player, opponent: Player):
    for minion in player.board:
        if minion.health < 1:
            index = player.board.index(minion)
            player.board.pop(index)
            player.destroyed[minion.name] = player.destroyed.get(
                minion.name, 0) + 1
    for minion in opponent.board:
        if minion.health < 1:
            index = opponent.board.index(minion)
            opponent.board.pop(index)
            opponent.destroyed[minion.name] = opponent.destroyed.get(
                minion.name, 0) + 1


def coin_effect(player: 'Player', opponent):
    player.mana = min(10, player.mana + 1)


# Card effects

def minion_no_effect(player, opponent):
    return


# Battlecry effects

def bloodsail_corsair(player: 'Player', opponent: 'Player'):
    if opponent.weapon:
        opponent.weapon_durability -= 1
        if opponent.weapon_durability == 0:
            opponent.weapon = False


def abusive_sergeant(player, opponent):
    pass


def elven_archer(player: Player, opponent: Player):
    pass


def hungry_crab(player, opponent):
    pass


def voodoo_doctor(player, opponent):
    pass


def acidic_swamp_ooze(player: Player, opponent: Player):
    opponent.weapon = None
    opponent.weapon_durability = 0


def bloodsail_raider(player: Player, opponent: Player):
    pass

# Druid


def innervate(player: Player, opponent: Player):
    player.mana = min(10, player.mana + 2)


def moonfire(player: Player, opponent: Player):
    choose_target_any(player=player, opponent=opponent).health -= 1


def claw(player: Player, opponent: Player):
    player.attack += 2
    player.armor += 2


def nourish(player: Player, opponent: Player):
    def one():
        player.max_mana = min(10, player.max_mana + 1)
        player.mana = min(player.mana + 2, 10)

    def two():
        player.draw(3)
    choose_one(one, two, "Gain 2 Mana Crystals.", "Draw 3 cards.")


def healing_touch(player: Player, opponent: Player):
    player.health = min(30, player.health + 8)


def wildfire_growth(player: Player, opponent: Player):
    player.max_mana = min(10, player.max_mana + 1)


def starfire(player: Player, opponent: Player):
    choose_target_any(player, opponent).health -= 5
    player.draw()


def bite(player: Player, opponent: Player):
    player.attack += 4
    player.armor += 4


# Hunter

def arcane_shot(player, opponent):
    choose_target_any(player, opponent).health -= 2


# secrets
def explosive_trap(player, opponent):
    pass


def freezing_trap(player, opponent):
    pass


def misdirection(player, opponent):
    pass


def snake_trap(player, opponent):
    pass

# logic for the following two weapons is incomplete. card text not implemented yet.


def equip_weapon(player: Player, opponent: Player):
    pass


def eaglehorn_bow(player: Player, opponent):
    player.weapon_durability = 2
    player.attack = 3
    player.weapon = True


def gladiators_longbow(player: Player, opponent: Player):
    player.weapon_durability = 2
    player.attack = 5
    player.weapon = True


coin_card = Card(cost=0, effect=coin_effect, name="The Coin",
                 description="Gain 1 Mana Crystal this turn only.")

# Druid class

innervate_card = Card(cost=0, effect=innervate, name="Innervate",
                      description="Gain 2 Mana Crystals this turn only.")

moonfire_card = Card(cost=0, effect=moonfire,
                     name="Moonfire", description="Deal 1 damage")

eaglehorn_bow_card = Weapon(cost=3, effect=equip_weapon,
                            name="Eaglehorn Bow", description="", attack=3, durability=2)

gladiators_longbow_card = Weapon(
    cost=7, effect=equip_weapon, name="Gladiator's Longbow", description="", attack=5, durability=2)


claw_card = Card(cost=1, effect=claw, name="Claw",
                 description="Give your hero 2 attack this turn. Gain 2 armor.")

nourish_card = Card(cost=5, effect=nourish, name="Nourish",
                    description="Choose one - Gain 2 Mana Crystals; or Draw 3 cards.")

healing_touch_card = Card(cost=3, effect=healing_touch,
                          name="Healing Touch", description="Restore 8 Health.")

wildfire_growth_card = Card(cost=2, effect=wildfire_growth,
                            name="Wildfire Growth", description="Gain an empty Mana Crystal.")

bite_card = Card(cost=4, effect=bite, name="Bite",
                 description="Give your hero 4 Attack this turn. Gain 4 armor.")

starfire_card = Card(cost=6, effect=starfire, name="Starfire",
                     description="Deal 5 damage. Draw a card.")

# Paladin

silver_hand_recruit = Minion(cost=1, attack=1, health=1,
                             effect=minion_no_effect, name="Silver Hand Recruit", description="")

# Card tribes


class Tribes(Enum):
    MURLOC = "Murloc"
    BEAST = "Beast"
    TOTEM = "Totem"
    DEMON = "Demon"
    PIRATE = "Pirate"
    DRAGON = "Dragon"
    MECH = "Mech"
    UNDEAD = "Undead"


# Neutrals
# No card text

wisp_card = Minion(cost=0, attack=1, health=1,
                   effect=minion_no_effect, name="Wisp", description="")

murloc_raider_card = Minion(cost=1, attack=2, health=1,
                            effect=minion_no_effect, name="Murloc Raider", description="", tribes=[Tribes.MURLOC])

bloodfen_raptor_card = Minion(cost=2, attack=3, health=2,
                              effect=minion_no_effect, name="Bloodfen Raptor", description="")

river_crocolisk_card = Minion(cost=2, attack=2, health=3,
                              effect=minion_no_effect, name="River Crocolisk", description="")

magma_rager_card = Minion(cost=3, attack=5, health=1,
                          effect=minion_no_effect, name="Magma Rager", description="")

chillwind_yeti_card = Minion(cost=4, attack=4, health=5,
                             effect=minion_no_effect, name="Chillwind Yeti", description="")

oasis_snapjaw_card = Minion(cost=4, attack=2, health=7,
                            effect=minion_no_effect, name="Oasis Snapjaw", description="")

boulderfirst_ogre = Minion(cost=6, attack=6, health=7,
                           effect=minion_no_effect, name="Boulderfirst Ogre", description="")

core_hound_card = Minion(cost=7, attack=9, health=5,
                         effect=minion_no_effect, name="Core Hound", description="")

war_golem_card = Minion(cost=7, attack=7, health=7,
                        effect=minion_no_effect, name="War Golem", description="")

# Battlecry

# TODO, battlecry effect targeting
abusive_sergeant_card = Minion(cost=1, attack=2, health=1, effect=abusive_sergeant,
                               name="Abusive Sergeant", description="Battlecry: Give a minion +2 Attack this turn.")

bloodsail_corsair_card = Minion(
    cost=1, attack=1, health=2, effect=bloodsail_corsair, name="Bloodsail Corsair", description="")

elven_archer_card = Minion(cost=1, attack=1, health=1, effect=elven_archer,
                           name="Elven Archer", description="Battlecry: Deal 1 damage.")

hungry_crab_card = Minion(cost=1, attack=1, health=2, effect=hungry_crab,
                          name="Hungry Crab", description="Battlecry: Destroy a Murloc and gain +2/+2.")

voodoo_doctor_card = Minion(cost=1, attack=2, health=1, effect=voodoo_doctor,
                            name="Voodoo Doctor", description="Battlecry: Restore 2 Health.")

acidic_swamp_ooze_card = Minion(cost=2, attack=3, health=2, effect=acidic_swamp_ooze,
                                name="Acidic Swamp Ooze", description="Battlecry: Destroy your opponent's weapon.")

bloodsail_raider_card = Minion(cost=2, attack=2, health=3, effect=elven_archer, name="Bloodsail Raider",
                               description="Battlecry: Gain Attack equal to the Attack of your weapon.")


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
    bloodsail_corsair_card,
    bloodfen_raptor_card,
    river_crocolisk_card,
    magma_rager_card,
    chillwind_yeti_card,
    oasis_snapjaw_card,
    boulderfirst_ogre,
    core_hound_card,
    war_golem_card,
    acidic_swamp_ooze_card,
    eaglehorn_bow_card,
    gladiators_longbow_card,
]

incomplete_cards = [
    abusive_sergeant_card,
    elven_archer_card,
    hungry_crab_card,
    voodoo_doctor_card
]
