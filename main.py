from cards import *
from typing import List, Dict


class Player:
    def __init__(self, deck=None, renathal=False, hero_class="mage"):
        self.health = 35 if renathal else 30
        self.max_health = 35 if renathal else 30
        self.hero_class = hero_class
        self.hero_power = True
        self.armor = 0
        self.mana = 0
        self.max_mana = 0
        self.weapon = None
        self.weapon_durability = 0
        self.attack = 0
        self.fatigue = 0
        self.hand: List[Card] = []
        # minions and locations. array is good enough. O(1) time
        self.board: List[Card] = []
        self.played: Dict[Card] = {}
        self.destroyed: Dict[Card] = {}
        self.deck: List[Card] = [
            moonfire_card for _ in range(30)] if deck is None else deck

    def draw(self, amount=1):
        if self.deck:
            for _ in range(amount):
                if len(self.hand) < 10:
                    self.hand.append(self.deck.pop())
                else:
                    self.deck.pop()
        else:
            self.fatigue += 1
            self.health -= self.fatigue

    def play(self, card, card_index, opponent):
        # TODO, pass down card for effects like enrage, bloodsail raider, etc.
        if card.play(self, opponent) == False:
            return

        self.mana -= card.mana_cost
        popped_card: Card = self.hand.pop(card_index)
        popped_name = popped_card.name
        self.played[popped_name] = self.played.get(popped_name, 0) + 1

    def use_hero_power(self, target=None):
        # TODO
        if self.hero_power:
            if self.mana >= 2:
                if self.hero_class == "mage":
                    target.health -= 1
                self.hero_power = False
                print("Hero power used.")
                return True
            else:
                print("Not enough mana.")
        else:
            print("Hero power already used.")
        return


class Card:
    def __init__(self, cost, effect, name, description):
        self.name = name
        self.description = description
        self.mana_cost = cost
        # effect for minions would be battlecry (it needs to survive to activate though)
        self.effect = effect

    def play(self, player: Player, opponent: Player):
        player.played[self.name] = player.played.get(self.name, 0) + 1
        if self.effect(player, opponent) is not None:
            return False


class Minion(Card):
    def __init__(self, cost, attack, health, effect, name, description):
        super().__init__(cost, effect, name, description)
        self.attack = attack
        self.health = health

    def play(self, player: Player, opponent: Player):
        super().play(player, opponent)
        # TODO: cannot play if boardsize is 7
        if not player.board:
            player.board.append(self)
        else:
            print("Choose where to play the minion.")
            n_possible = min(7, len(player.board) + 1)
            board_copy: List[Card] = player.board
            for i in range(n_possible - 1):
                print(i + 1, board_copy[i].name, end=" ")
            print(n_possible)

            pos = input()
            try:
                pos = int(pos)
                player.board.insert(pos - 1, self)
            except ValueError:
                print("no bueno")


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

            game_end, winner = self.game_over(
                self.player1.health, self.player2.health)
            if game_end:
                return winner

            self.turn(player=self.player2, index=2, opponent=self.player1)

            game_end, winner = self.game_over(
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
        player.attack = 0
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
            try:
                card_index = int(card_index) - 1
                # play cards instantly here rather than after all input

                if card_index == -1:
                    target = choose_target_enemy(player, opponent)
                    if player.use_hero_power(
                            target=target):
                        destroyed_check_enemy(player, opponent, target)
                        self.print_hand(player)
                        self.print_board()
                elif card_index == 10:
                    if player.attack > 0:
                        target = choose_target_enemy(player, opponent)
                        if isinstance(target, Minion):
                            player.health -= target.attack
                        target.health -= player.attack
                        player.weapon_durability = max(
                            0, player.weapon_durability - 1)
                        self.print_hand(player)
                        self.print_board()

                    else:
                        print(
                            "Your hero doesn't have any attack or a weapon equipped.")
                    pass
                elif 0 <= card_index < len(player.hand):
                    card: Card = player.hand[card_index]
                    if player.mana >= card.mana_cost:
                        player.play(card=card, card_index=card_index,
                                    opponent=opponent)
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

            except ValueError:
                print(
                    "Invalid input. Please enter a valid card index or press Enter to skip your turn."
                )

    def print_board(self):
        print(
            f"Player 1 board: {', '.join(card.name for card in self.player1.board)}")
        print(
            f"Player 2 board: {', '.join(card.name for card in self.player2.board)}")
        print("-------------------------------------------------")

    def print_hand(self, player: Player):
        print(f"0. Hero Power {int(player.hero_power)}/1")
        print("Hand:")
        for i, card in enumerate(player.hand):
            print(
                f"{i + 1}. {card.name}, {card.mana_cost} MANA. {card.description}")
        if player.attack > 0:
            print("11. Attack with hero.")

    def game_over(self, p1_health, p2_health):
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
