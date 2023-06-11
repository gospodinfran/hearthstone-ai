class Player:
    def __init__(self, deck=None, renathal=False):
        self.health = 35 if renathal else 30
        self.mana = 0
        self.hand = []
        self.played = []
        self.deck = [Card(cost=2) for i in range(30)] if deck is None else deck

    def draw(self, amount=1):
        for _ in range(amount):
            self.hand.append(self.deck.pop())

    def play(self, card):
        # as complexity rises pop the specific card played
        # currently all of the cards are the same
        self.played.append(self.hand.pop())
        return card.damage


class Card:
    def __init__(self, cost, name="Frostbolt", damage=0, target=None):
        self.name = name
        self.mana_cost = cost
        self.damage = damage
        self.target = target


class Game:
    def __init__(self, p1_deck=None, p2_deck=None):
        self.player1 = Player(deck=p1_deck)
        self.player2 = Player(deck=p2_deck)

    def game_loop(self):
        game_end = False
        self.player1.draw(3)
        self.player2.draw(4)

        while not game_end:
            self.turn(player=self.player1, index=1)

            if self.player1.health < 1:
                print("Player 1 wins!")
                game_end = True
            if self.player2.health < 1:
                print("Player 2 wins!")
                game_end = True

            self.turn(player=self.player2, index=2)

            if self.player1.health < 1:
                print("Player 1 wins!")
                game_end = True
            if self.player2.health < 1:
                print("Player 2 wins!")
                game_end = True

    def turn(self, player, index):
        print(f"Player {index}'s turn!")
        if player.mana < 10:
            player.mana += 1
        player.draw()
        print(f"Player {index} has {player.mana} mana crystals.")
        print("Your hand:")
        for i, card in enumerate(player.hand):
            print(f"{i + 1}. {card.name}")
        print("Enter the card index of the cards you want to play one by one.")
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

        to_play.sort(reverse=True)
        for i in to_play:
            player.hand.pop(i)


if __name__ == "__main__":
    game = Game()
    game.game_loop()
