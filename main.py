from cards import *
from typing import List, Dict

class Player:
    def __init__(self, deck=None, renathal=False):
        self.health = 35 if renathal else 30
        self.max_health = 35 if renathal else 30
        self.armor = 0
        self.mana = 0
        self.max_mana = 0
        self.weapon = None
        self.weapon_durability = 0
        self.attack = 0
        self.fatigue = 0
        self.hand: List[Card] = []
        self.board: List[Card] = [] # minions and locations. array is good enough. O(1) time
        self.played: Dict[Card] = {}
        self.deck: List[Card] = [moonfire_card for _ in range(30)] if deck is None else deck

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
        popped_card:Card = self.hand.pop(card_index)
        popped_name = popped_card.name
        self.played[popped_name] = self.played.get(popped_name, 0) + 1


class Card:
    def __init__(self, cost, effect, name, description):
        self.name = name
        self.description = description
        self.mana_cost = cost
        self.effect = effect # effect for minions would be battlecry (it needs to survive to activate though)

    def play(self, player, opponent):
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
            n_possible = min(7, len(player.board) + 1 )
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

        print(
            "Enter the card index of the cards you want to play one by one. ORDER MATTERS."
        )

        while not game_end:
            self.turn(player=self.player1, index=1, opponent=self.player2)

            game_end, winner = self.game_over(self.player1.health, self.player2.health)
            if game_end:
                return winner

            self.turn(player=self.player2, index=2, opponent=self.player1)

            game_end, winner = self.game_over(self.player1.health, self.player2.health)
            if game_end:
                return winner

    def turn(self, player: Player, index: int, opponent: Player):
        print(f"Player {index}'s turn!")
        if player.max_mana < 10:
            player.max_mana += 1
        player.mana = min(10, player.max_mana)
        player.attack = 0
        player.draw()

        # printing for debugging 
        print(f"Player {index} mana: {player.mana}/{player.max_mana}")
        print("Your hand:")
        for i, card in enumerate(player.hand):
            print(f"{i + 1}. {card.name}, {card.mana_cost} Mana. {card.description}")
        self.print_board()
        print(f"Player {index} HP: ", player.health)
        print(f"Player {1 if index == 2 else 2} HP: ", opponent.health)
        
        while True:
            card_index = input()
            if not card_index:
                break
            try:
                card_index = int(card_index) - 1

                # play cards instantly here rather than after all input
                if card_index < len(player.hand):
                    card: Card = player.hand[card_index]
                    if player.mana >= card.mana_cost:
                        player.play(card=card, card_index=card_index, opponent=opponent)
                        print(f"Current mana: {player.mana}/{player.max_mana}")
                        # print all cards again since card indices are different
                        print("Your hand:")
                        for i, card in enumerate(player.hand):
                            print(f"{i + 1}. {card.name}, {card.mana_cost} MANA. {card.description}")
                        self.print_board()
                    else:
                        print("Not enough mana.")
                else:
                    print("Not a valid card index.")

                

            except ValueError:
                print(
                    "Invalid input. Please enter a valid card index or press Enter to skip your turn."
                )

    def print_board(self):
        print(f"Player1 board: {', '.join(card.name for card in self.player1.board)}")
        print(f"Player2 board: {', '.join(card.name for card in self.player2.board)}")

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
