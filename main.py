from cards import *
from typing import List, Dict


class HeroClass():
    def use_hero_power(self, player=None, opponent=None, target=None):
        if player.hero_power and player.mana >= 2:
            self.use_power(player, opponent, target)
            player.hero_power = False
            print("Hero power used.")
            return True
        else:
            print("Hero power already used or not enough mana.")

    def use_power(self, player=None, opponent=None, target=None):
        raise NotImplementedError("This method should be overriden.")


class Mage(HeroClass):
    def use_power(self, player, opponent, target):
        target.health -= 1


class Warrior(HeroClass):
    def use_power(self, player, opponent, target):
        player.armor += 2


class Priest(HeroClass):
    def use_power(self, player, opponent, target):
        # TODO, implement base stats for all minions because heals can't go over base health
        if isinstance(target, Player):
            target.health = min(target.max_health, target.health + 2)


class Hunter(HeroClass):
    def use_power(self, player, opponent, target):
        opponent.health -= 2


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
        player.attack = 1
        player.weapon_durability = 2
        player.weapon = True


class Shaman(HeroClass):
    def use_power(self, player, opponent, target):
        if len(player.board) < 7:
            # TODO, implement all 4 shaman token hero power minions
            # silver hand recruit as placeholder
            player.board.append(silver_hand_recruit)


class Warlock(HeroClass):
    def use_power(self, player, opponent, target):
        player.health -= 2
        player.draw()


class Player:
    def __init__(self, deck=None, renathal=False, hero_class: HeroClass = Paladin()):
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
        self.attack: int = 0
        self.fatigue: int = 0
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
        self.mana -= card.mana_cost
        popped_card: Card = self.hand.pop(card_index)
        popped_name = popped_card.name
        self.played[popped_name] = self.played.get(popped_name, 0) + 1
        card.play(self, opponent)

    def use_hero_power(self, player=None, opponent=None, target=None):
        self.hero_class.use_hero_power(self, opponent, target)


class Card:
    def __init__(self, cost, effect, name, description):
        self.name = name
        self.description = description
        self.mana_cost = cost
        # effect for minions would be battlecry (it needs to survive to activate though)
        self.effect = effect

    def play(self, player: Player, opponent: Player):
        player.played[self.name] = player.played.get(self.name, 0) + 1
        self.effect(player, opponent)


class Minion(Card):
    def __init__(self, cost, attack, health, effect, name, description, tribes: List | None = None):
        super().__init__(cost, effect, name, description)
        self.attack = attack
        self.health = health
        self.tribes = None if not tribes else set(tribes)

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
        player.attack += self.attack


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
        # reset hero power
        player.hero_power = True
        player.attack = 0 if not player.weapon else player.weapon.attack
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
                        target = choose_target_enemy(player, opponent)
                    if isinstance(player.hero_class, Priest):
                        # TODO, allow targeting of own units, not just enemy via choose_target_enemy
                        # This is placeholder until then. Heals self
                        target = player

                    # True if used, False if not used
                    if player.use_hero_power(player=player, opponent=opponent,
                                             target=target):
                        destroyed_check(player, opponent)
                        self.is_game_over(player.health, opponent.health)
                        self.print_hand(player)
                        self.print_board()
                else:
                    print("Not enough mana.")
            elif card_index == 10:
                if player.attack > 0 and not player.attacked:
                    target = choose_target_enemy(player, opponent)
                    target.health -= player.attack
                    if not isinstance(target, Player):
                        # BUG: player never takes damage for some reason
                        player.health -= target.attack
                        print(f"target attack:{target.attack}")
                        print(f"target health: {target.health}")
                        print(f"target name: {target.name}")
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
                if player.mana >= card.mana_cost:
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

    def print_board(self):
        print(
            f"Player 1 board: {', '.join(card.name for card in self.player1.board)}")
        print(
            f"Player 2 board: {', '.join(card.name for card in self.player2.board)}")
        print("-------------------------------------------------")

    @staticmethod
    def print_hand(player: Player):
        print(f"Current mana: {player.mana}/{player.max_mana}")
        print("Hand:")
        print(f"0. Hero Power {int(player.hero_power)}/1")
        for i, card in enumerate(player.hand):
            print(
                f"{i + 1}. {card.name}, {card.mana_cost} MANA. {card.description}")
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
    p1_deck = get_random_deck()
    p2_deck = get_random_deck()
    game = Game(p1_deck=p1_deck, p2_deck=p2_deck)
    game.game_loop()
