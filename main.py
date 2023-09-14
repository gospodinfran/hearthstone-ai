from typing import List, Dict, Callable, Tuple, Literal
import random
from enum import Enum


class HeroClass():
    def use_hero_power(self, player=None, opponent=None, target=None):
        if player.hero_power and player.mana >= 2:
            self.use_power(player, opponent, target)
            player.mana -= 2
            player.hero_power = False
            print("Hero power used.")
            return True
        else:
            print("Hero power already used or not enough mana.")

    def use_power(self, player=None, opponent=None, target=None):
        raise NotImplementedError("This will be overridden.")


class Mage(HeroClass):
    def use_power(self, player, opponent, target):
        deal_damage(target, 1)


class Warrior(HeroClass):
    def use_power(self, player, opponent, target):
        player.armor += 2


class Priest(HeroClass):
    def use_power(self, player, opponent, target):
        # TODO, implement base stats for all minions because heals can't go over base health
        target.health = min(target.max_health, target.health + 2)


class Hunter(HeroClass):
    def use_power(self, player, opponent, target):
        deal_damage(opponent, 2)


class Paladin(HeroClass):
    def use_power(self, player, opponent, target):
        if len(player.board) < 7:
            player.board.append(card_factory(silver_hand_recruit))


class Druid(HeroClass):
    def use_power(self, player, opponent, target):
        player.armor += 1
        player.attack += 1


class Rogue(HeroClass):
    def use_power(self, player, opponent, target):
        wicked_knife.play(player, opponent)


class Shaman(HeroClass):
    def use_power(self, player, opponent, target):
        if len(player.board) < 7:
            # check if all 4 basic totems are on player board. if so don't allow hero power to go through
            basic_totems_cpy = basic_totems.copy()
            for totem in basic_totems_cpy:
                for minion in player.board:
                    if totem.name == minion.name:
                        basic_totems_cpy = [
                            t for t in basic_totems_cpy if t.name != totem.name]

            if basic_totems_cpy:
                rand_totem = random.choice(basic_totems_cpy)
                if rand_totem.name == strength_totem_token.name:
                    player.end_of_turn_effects.append(strength_totem_effect)
                elif rand_totem.name == healing_totem_token.name:
                    player.end_of_turn_effects.append(healing_totem_effect)
                player.board.append(rand_totem)
            else:
                player.mana += 2
                player.hero_power = True


class Warlock(HeroClass):
    def use_power(self, player, opponent, target):
        deal_damage(player, 2)
        player.draw()


class Player:
    def __init__(self, deck=None, renathal=False, hero_class: HeroClass = Mage(), starting_mana=0):
        self.max_health: int = 35 if renathal else 30
        self.health = self.max_health
        self.hero_class: HeroClass = hero_class
        self.hero_power: bool = True
        self.armor: int = 0
        self.mana: int = starting_mana
        self.max_mana: int = 0
        self.weapon: Weapon | None = None
        self.weapon_durability: int = 0
        self.attacked: bool = False
        # Treat attack as attack gained during a turn that is lost upon every new turn
        self.attack: int = 0
        self.fatigue: int = 0
        self.persistent_effects = None
        self.end_of_turn_effects: List[Callable] = []
        self.one_of_effects: List[Callable] = []
        self.hand: List[Card] = []
        # minions and locations. array is good enough. O(1) time
        self.board: List[Card] = []
        self.played: Dict[Card] = {}
        self.destroyed: Dict[Card] = {}
        self.deck: List[Card] = [
            card_factory(moonfire_card) for _ in range(30)] if deck is None else deck

    def take_damage(self, damage):
        if self.armor >= damage:
            self.armor -= damage
        else:
            self.health += self.armor - damage
            self.armor = 0

    def draw(self, amount=1):
        for _ in range(amount):
            if self.deck:
                if len(self.hand) < 10:
                    self.hand.append(self.deck.pop())
                else:
                    self.deck.pop()
            else:
                self.fatigue += 1
                self.take_damage(self.fatigue)
        if 'game' in locals():
            game.is_game_over(game.player1.health, game.player2.health)

    def play(self, card, card_index, opponent):
        self.mana -= card.cost
        popped_card: Card = self.hand.pop(card_index)
        popped_name = popped_card.name
        self.played[popped_name] = (self.played.get(
            popped_name, 0) + 1, game.current_turn)
        card.play(self, opponent)

    def use_hero_power(self, player=None, opponent=None, target=None):
        return self.hero_class.use_hero_power(self, opponent, target)


