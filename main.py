from cards import *


class Player:
    def __init__(self, deck=None, renathal=False):
        self.health = 35 if renathal else 30
        self.max_health = 35 if renathal else 30
        self.mana = 0
        self.max_mana = 0
        self.hand = []
        self.played = []
        self.deck = [moonfire_card for _ in range(30)] if deck is None else deck

    def draw(self, amount=1):
        for _ in range(amount):
            self.hand.append(self.deck.pop())

    def play(self, card_index, opponent):
        card: Card = self.hand[card_index]
        card.play(self, opponent)
        self.mana -= card.mana_cost
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
        player.mana = player.max_mana
        player.draw()
        print(f"Player {index} has {player.mana} mana crystals.")
        print("Your hand:")
        for i, card in enumerate(player.hand):
            print(f"{i + 1}. {card.name}")
        print(f"Player {index} HP: ", player.health)
        print(f"Player {1 if index == 2 else 2} HP: ", opponent.health)
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

        i = 0
        while i < len(to_play):
            # check if the card index is still valid. important
            if to_play[i] < len(player.hand):
                card: Card = player.hand[to_play[i]]
                if player.mana >= card.mana_cost:
                    player.play(card_index=to_play[i], opponent=opponent)
                    for j in range(i + 1, len(to_play)):
                        to_play[j] -= 1
            i += 1

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
    p2_deck = [innervate_card for _ in range(15)] + [starfire_card for _ in range(15)]
    game = Game(p1_deck=p1_deck, p2_deck=p2_deck)
    game.game_loop()
