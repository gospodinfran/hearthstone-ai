# Hearthstone State Implementation

Currently all of the code, except for unit tests, is found inside main.py until a complete refactor which is planned in the very near future.

## Game state 

Hearthstone game loop state logic found in _main.py_, along with Player, Minion, Weapon and Card classes which encapsulate all data needed to reproduce a 1-to-1 state as that of the collectible card-game (CCG) Hearthstone. Run main.py to start the CLI:
```python
python3 main.py
```

## Cards

Card effects are created with the command design pattern and instantiated with a card factory for every unique instance that exists.

## Unit tests

Unit tests written for the Player class. Tests are currently very fast (0.000s avg over 10 iterations). Run the tests with:
```python
python3 tests.py
```

## Using the CLI

Player options appear as 0-indexed numbers which are sorted in the CLI. If you want to play an action input the corresponding number and click enter on the keyboard. If prompted again, e.g. to choose a target, input a number and click enter. When the player is done with his turn, he can click enter with no prior input to end his turn. 