from typing import List, Dict, Callable
from cards import *
from testing import get_random_deck
import random


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
            player.board.append(silver_hand_recruit)


class Druid(HeroClass):
    def use_power(self, player, opponent, target):
        player.armor += 1
        player.attack += 1


class Rogue(HeroClass):
    def use_power(self, player, opponent, target):
        # TODO make rogue weapon
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
        player.health -= 2
        player.draw()


class Player:
    def __init__(self, deck=None, renathal=False, hero_class: HeroClass = Shaman()):
        self.health: int = 35 if renathal else 30
        self.max_health: int = 35 if renathal else 30
        self.hero_class: HeroClass = hero_class
        self.hero_power: bool = True
        self.armor: int = 0
        self.mana: int = 0
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
            moonfire_card for _ in range(30)] if deck is None else deck

    def draw(self, amount=1):
        for _ in range(amount):
            if self.deck:
                if len(self.hand) < 10:
                    self.hand.append(self.deck.pop())
                else:
                    self.deck.pop()
            else:
                self.fatigue += 1
                self.health -= self.fatigue

    def play(self, card, card_index, opponent):
        self.mana -= card.cost
        popped_card: Card = self.hand.pop(card_index)
        popped_name = popped_card.name
        self.played[popped_name] = self.played.get(popped_name, 0) + 1
        card.play(self, opponent)

    def take_damage(self, damage):
        if self.armor >= damage:
            self.armor -= damage
        else:
            self.health += self.armor - damage
            self.armor = 0

    def use_hero_power(self, player=None, opponent=None, target=None):
        return self.hero_class.use_hero_power(self, opponent, target)


class Card:
    def __init__(self, cost, effect, name, description):
        self.name = name
        self.description = description
        self.cost = cost
        # effect for minions would be battlecry (it needs to survive to activate though)
        self.effect = effect

    def play(self, player: Player, opponent: Player):
        player.played[self.name] = player.played.get(self.name, 0) + 1
        self.effect(player, opponent)


class Minion(Card):
    def __init__(self, cost, attack, health, effect, name, description, tribes: List[str] | None = None, deathrattles=[]):
        super().__init__(cost, effect, name, description)
        self.attack = attack
        self.max_health = health
        self.health = health
        self.deathrattles = [dr for dr in deathrattles]
        self.tribes = set(tribes) if tribes else None

    def play(self, player: Player, opponent: Player):
        super().play(player, opponent)
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
        random.shuffle(self.player1.deck)
        random.shuffle(self.player2.deck)

    def game_loop(self):
        game_end = False
        self.player1.draw(3)
        self.player2.draw(4)
        self.player2.hand.append(coin_card)

        print(
            "Enter the card index of the cards you want to play one by one. ORDER MATTERS."
        )
        print("-------------------------------------------------")

        while not game_end:
            self.turn(player=self.player1, index=1, opponent=self.player2)

            game_end, winner = self.is_game_over(
                self.player1.health, self.player2.health)
            if game_end:
                return winner

            self.turn(player=self.player2, index=2, opponent=self.player1)

            game_end, winner = self.is_game_over(
                self.player1.health, self.player2.health)
            if game_end:
                return winner

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
                        self.is_game_over(player.health, opponent.health)
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
                        self.is_game_over(player.health, opponent.health)
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

        # call when turn ends
        for effect in player.end_of_turn_effects:
            effect(player, opponent)

        for effect in player.one_of_effects:
            effect()
        player.one_of_effects = []

    def print_board(self):
        print(
            f"Player 1 board: {', '.join(f'{card.name} [{card.attack}/{card.health}]' for card in self.player1.board)}")
        print(
            f"Player 2 board: {', '.join(f'{card.name} [{card.attack}/{card.health}]'for card in self.player2.board)}")
        print("-------------------------------------------------")

    @staticmethod
    def print_hand(player: Player):
        print(f"Current mana: {player.mana}/{player.max_mana}")
        print("Hand:")
        print(f"0. Hero Power {int(player.hero_power)}/1")
        for i, card in enumerate(player.hand):
            print(
                f"{i + 1}. {card.name}, {card.cost} MANA. {card.description}")
        if player.attack > 0 or player.weapon:
            print("11. Attack with hero.")

    @staticmethod
    def is_game_over(p1_health, p2_health):
        if p1_health < 1:
            print("Player 2 wins!")
            return True, "Player2"
        if p2_health < 1:
            print("Player 1 wins!")
            return True, "Player1"
        return False, None


if __name__ == "__main__":
    # decks are shuffled when the game starts
    p1_deck = generate_deck(cards)
    p2_deck = generate_deck(cards)
    game = Game(p1_deck=p1_deck, p2_deck=p2_deck)
    game.game_loop()
