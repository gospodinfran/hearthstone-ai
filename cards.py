from main import Card, Minion, Player, Weapon
from typing import Tuple, Literal
import random
from enum import Enum


def destroy_minion(player, opponent, target, index, player_or_opponent):
    # 0 = player, 1 = opponent
    if player_or_opponent == 0:
        player.board.pop(index)
        player.destroyed[target.name] = player.destroyed.get(
            target.name, 0) + 1

    elif player_or_opponent == 1:
        opponent.board.pop(index)
        opponent.destroyed[target.name] = opponent.destroyed.get(
            target.name, 0) + 1


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
    print("------Enemy:------")
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
    print("------Enemy:------")
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
        elif l < index < len(player.board) + l + 1:
            return player.board[index - 1 - l]


def choose_any_minion(player, opponent) -> Tuple[Minion, int, Literal[1, 0]]:
    # recommended way to destructure:
    # minion, index, p_or_o = choose_any_minion(player, opponent)
    i = 0
    print("------Enemy:------")
    for minion in opponent.board:
        print(f"{i+1}. {minion.name}")
        i += 1

    print("------Allied:------")
    for minion in player.board:
        print(f"{i+1}. {minion.name}")
        i += 1

    while True:
        index = int(input())
        if 0 < index <= (len(opponent.board) + len(player.board)):
            if index <= len(opponent.board):
                # returning tuple (Minion, hand index, player/opponent)
                # player 0, opponent 1
                return (opponent.board[index - 1], index - 1, 1)
            else:
                return (player.board[index - 1], index - 1, 0)


# Gets called after every card is played. All deathrattles trigger here.
def destroyed_check(player: Player, opponent: Player):
    for minion in player.board:
        if minion.health < 1:
            index = player.board.index(minion)
            player.board.pop(index)
            player.destroyed[minion.name] = player.destroyed.get(
                minion.name, 0) + 1
            if minion.deathrattles:
                for dr in minion.deathrattles:
                    dr(player, opponent)
    for minion in opponent.board:
        if minion.health < 1:
            index = opponent.board.index(minion)
            opponent.board.pop(index)
            opponent.destroyed[minion.name] = opponent.destroyed.get(
                minion.name, 0) + 1
            if minion.deathrattles:
                for dr in minion.deathrattles:
                    dr(player, opponent)


def deal_damage(target, damage):
    if hasattr(target, 'take_damage'):
        target.take_damage(damage)
    else:
        target.health -= damage


def restore_health(target: Player | Minion, amount: int):
    target.health = min(target.max_health, target.health + amount)


def increase_health(target: Player | Minion, amount):
    target.max_health += amount
    target.health += amount


def apply_all_enemy_board(player, opponent, effect):
    for minion in opponent.board:
        effect(minion)


def apply_all_friendly_board(player, opponent, effect):
    for minion in player.board:
        effect(minion)


def apply_all_board(player, opponent, effect):
    for minion in player.board:
        effect(minion)
    for minion in opponent.board:
        effect(minion)


def coin_effect(player: 'Player', opponent):
    player.mana = min(10, player.mana + 1)


# Card effects

def minion_no_effect(player, opponent):
    return


class Tribes(Enum):
    MURLOC = "Murloc"
    BEAST = "Beast"
    TOTEM = "Totem"
    DEMON = "Demon"
    PIRATE = "Pirate"
    DRAGON = "Dragon"
    MECH = "Mech"
    UNDEAD = "Undead"

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
    target = choose_target_any(player, opponent)
    deal_damage(target, 1)


def claw(player: Player, opponent: Player):
    player.attack += 2
    player.armor += 2


def naturalize(player, opponent):
    minion, index, p_or_o = choose_any_minion(player, opponent)
    destroy_minion(player, opponent, minion, index, p_or_o)
    opponent.draw(2)


def savagery(player, opponent):
    minion, index, p_or_o = choose_any_minion(player, opponent)
    minion.health -= player.attack
    if minion.health < 1:
        destroy_minion(player, opponent, minion, index, p_or_o)


