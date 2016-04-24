import random
import uuid
from typing import List
from typing import Set


class Casino:
    def __init__(self, call_sign: int, banknotes: list):
        self.call_sign = call_sign
        self.dice = []
        banknotes.sort(reverse=True)
        self.banknotes = banknotes

    def get_banknotes(self):
        return self.banknotes

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
            if self.banknotes:
                prize = Prize(dice_set, self.banknotes.pop())
                prizes.append(prize)
        return prizes

    def __repr__(self):
        call_sign = "Casino " + str(self.call_sign) + ":\n"
        prizes = str(self.banknotes) + "\n"
        dice = str(self.dice)
        return call_sign + prizes + dice


class Die:
    def __init__(self, faces, color):
        self.color = color
        self.faces = faces
        self.top_face = random.choice(self.faces)
        self.owner_id = None

    def __repr__(self):
        return self.color + ":" + str(self.top_face)

    def get_owner_id(self):
        return self.owner_id

    def roll(self):
        self.top_face = random.choice(self.faces)

    def set_owner(self, owner_id):
        self.owner_id = owner_id


class Experiment:
    ALPHA = "alpha"
    BETA = "beta"
    GAMMA = "gamma"

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
        # The GAMMA experiment: 5 players, all using the DELTA heuristic.
        elif self.configuration == self.GAMMA:
            players = [Player.DELTA, Player.DELTA, Player.DELTA, Player.DELTA, Player.DELTA]
            game = Game(players)
        else:
            raise UnknownConfigurationException()
        return game


class ExperimentSet:

    def __init__(self, experiments: List[Experiment]):
        self.experiments = experiments

    def execute(self):
        for experiment in self.experiments:
            experiment.execute()


class Prize:
    def __init__(self, dice: List[Die], banknote):
        self.dice = dice
        self.banknote = banknote

    def get_dice_owner(self):
        if self.dice:
            return self.dice[0].get_owner_id()


class Player:
    ALPHA = "alpha"
    BRAVO = "bravo"
    CHARLIE = "charlie"
    DELTA = "delta"
    ECHO = "echo"

    def __init__(self, call_sign, age, dice: List[Die]):
        self.call_sign = call_sign
        self.age = age
        self.id = uuid.uuid1()
        for die in dice:
            die.set_owner(self.id)
        self.dice = dice
        self.prize = None

    def __repr__(self):
        return self.call_sign + " " + str(self.get_id()) + " " + str(self.get_prize_amount())

    def get_dices_grouped_by_top_face(self):
        dice_sets = []
        for i in range(1, 7):
            current_set = []
            for die in self.dice:
                if die.top_face == i:
                    current_set.append(die)
            if current_set:
                dice_sets.append(current_set)
        return dice_sets

    def alpha(self):
        # The ALPHA heuristic: Choose to bet the maximum amount of dice (the biggest dice set).

        dice_sets = self.get_dices_grouped_by_top_face()

        # Get the size of the biggest group, there might be two or more groups with the same size.
        biggest_die_set_cardinality = 0
        for dice_set in dice_sets:
            if biggest_die_set_cardinality < len(dice_set):
                biggest_die_set_cardinality = len(dice_set)

        # Keep only the biggest group (or groups).
        choices = []
        for dice_set in dice_sets:
            if len(dice_set) == biggest_die_set_cardinality:
                choices.append(dice_set)

        # From the biggest groups, choose at random.
        choice = choices[random.randint(0, len(choices)-1)]

        # Give up the chosen dice.
        for die in choice:
            self.dice.remove(die)

        return choice

    def delta(self, casinos, opponents):
        # The DELTA heuristic: Choose to outnumber an opponent.
        dice_sets = self.get_dices_grouped_by_top_face()

        # Choices in this case is the dice_sets with which I outnumber if someone.
        choices = []
        for casino in casinos:
            for dice_set in dice_sets:
                if dice_set[0].top_face == casino.call_sign:
                    number_of_dice_in_casino = self.get_number_of_dice_in_casino(casino)
                    number_of_dice_that_can_be_put = len(dice_set)
                    number_of_dice_would_have = number_of_dice_in_casino + number_of_dice_that_can_be_put
                    for opponent in opponents:
                        if opponent.get_number_of_dice_in_casino() < number_of_dice_would_have:
                            choices = dice_set

        # Which opponent to outnumber? In which casino?
        # Any opponent in the the casino with the highest prize:
        which_casino = Player.get_call_sign_of_the_casino_with_the_highest_prize(casinos)
        choice = None
        for chosen_set in choices:
            if chosen_set[0].top_face == which_casino:
                choice = chosen_set
                break

        # If I can outnumber none (in the the casino with the highest prize), choose at random from my dice sets.
        if not choices:
            choice = dice_sets[random.randint(0, len(dice_sets)-1)]

        # Give up the chosen dice.
        for die in choice:
            self.dice.remove(die)

        return choice

    @staticmethod
    def get_call_sign_of_the_casino_with_the_highest_prize(casinos):
        higher_prize = 0
        which_casino = 0
        for casino in casinos:
            if higher_prize < casino.get_banknotes()[0]:
                higher_prize = casino.get_banknotes()[0]
                which_casino = casino.call_sign
        return which_casino

    def get_number_of_dice_in_casino(self, casino):
        this_players_dice = []
        for die in casino.dice:
            if die.get_owner_id() == self.get_id():
                this_players_dice.append(die)
        return len(this_players_dice)

    def get_id(self):
        return self.id

    def get_prize_amount(self):
        amount = 0
        if self.prize:
            amount = self.prize.banknote
        return amount

    def roll_dice(self):
        for die in self.dice:
            die.roll()

    def relinquish_dice(self, casinos, opponents):
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
            return self.delta(casinos, opponents)
        # The ECHO heuristic: Choose to tie an opponent. Which opponent? In which casino?
        else:
            # Random: Return a random set of dice.
            return {}

    def set_prize(self, prize: Prize):
        self.prize = prize


