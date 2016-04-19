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
    ALPHA = "alpha"
    BETA = "beta"

    def __init__(self, replicate_cardinality, configuration):
        self.replicate_cardinality = replicate_cardinality
        self.configuration = configuration

    def execute(self):
        for i in range(self.replicate_cardinality):
            current_game = self.initialize_game()
            current_game.play()

    def initialize_game(self):
        # The ALPHA experiment: 5 players, a different heuristic for each.
        if self.configuration == self.ALPHA:
            players = [Player.ALPHA, Player.BRAVO, Player.CHARLIE, Player.DELTA, Player.DELTA]
            game = Game(players)
        # The BETA experiment: 5 players, all using the ALPHA heuristic.
        elif self.configuration == self.BETA:
            players = [Player.ALPHA, Player.ALPHA, Player.ALPHA, Player.ALPHA, Player.ALPHA]
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

    def __init__(self, call_sign, age, dice: list):
        self.call_sign = call_sign
        self.age = age
        self.dice = dice

    def roll_dice(self):
        for die in self.dice:
            die.roll()

    def relinquish_dice(self, casinos):
        # Player has no dice.
        if not self.dice:
            return {}

        # The ALPHA heuristic: Choose to bet the maximum amount of dice (the biggest dice set).
        if self.call_sign == self.ALPHA:
            return self.alpha()
        # The BRAVO heuristic: Choose to bet to the casino with the highest prize.
        elif self.call_sign == self.BRAVO:
            return {}
        # The CHARLIE heuristic: Choose to bet to the casino with the most prizes.
        elif self.call_sign == self.CHARLIE:
            return {}
        # The DELTA heuristic: Choose to outnumber an opponent. Which opponent? In which casino?
        elif self.call_sign == self.DELTA:
            return {}
        # The ECHO heuristic: Choose to tie an opponent. Which opponent? In which casino?
        else:
            # Random: Return a random set of dice.
            return {}

    def alpha(self):
        # Group the dice by top face.
        dice_sets = []
        for i in range(1, 7):
            current_set = []
            for die in self.dice:
                if die.top_face == i:
                    current_set.append(die)
            if current_set:
                dice_sets.append(current_set)
        print("Dice sets: ")
        print(dice_sets)

        # Get the size of the biggest group, there might be two or more groups with the same size.
        biggest_die_set_cardinality = 0
        for dice_set in dice_sets:
            if biggest_die_set_cardinality < len(dice_set):
                biggest_die_set_cardinality = len(dice_set)
        print("biggest_die_set_cardinality: " + str(biggest_die_set_cardinality))

        # Keep only the biggest group (or groups).
        choices = []
        for dice_set in dice_sets:
            if len(dice_set) == biggest_die_set_cardinality:
                choices.append(dice_set)
        print("Choices: ")
        print(choices)

        # From the biggest groups, choose at random.
        choice = choices[random.randint(0, len(choices)-1)]
        print("Player chose:")
        print(choice)

        # Give up the chosen dice.
        for die in choice:
            self.dice.remove(die)

        print("Player was left with: ")
        print(self.dice)
        print("------------------------------------------------")
        return choice


class Casino:
    def __init__(self, call_sign: int, prizes: list):
        self.call_sign = call_sign
        self.dice = []
        prizes.sort(reverse=True)
        self.prizes = prizes

    def get_prizes(self):
        # Group the dice by color.
        dice_sets = []
        for color in Game.DICE_COLORS:
            current_set = []
            for die in self.dice:
                if die.color == color:
                    current_set.append(die)
            if current_set:
                dice_sets.append(current_set)
        dice_sets.sort(key=len, reverse=True)
        prizes = []
        for dice_set in dice_sets:
            if self.prizes:
                prize = [self.prizes.pop(), dice_set]
                prizes.append(prize)
        print("Prized sets: ")
        print(prizes)
        return prizes

    def __repr__(self):
        call_sign = "Casino " + str(self.call_sign) + ":\n"
        prizes = str(self.prizes) + "\n"
        dice = str(self.dice)
        return  call_sign + prizes + str(self.dice)


class Game:
    DICE_COLORS = ["blue", "white", "black", "red", "green"]

    def __init__(self, call_signs: list):
        self.player_colors = {}
        self.players = []
        self.initialize_players(call_signs)
        self.banknotes = []
        self.initialize_banknotes()
        self.casinos = []
        self.initialize_casinos()

    def initialize_banknotes(self):
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

    def initialize_casinos(self):
        self.casinos = []
        for i in range(6):
            prizes = []
            while sum(prizes) < 50000:
                prizes.append(self.banknotes.pop())
            self.casinos.append(Casino(i+1, prizes))

    def initialize_players(self, call_signs):
        self.players = []
        i = 1
        for call_sign in call_signs:
            color = self.DICE_COLORS[i-1]
            self.players.append(Player(call_sign, i, self.initialize_dice_set(color)))
            self.player_colors[call_sign] = self.DICE_COLORS[i-1]
            i += 1
        self.players.sort(key=lambda player: player.age)

    @staticmethod
    def initialize_dice_set(color):
        dice = []
        faces = range(1, 7)
        for i in range(8):
            dice.append(Die(faces, color))
        return dice

    def play(self):
        while not self.is_all_players_dice_depleted():
            for player in self.players:
                player.roll_dice()
                self.place_dice(player)
        self.award_banknotes()
        self.declare_winner()

    def place_dice(self, player: Player):
        if player.dice:
            dice = player.relinquish_dice(self.casinos)
            for die in dice:
                self.casinos[die.top_face-1].dice.append(die)

    def is_all_players_dice_depleted(self) -> bool:
        dice_counts = []
        for player in self.players:
            dice_counts.append(len(player.dice))
        return sum(dice_counts) == 0

    def award_banknotes(self):
        for casino in self.casinos:
            print(casino)
            casino.get_prizes()


class Die:
    def __init__(self, faces, color):
        self.color = color
        self.faces = faces
        self.top_face = random.choice(self.faces)

    def roll(self):
        self.top_face = random.choice(self.faces)

    def __repr__(self):
        return self.color + ":" + str(self.top_face)


class UnknownConfigurationException(Exception):
    pass
