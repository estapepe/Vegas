import random


class ExperimentSet:

    def __init__(self, experiments):
        """
        @type self: list[Experiment]
        """
        self.experiments = experiments

    def execute(self):
        for experiment in self.experiments:
            experiment.execute()


class Experiment:
    ALPHA = 1

    def __init__(self, replicate_cardinality, configuration):
        self.replicate_cardinality = replicate_cardinality
        self.configuration = configuration

    def execute(self):
        for i in range(self.replicate_cardinality):
            current_game = self.initialize_game()
            current_game.play()

    def initialize_game(self) -> Game:
        if self.configuration == self.ALPHA:
            alpha = Player(Player.ALPHA, 5)
            bravo = Player(Player.BRAVO, 4)
            charlie = Player(Player.CHARLIE, 3)
            delta = Player(Player.DELTA, 2)
            echo = Player(Player.ECHO, 1)
            players = [alpha, bravo, charlie, delta, echo]
            game = Game(players)
        else:
            raise UnknownConfigurationException()
        return game


class Player:
    ALPHA = "alpha"
    BRAVO = "bravo"
    CHARLIE = "charlie"
    DELTA = "delta"
    ECHO = "echo"

    def __init__(self, call_sign, age):
        self.call_sign = call_sign
        self.age = age


class Casino:
    def __init__(self, call_sign):
        self.call_sign = call_sign
        self.dice = []


class Game:
    def __init__(self, players: list[Player]):
        self.players = players
        self.players.sort(key=lambda player: player.age)
        self.banknotes = self.initialize_banknotes()
        self.casinos = self.initialize_casinos()

    def initialize_banknotes(self) -> list:
        self.banknotes = []
        for i in range(5):
            self.banknotes.append(60000)
            self.banknotes.append(70000)
            self.banknotes.append(80000)
            self.banknotes.append(90000)
        for i in range(6):
            self.banknotes.append(10000)
            self.banknotes.append(40000)
            self.banknotes.append(50000)
        for i in range(8):
            self.banknotes.append(20000)
            self.banknotes.append(30000)
        random.shuffle(self.banknotes)

    def initialize_casinos(self) -> list:


    def play(self):
        for player in self.players:
            self.roll_dice(player)
            self.place_dice(player)


class Die:
    def __init__(self, cardinality, color):
        self.color = color
        self.upper_surface = random.randint(1, cardinality)


class UnknownConfigurationException(Exception):
    pass