class Game:
    DICE_COLORS = ["blue", "white", "black", "red", "green"]

    def __init__(self, call_signs: list):
        self.players = set([])  # type: Set[Player]
        self.initialize_players(call_signs)
        self.banknotes = []
        self.initialize_banknotes()
        self.casinos = []
        self.initialize_casinos()

    def award_banknotes(self):
        prizes = []
        for casino in self.casinos:
            prizes.extend(casino.get_prizes())
        for prize in prizes:
            self.get_player(prize.get_dice_owner()).set_prize(prize)

    def declare_winner(self):
        highest_banknote = 0
        winner = None
        for player in self.players:
            if player.get_prize_amount() > highest_banknote:
                winner = player
        print("The winner is: " + str(winner))

    def get_player(self, player_id):
        for player in self.players:
            if player.get_id() == player_id:
                return player

    def get_player_opponents(self, player):
        opponents = []
        for opponent in self.players:
            if opponent.get_id() == player.get_id:
                opponents.append(opponent)
        return opponents

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
            banknotes = []
            while sum(banknotes) < 50000:
                banknotes.append(self.banknotes.pop())
            self.casinos.append(Casino(i+1, banknotes))

    @staticmethod
    def initialize_dice_set(color):
        dice = []
        faces = range(1, 7)
        for i in range(8):
            dice.append(Die(faces, color))
        return dice

    def initialize_players(self, call_signs):
        self.players = []
        i = 1
        for call_sign in call_signs:
            color = self.DICE_COLORS[i-1]
            player = Player(call_sign, i, self.initialize_dice_set(color))
            self.players.append(player)
            i += 1

    def is_all_players_dice_depleted(self) -> bool:
        dice_counts = []
        for player in self.players:
            dice_counts.append(len(player.dice))
        return sum(dice_counts) == 0

    def place_dice(self, player: Player):
        if player.dice:
            dice = player.relinquish_dice(self.casinos, self.get_player_opponents(player))
            for die in dice:
                self.casinos[die.top_face-1].dice.append(die)

    def play(self):
        # self.players.sort(key=lambda player: player.age)
        i = 0
        while not self.is_all_players_dice_depleted():
            print("Ronda " + str(i) + ":")
            for player in self.players:
                print(player)
                player.roll_dice()
                self.place_dice(player)
            i += 1
        self.award_banknotes()
        self.declare_winner()


class UnknownConfigurationException(Exception):
    pass