def mark_of_the_wild(player, opponent):
    minion, index, p_or_o = choose_any_minion(player, opponent)
    minion.max_health += 2
    minion.health += 2
    minion.attack += 2
    # TODO add taunt


def power_of_the_wild(player, opponent):
    def one():
        def effect(minion):
            minion.max_health += 1
            minion.health += 1
            minion.attack += 1

        apply_all_friendly_board(player, opponent, effect)

    def two():
        if len(player.board) < 7:
            player.board.append(panther_token)

    choose_one(one, two, "Give your minions +1/+1.", "Summong a 3/2 panther.")


def wild_growth(player: Player, opponent: Player):
    player.max_mana = min(10, player.max_mana + 1)


def wrath(player, opponent):
    def one():
        minion, index, p_or_o = choose_any_minion(player, opponent)
        minion.health -= 3
        if minion.health < 1:
            destroy_minion(player, opponent, minion, index, p_or_o)

    def two():
        minion, index, p_or_o = choose_any_minion(player, opponent)
        minion.health -= 1
        if minion.health < 1:
            destroy_minion(player, opponent, minion, index, p_or_o)
        player.draw()

    choose_one(one, two, "Deal 3 damage to a minion.",
               "Deal 1 damage and draw a card.")


def healing_touch(player: Player, opponent: Player):
    target = choose_target_any(player, opponent)
    target.health = min(target.max_health, target.health + 8)


def mark_of_nature(player, opponent):
    def one():
        minion, index, p_or_o = choose_any_minion(player, opponent)
        minion.attack += 4

    def two():
        minion, index, p_or_o = choose_any_minion(player, opponent)
        minion.max_health += 4
        minion.health += 4
        # TODO, add taunt when implemented

    choose_one(one, two, "Give a minion +4 Attack.", "Or +4 Health and Taunt.")


def savage_roar(player, opponent):
    player.attack += 2

    def effect(minion):
        def remove_attack():
            setattr(minion, 'attack', minion.attack - 2)
        minion.attack += 2
        player.one_of_effects.append(remove_attack)

    apply_all_friendly_board(player, opponent, effect)


def bite(player: Player, opponent: Player):
    player.attack += 4
    player.armor += 4


def keeper_of_the_grove(player, opponent):
    def one():
        deal_damage(choose_target_any(player, opponent), 2)

    def two():
        # TODO: silence a minion
        # silence(choose_any_minion(player, opponent))
        pass

    choose_one(one, two, "Deal 2 damage", "Silence a minion")


def soul_of_the_forest(player, opponent):
    def effect(minion: Minion):
        def dr(player, opponent):
            player.board.append(treant_token)
        minion.deathrattles.append(dr)

    apply_all_friendly_board(player, opponent, effect)


def swipe(player, opponent):
    target = choose_target_enemy(player, opponent)
    deal_damage(target, 4)

    if hasattr(target, 'use_hero_power'):
        apply_all_enemy_board(player, opponent, lambda minion: setattr(
            minion, 'health', minion.health - 1))
    else:
        deal_damage(opponent, 1)
        target_idx = opponent.board.index(target)
        for i, enemy_minion in enumerate(opponent.board):
            if i == target_idx:
                continue
            deal_damage(enemy_minion, 1)

    destroyed_check(player, opponent)


def druid_of_the_claw(player, opponent):
    def one():
        # TODO, implement Charge, pass it here
        pass

    def two():
        # TODO, give it Taunt and 2 health
        pass
    choose_one(one, two, "Gain Charge", "Gain +2 health and Taunt.")


def nourish(player: Player, opponent: Player):
    def one():
        player.max_mana = min(10, player.max_mana + 1)
        player.mana = min(player.mana + 2, 10)

    def two():
        player.draw(3)

    choose_one(one, two, "Gain 2 Mana Crystals.", "Draw 3 cards.")


def starfall(player, opponent):
    def one():
        minion, index, p_or_o = choose_any_minion(player, opponent)
        deal_damage(minion, 5)

    def two():
        def effect(minion):
            deal_damage(minion, 2)
        apply_all_enemy_board(player, opponent, effect)

    choose_one(one, two, "Deal 5 damage to a minion.",
               "Deal 2 damage to all enemy minions.")

    destroyed_check(player, opponent)


