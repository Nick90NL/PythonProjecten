import random
import time
from openpyxl import Workbook
import itertools

HAND_RANKS = {
    "Straight Flush": 9,
    "Four of a Kind": 8,
    "Full House": 7,
    "Flush": 6,
    "Straight": 5,
    "Three of a Kind": 4,
    "Two Pair": 3,
    "One Pair": 2,
    "High Card": 1
}

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __repr__(self):
        return f"{self.suit} {self.value}"

class HandEvaluator:
    def __init__(self, cards):
        self.cards = sorted(cards, key=lambda card: self.card_value(card.value), reverse=True)
        self.ranks = [card.value for card in self.cards]
        self.suits = [card.suit for card in self.cards]
        
    @staticmethod
    def card_value(rank):
        rank_to_value = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return rank_to_value.get(rank, 0)

    def is_flush(self):
        return len(set(self.suits)) == 1

    def is_straight(self):
        rank_values = [self.card_value(rank) for rank in self.ranks]
        if len(set(rank_values)) < 5:
            return False
        if max(rank_values) - min(rank_values) == 4:
            return True
        return set(rank_values) == {2, 3, 4, 5, 14}
    
    def is_four_of_a_kind(self):
        rank_counts = {rank: self.ranks.count(rank) for rank in self.ranks}
        return 4 in rank_counts.values()
    
    def is_full_house(self):
        rank_counts = {rank: self.ranks.count(rank) for rank in self.ranks}
        return 3 in rank_counts.values() and 2 in rank_counts.values()
    
    def is_three_of_a_kind(self):
        rank_counts = {rank: self.ranks.count(rank) for rank in self.ranks}
        return 3 in rank_counts.values()    
    
    def is_two_pair(self):
        rank_counts = {rank: self.ranks.count(rank) for rank in self.ranks}
        return len([rank for rank, count in rank_counts.items() if count == 2]) == 2

    def is_one_pair(self):
        rank_counts = {rank: self.ranks.count(rank) for rank in self.ranks}
        return list(rank_counts.values()).count(2) == 1

    def evaluate_hand(self):
        if self.is_flush() and self.is_straight():
            return ("Straight Flush", HAND_RANKS["Straight Flush"], self.cards)
        if self.is_four_of_a_kind():
            return ("Four of a Kind", HAND_RANKS["Four of a Kind"], self.cards)
        if self.is_full_house():
            return ("Full House", HAND_RANKS["Full House"], self.cards)
        if self.is_flush():
            return ("Flush", HAND_RANKS["Flush"], self.cards)
        if self.is_straight():
            return ("Straight", HAND_RANKS["Straight"], self.cards)
        if self.is_three_of_a_kind():
            return ("Three of a Kind", HAND_RANKS["Three of a Kind"], self.cards)
        if self.is_two_pair():
            return ("Two Pair", HAND_RANKS["Two Pair"], self.cards)
        if self.is_one_pair():
            return ("One Pair", HAND_RANKS["One Pair"], self.cards)
        return ("High Card", HAND_RANKS["High Card"], self.cards)

class PokerHandEvaluator:
    def __init__(self, hole_cards, community_cards):
        self.hole_cards = hole_cards
        self.community_cards = community_cards

    def get_all_hands(self):
        all_seven_cards = self.hole_cards + self.community_cards
        return list(itertools.combinations(all_seven_cards, 5))

    def evaluate(self):
        best_hand = None
        best_rank = ("", 0)
        for combo in self.get_all_hands():
            evaluator = HandEvaluator(list(combo))
            rank = evaluator.evaluate_hand()

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def __repr__(self):
        return f"{self.name}: {self.hand}"

class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in ['♥', '♦', '♣', '♠'] for value in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']]
    
    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None

class PokerTable:
    def __init__(self, players):
        self.num_players = len(players)
        self.players = [Player(name) for name in players]
        print(f"Laten we gaan pokeren!")
        print(f"De spelers van vandaag zijn: {', '.join(players)}.")
        random.shuffle(self.players)
        self.dealer_position = random.randint(0, self.num_players - 1)
        self.deck = Deck()
        self.deck.shuffle()
        self.distribute_player_cards()
        self.print_player_hands()

    def distribute_player_cards(self):
        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.deal())

    def print_player_hands(self):
        for player in self.players:
            print(f"{player.name}: {player.hand}")

    def play_hand(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.reset_player_hands()
        self.distribute_player_cards()
        self.print_player_hands()
        # Evaluate hands and determine winner here

    def reset_player_hands(self):
        for player in self.players:
            player.hand = []

names = ["Nick", "Willem", "Maarten", "Jorn", "Kevin", "Patrick"]
table = PokerTable(players=names)
table.play_hand()           

