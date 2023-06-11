from cards import *


class Player:
    def __init__(self, deck=None, renathal=False):
        self.health = 35 if renathal else 30
        self.max_health = 35 if renathal else 30
        self.mana = 0
        self.hand = []
        self.played = []
        self.deck = [Card(cost=2) for i in range(30)] if deck is None else deck

    def draw(self, amount=1):
        for _ in range(amount):
            self.hand.append(self.deck.pop())

    def play(self, card_index, opponent):
        card: Card = self.hand[card_index]
        if self.mana >= card.mana_cost:
            card.play(self, opponent)
            self.played.append(self.hand.pop(card_index))


class Card:
    def __init__(self, cost, effect, name="Frostbolt"):
        self.name = name
        self.mana_cost = cost
        self.effect = effect

    def play(self, player, opponent):
        self.effect(player, opponent)


class Game:
    def __init__(self, p1_deck=None, p2_deck=None):
        self.player1 = Player(deck=p1_deck)
        self.player2 = Player(deck=p2_deck)

    def game_loop(self):
        game_end = False
        self.player1.draw(3)
        self.player2.draw(4)

        print(
            "Enter the card index of the cards you want to play one by one. ORDER MATTERS."
        )

        while not game_end:
            self.turn(player=self.player1, index=1, opponent=self.player2)

            if self.game_over(self.player1.health, self.player2.health):
                game_end = True

            self.turn(player=self.player2, index=2, opponent=self.player1)

            if self.game_over(self.player1.health, self.player2.health):
                game_end = True

    def turn(self, player: Player, index: int, opponent: Player):
        print(f"Player {index}'s turn!")
        if player.mana < 10:
            player.mana += 1
        player.draw()
        print(f"Player {index} has {player.mana} mana crystals.")
        print("Your hand:")
        for i, card in enumerate(player.hand):
            print(f"{i + 1}. {card.name}")
        print("Player 1 HP: ", player.health)
        print("Player 2 HP: ", opponent.health)
        print()
        to_play = []
        while True:
            card_index = input()
            if not card_index:
                break
            try:
                card_index = int(card_index) - 1
                if 0 <= card_index < len(player.hand):
                    to_play.append(card_index)
            except ValueError:
                print(
                    "Invalid input. Please enter a valid card index or press Enter to skip your turn."
                )

        for i in to_play:
            # this maintains playing order
            for j in range(i + 1, len(to_play)):
                to_play[j] -= 1
            player.play(card_index=i, opponent=opponent)

    def game_over(p1_health, p2_health):
        if p1_health < 1:
            print("Player 2 wins!")
            return True
        if p2_health < 1:
            print("Player 1 wins!")
            return True


if __name__ == "__main__":
    p1_deck = get_random_deck()
    p2_deck = get_random_deck()
    game = Game(p1_deck=p1_deck, p2_deck=p2_deck)
    game.game_loop()