def force_of_nature(player, opponent):
    treant1 = card_factory(treant_token)
    treant2 = card_factory(treant_token)
    treant3 = card_factory(treant_token)
    player.board.extend([treant1, treant2, treant3])

    def effect():
        player.board.remove(treant1)
        player.board.remove(treant2)
        player.board.remove(treant3)
    player.one_of_effects.append(effect)


def starfire(player: Player, opponent: Player):
    deal_damage(choose_target_any(player, opponent), 5)
    player.draw()


def ancient_of_lore(player, opponent):
    def one():
        player.draw(2)

    def two():
        restore_health(choose_target_any(player, opponent), 5)

    choose_one(one, two, "Draw 2 cards.", "Restore 5 Health.")


def ancient_of_war(player, opponent):
    # TODO, target self somehow
    # currently most sensible way is seeing if ancient already exists and it isn't damaged: no muy bueno

    def one():
        target = None
        for minion in player.board:
            if minion.name == "Ancient of War" and minion.attack == 5 and minion.health == 5:
                target = minion
        if target:
            target.attack += 5

    def two():
        target = None
        for minion in player.board:
            if minion.name == "Ancient of War" and minion.attack == 5 and minion.health == 5:
                target = minion
        if target:
            target.max_health += 5
            target.health = target.max_health
    choose_one(one, two, "Gain +5 Attack.", "Gain +5 Health and Taunt.")


def cenarius(player, opponent):
    def one():
        def effect(minion):
            if minion.name == "Cenarius":
                return
            minion.attack += 2
            minion.max_health += 2
            minion.health = minion.max_health
        apply_all_friendly_board(player, opponent, effect)

    def two():
        # TODO give them taunt
        player.board.extend([treant_token, treant_token])

    choose_one(one, two, "Give your other minions +2/+2.",
               "Summon two 2/2 Treants with Taunt.")

# Hunter


def arcane_shot(player, opponent):
    deal_damage(choose_target_any(player, opponent), 2)


# secrets
def explosive_trap(player, opponent):
    pass


def freezing_trap(player, opponent):
    pass


def misdirection(player, opponent):
    pass


def snake_trap(player, opponent):
    pass

# Priest


def circle_of_healing(player, opponent):
    def effect(minion):
        restore_health(minion, 4)
    apply_all_board(player, opponent, effect)


def silence(player, opponent):
    # TODO, silence
    pass


def holy_smite(player, opponent):
    deal_damage(choose_target_any(player, opponent), 2)


def inner_fire(player, opponent):
    minion, index, p_or_o = choose_any_minion(player, opponent)
    minion.attack = minion.health


def mind_vision(player, opponent):
    rand_card = random.choice(opponent.hand)
    player.hand.append(rand_card)


def power_word_shield(player, opponent):
    minion, i, p_or_r = choose_any_minion(player, opponent)
    increase_health(minion, 2)
    player.draw()


def divine_spirit(player, opponent):
    minion, index, p_or_o = choose_any_minion(player, opponent)
    increase_health(minion, minion.health)


def mind_blast(player, opponent):
    deal_damage(opponent, 5)


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

# Deathrattles


def strength_totem_dr(player, opponent):
    player.end_of_turn_effects.remove(strength_totem_effect)


def healing_totem_dr(player, opponent):
    player.end_of_turn_effects.remove(healing_totem_effect)


coin_card = Card(cost=0, effect=coin_effect, name="The Coin",
                 description="Gain 1 Mana Crystal this turn only.")

# Druid class

innervate_card = Card(cost=0, effect=innervate, name="Innervate",
                      description="Gain 2 Mana Crystals this turn only.")

moonfire_card = Card(cost=0, effect=moonfire,
                     name="Moonfire", description="Deal 1 damage")

naturalize_card = Card(cost=1, effect=naturalize, name="Naturalize",
                       description="Destroy a minion. Your opponent draws 2 cards.")

savagery_card = Card(1, savagery, "Savagery",
                     "Deal damage equal to your hero's Attack to a minion.")