class Card:
    def __init__(self, cost, effect, name, description):
        self.name = name
        self.description = description
        self.cost = cost
        # effect for minions would be battlecry (it needs to survive to activate though)
        self.effect = effect

    def __str__(self):
        return self.name

    def play(self, player: Player, opponent: Player):
        player.played[self.name] = player.played.get(self.name, 0) + 1
        self.effect(player, opponent)


class Minion(Card):
    def __init__(self, cost, attack, health, effect, name, description, tribes: List[str] | None = None, deathrattles=[], taunt=False, charge=False):
        super().__init__(cost, effect, name, description)
        self.attack = attack
        self.max_health = health
        self.health = health
        self.deathrattles = [dr for dr in deathrattles]
        self.tribes = set(tribes) if tribes else None
        self.taunt = taunt
        self.charge = charge

    def __str__(self):
        return f'{self.name} [{self.attack}/{self.health}]'

    def play(self, player: Player, opponent: Player):
        # Adds minion to board first then plays effect. This helps with choose one effects that buff themselves.
        if not player.board:
            player.board.append(self)
        else:
            print("Choose where to play the minion.")
            n_possible = min(7, len(player.board) + 1)
            for i in range(n_possible - 1):
                print(i + 1, player.board[i].name, end=" ")
            print(n_possible)

            pos = input()
            try:
                pos = int(pos)
                player.board.insert(pos - 1, self)
            except ValueError:
                print("no bueno")

        super().play(player, opponent)


class Weapon(Card):
    def __init__(self, cost, effect, name, description, attack, durability):
        super().__init__(cost, effect, name, description)
        self.attack = attack
        self.durability = durability

    def play(self, player: Player, opponent: Player):
        player.weapon = self
        player.weapon_durability = self.durability