mark_of_the_wild_card = Card(
    2, mark_of_the_wild, "Mark of the Wild", "Give a minion Taunt and +2/+2.")

power_of_the_wild_card = Card(2, power_of_the_wild, "Power of the Wild",
                              "Choose One - Give your minions +1/+1; or Summon a 3/2 Panther.")

wild_growth_card = Card(cost=2, effect=wild_growth,
                        name="Wild Growth", description="Gain an empty Mana Crystal.")

wrath_card = Card(2, wrath, "Wrath",
                  "Choose One - Deal 3 damage to a minion; or 1 damage and draw a card.")

healing_touch_card = Card(cost=3, effect=healing_touch,
                          name="Healing Touch", description="Restore 8 Health.")

mark_of_nature_card = Card(3, mark_of_nature, "Mark of Nature",
                           "Choose One - Give a minion +4 Attack; or +4 Health and Taunt.")

savage_roar_card = Card(3, savage_roar, "Savage Roar",
                        "Give your characters +2 Attack this turn")

bite_card = Card(cost=4, effect=bite, name="Bite",
                 description="Give your hero 4 Attack this turn. Gain 4 armor.")

keeper_of_the_grove_card = Minion(4, 2, 4, keeper_of_the_grove, "Keeper of the Grove",
                                  "Choose One - Deal 2 damage; or Silence a minion.")

soul_of_the_forest_card = Card(4, soul_of_the_forest, "Soul of the Forest",
                               "Give your minions 'Deathrattle: Summon a 2/2 Treant'.")

swipe_card = Card(4, swipe, "Swipe",
                  "Choose One - Deal 5 damage to a minion; or 2 damage to all enemy minions.")

# not yet in cards array since not fully implemented
druid_of_the_claw_card = Minion(
    5, 4, 4, druid_of_the_claw, "Druid of the Claw", "Choose One - Charge; or +2 Health and Taunt.")

eaglehorn_bow_card = Weapon(cost=3, effect=equip_weapon,
                            name="Eaglehorn Bow", description="", attack=3, durability=2)

gladiators_longbow_card = Weapon(
    cost=7, effect=equip_weapon, name="Gladiator's Longbow", description="", attack=5, durability=2)


claw_card = Card(cost=1, effect=claw, name="Claw",
                 description="Give your hero 2 attack this turn. Gain 2 armor.")


nourish_card = Card(cost=5, effect=nourish, name="Nourish",
                    description="Choose one - Gain 2 Mana Crystals; or Draw 3 cards.")

starfall_card = Card(5, starfall, "Starfall",
                     "Deal 5 damage to a minion; or 2 damage to all enemy minions.")

force_of_nature_card = Card(6, force_of_nature, "Force of Nature",
                            "Summon three 2/2 Treants with Charge that die at the end of the turn.")

starfire_card = Card(cost=6, effect=starfire, name="Starfire",
                     description="Deal 5 damage. Draw a card.")

ancient_of_lore_card = Minion(7, 5, 5, ancient_of_lore, "Ancient of Lore",
                              "Choose One - Draw 2 cards; or Restore 5 Health.")

ancient_of_war_card = Minion(7, 5, 5, ancient_of_war, "Ancient of War",
                             "Choose One - +5 Attack or; +5 Health and Taunt.")

ironbark_prodector_card = Minion(
    8, 8, 8, minion_no_effect, "Ironbark Protector", "Taunt")

cenarius_card = Minion(9, 5, 8, cenarius, "Cenarius",
                       "Choose One - Give your other minions +2/+2; or Summon two 2/2 Treants with Taunt.")

# Priest cards

circle_of_healing_card = Card(
    0, circle_of_healing, "Circle of Healing", "Restore 4 Health to ALL minions.")

holy_smite_card = Card(1, holy_smite, "Holy Smite", "Deal 2 damage.")

inner_fire_card = Card(1, inner_fire, "Inner Fire",
                       "Change a minion's Attack to be equal to its Health.")

mind_vision_card = Card(1, mind_vision, "Mind Vision",
                        "Put a copy of a random card in your opponent's hand into your hand.")