class Game:
    def __init__(self, p1_deck=None, p2_deck=None):
        self.player1 = Player(deck=p1_deck)
        self.player2 = Player(deck=p2_deck)
        self.current_turn: int = 0
        self.game_end = False
        random.shuffle(self.player1.deck)
        random.shuffle(self.player2.deck)

    def game_loop(self):
        self.player1.draw(3)
        self.player2.draw(4)
        self.player2.hand.append(coin_card)

        print(
            "Enter the card index of the cards you want to play one by one. ORDER MATTERS."
        )
        print("-------------------------------------------------")

        index = 1
        player, opponent = self.player1, self.player2
        while self.game_end == False:
            self.current_turn += 1
            self.turn(player, index, opponent)

            game_end, winner = self.is_game_over(
                self.player1.health, self.player2.health)
            if game_end:
                self.game_end == True
                break

            index = 2 if index == 1 else 1
            player, opponent = opponent, player

    def turn(self, player: Player, index: int, opponent: Player):
        print(f"Player {index}'s turn!")
        if player.max_mana < 10:
            player.max_mana += 1
        player.mana = min(10, player.max_mana)
        # reset hero power and attack
        player.hero_power = True
        player.attack = 0
        player.attacked = False
        player.draw()
        over, winner = game.is_game_over(
            game.player1.health, game.player2.health)
        if over:
            return

        # printing for debugging/interface
        print(f"Player {index} mana: {player.mana}/{player.max_mana}")
        self.print_hand(player)
        self.print_board()
        print(f"Player {index} HP: {player.health} ({player.armor} Armor)")
        print(
            f"Player {1 if index == 2 else 2} HP: {opponent.health} ({opponent.armor} Armor)")

        while True:
            card_index = input()

            if not card_index:
                break

            card_index = int(card_index) - 1
            # play cards instantly here rather than after all input

            if card_index == -1:
                if player.mana >= 2:
                    target = None
                    if isinstance(player.hero_class, Mage):
                        target = choose_target_any(player, opponent)
                    if isinstance(player.hero_class, Priest):
                        target = choose_target_any(player, opponent)

                    if player.use_hero_power(player=player, opponent=opponent,
                                             target=target):
                        destroyed_check(player, opponent)
                        self.print_hand(player)
                        self.print_board()
                else:
                    print("Not enough mana.")
            elif card_index == 10:
                if not player.attacked:
                    if player.attack > 0 or player.weapon:
                        target = choose_target_enemy(player, opponent)
                        deal_damage(target, player.attack +
                                    (player.weapon.attack if player.weapon else 0))
                        # check if target is Player object
                        if not hasattr(target, 'use_hero_power'):
                            deal_damage(player, target.attack)
                        player.weapon_durability = max(
                            0, player.weapon_durability - 1)
                        if player.weapon_durability == 0:
                            player.weapon == None
                        player.attacked = True
                        self.is_game_over(self.player1.health,
                                          self.player2.health)
                        destroyed_check(player, opponent)
                        self.print_hand(player)
                        self.print_board()
                        print(
                            f"Player {index} HP: {player.health} ({player.armor} Armor)")
                        print(
                            f"Player {1 if index == 2 else 2} HP: {opponent.health} ({opponent.armor} Armor)")

                else:
                    print(
                        "You already attacked.")
                pass
            elif 0 <= card_index < len(player.hand):
                card: Card = player.hand[card_index]
                if player.mana >= card.cost:
                    player.play(card=card, card_index=card_index,
                                opponent=opponent)
                    destroyed_check(player, opponent)
                    print(f"Current mana: {player.mana}/{player.max_mana}")
                    # print all cards again since card indices are different
                    self.print_hand(player)
                    self.print_board()
                    print(
                        f"Player {index} HP: {player.health} ({player.armor} Armor)")
                    print(
                        f"Player {1 if index == 2 else 2} HP: {opponent.health} ({opponent.armor} Armor)")
                else:
                    print("Not enough mana.")
            else:
                print("Not a valid card index.")
            game_over, winner = self.is_game_over(
                self.player1.health, self.player2.health)
            if game_over:
                break

        # call when turn ends
        for effect in player.end_of_turn_effects:
            effect(player, opponent)

        for effect in player.one_of_effects:
            effect()
        player.one_of_effects = []

    def print_board(self):
        print(
            f"Player 1 board: {', '.join(str(minion) for minion in self.player1.board)}")
        print(
            f"Player 2 board: {', '.join(str(minion) for minion in self.player2.board)}")
        print("-------------------------------------------------")

    @staticmethod
    def print_hand(player: Player):
        print(f"Current mana: {player.mana}/{player.max_mana}")
        print("Hand:")
        print(f"0. Hero Power {int(player.hero_power)}/1")
        for i, card in enumerate(player.hand):
            print(
                f"{i + 1}. {card}, {card.cost} MANA. {card.description}")
        if player.attack > 0 or player.weapon:
            print("11. Attack with hero.")

    @staticmethod
    def is_game_over(p1_health, p2_health):
        if p1_health < 1:
            print("Player 2 wins!")
            game.game_end == True
            return True, "Player2"
        if p2_health < 1:
            print("Player 1 wins!")
            game.game_end == True
            return True, "Player1"
        return False, None


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
    minion.taunt = True


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
        minion.taunt = True

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
        for minion in player.board:
            if minion.name == 'Druid of the Claw' and minion.attack == 4 and minion.health == 4:
                minion.charge = True

    def two():
        for minion in player.board:
            if minion.name == 'Druid of the Claw' and minion.attack == 4 and minion.health == 4:
                minion.taunt = True
                minion.max_health += 2
                minion.health = minion.max_health

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
    innervate_card,
    moonfire_card,
    claw_card,
    naturalize_card,
    savagery_card,
    mark_of_the_wild_card,
    power_of_the_wild_card,
    wild_growth_card,
    wrath_card,
    healing_touch_card,
    mark_of_nature_card,
    savage_roar_card,
    bite_card,
    keeper_of_the_grove_card,
    soul_of_the_forest_card,
    swipe_card,
    druid_of_the_claw_card,
    nourish_card,
    starfall_card,
    force_of_nature_card,
    starfire_card,
    ancient_of_lore_card,
    ancient_of_war_card,
    ironbark_prodector_card,
    cenarius_card,
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


if __name__ == "__main__":
    # decks are shuffled when the game starts
    p1_deck = generate_deck(cards)
    p2_deck = generate_deck(cards)
    game = Game(p1_deck=p1_deck, p2_deck=p2_deck)
    game.game_loop()