power_word_shield_card = Card(
    1, power_word_shield, "Power Word: Shield", "Give a minion +2 Health. Draw a card.")

divine_spirit_card = Card(
    2, divine_spirit, "Divine Spirit", "Double a minion's health.")

mind_blast_card = Card(2, mind_blast, "Mind Blast",
                       "Deal 5 damage to the enemy hero.")


# Paladin


# Token Cards

def strength_totem_effect(player, opponent):
    if len(player.board) > 1:
        randint = random.randint(0, len(player.board) - 1)
        while player.board[randint].name == strength_totem_token.name:
            randint = random.randint(0, len(player.board) - 1)
        player.board[randint].attack += 1


def healing_totem_effect(player, opponent):
    apply_all_friendly_board(player, opponent, lambda minion: setattr(
        minion, 'health', min(minion.max_health, minion.health + 1)))


# Has to look like this because this effect happens when it is played from hand.
def strength_totem(player: Player, opponent):
    player.end_of_turn_effects.append(strength_totem_effect(player, opponent))


def healing_totem(player, opponent):
    player.end_of_turn_effects.append(healing_totem_effect(player, opponent))


treant_token = Minion(1, 2, 2, minion_no_effect, "Treant", "")

searing_totem_token = Minion(
    1, 1, 1, minion_no_effect, "Searing totem", "", [Tribes.TOTEM])

stoneclaw_totem_token = Minion(
    1, 0, 2, minion_no_effect, "Stoneclaw totem", "", [Tribes.TOTEM])

strength_totem_token = Minion(
    1, 0, 2, strength_totem, "Strength totem", "", [Tribes.TOTEM], [strength_totem_dr])

healing_totem_token = Minion(
    1, 0, 2, healing_totem, "Healing totem", "", [Tribes.TOTEM], [healing_totem_dr])

basic_totems = [
    searing_totem_token,
    stoneclaw_totem_token,
    strength_totem_token,
    healing_totem_token
]

panther_token = Minion(2, 3, 2, minion_no_effect,
                       "Panther", "", [Tribes.BEAST])

silver_hand_recruit = Minion(cost=1, attack=1, health=1,
                             effect=minion_no_effect, name="Silver Hand Recruit", description="")

wicked_knife = Weapon(1, equip_weapon, "Wicked Knife", "", 1, 2)

# Card tribes


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


def card_factory(card: Card):
    if hasattr(card, "tribes"):
        # minion
        return Minion(card.cost, card.attack, card.health, card.effect, card.name, card.description, card.tribes, card.deathrattles)
    elif hasattr(card, "durability"):
        # weapon
        return Weapon(card.cost, card.effect, card.name, card.description, card.attack, card.durability)
    else:
        # spell
        return Card(card.cost, card.effect, card.name, card.description)

# cards are initialized only once and are then reused. fix this and the bug will go away.


# card templates for the factory
cards = [
    # innervate_card,
    # moonfire_card,
    # claw_card,
    # naturalize_card,
    # savagery_card,
    # mark_of_the_wild_card,
    # power_of_the_wild_card,
    # wild_growth_card,
    # wrath_card,
    # healing_touch_card,
    # mark_of_nature_card,
    # savage_roar_card,
    # bite_card,
    # keeper_of_the_grove_card,
    # soul_of_the_forest_card,
    # swipe_card,
    # nourish_card,
    # starfall_card,
    # force_of_nature_card,
    # starfire_card,
    # ancient_of_lore_card,
    # ancient_of_war_card,
    # ironbark_prodector_card,
    # cenarius_card,
    circle_of_healing_card,
    holy_smite_card,
    inner_fire_card,
    mind_vision_card,
    power_word_shield_card,
    divine_spirit_card,
    mind_blast_card,
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
    gladiators_longbow_card
]


def generate_deck(cards):
    deck = []
    for card in cards:
        deck.extend([card_factory(card), card_factory(card)])
    return deck


incomplete_cards = [
    abusive_sergeant_card,
    elven_archer_card,
    hungry_crab_card,
    voodoo_doctor_card
]
