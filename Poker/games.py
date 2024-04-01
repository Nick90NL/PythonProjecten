import random
from itertools import combinations
import time
import pandas as pd
import collections
import os
import zipfile

HAND_RANKS = {
    "Royal Flush": 10,
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

    def __lt__(self, other):
        # Comparison based on card value, then suit
        return (Card.card_value(self.value), self.suit) < (Card.card_value(other.value), other.suit)

    @staticmethod
    def card_value(rank):
        rank_to_value = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return rank_to_value.get(rank, 0)
    
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def __repr__(self):
        return f"{self.name}: {', '.join(str(card) for card in self.hand)}"

    def get_best_hand(self, community_cards):
        all_seven_cards = self.hand + community_cards
        all_possible_hands = list(combinations(all_seven_cards, 5))
        best_hand = max(all_possible_hands, key=lambda hand: HandEvaluator(hand).get_hand_rank()[0])
        return best_hand, HandEvaluator(best_hand).get_hand_rank()
    
class PokerTable:
    def __init__(self, players):
        self.players = [Player(name) for name in players]
        print(f"Laten we gaan pokeren!")
        time.sleep(0)
        print(f"De spelers van vandaag zijn: {', '.join(players)}.")
        time.sleep(0)
        random.shuffle(self.players)  
        self.dealer_position = random.randint(0, len(self.players) - 1)
        self.community_cards = []
        self.introduce_players()
        self.deck = Deck()

    def introduce_players(self):
        print("\nSpelers worden willekeurig aan een stoel toegewezen...")
        time.sleep(0)
        for i, player in enumerate(self.players):
            print(f"{player.name} mag op stoel {i + 1}.")
            time.sleep(0)
        time.sleep(0)
        print(f"\nIedereen zit, laten we beginnen!")
        time.sleep(0)
    
    def dealer_button(self):
        print(f"\nDe dealer button is willekeurig toegewezen aan {self.players[self.dealer_position].name} voor de eerste ronde. De kaarten worden één voor één gedeeld, de eerste is dus voor {self.players[(self.dealer_position + 1) % len(self.players)].name}.")
        print(f"De kaarten worden geschut en gedeeld...")
        time.sleep(0)
        
    def move_dealer_button(self):
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        print(f"\nDe dealer button verplaatst naar {self.players[self.dealer_position].name}.")
        print(f"Volgende ronde! De kaarten worden opnieuw geschut en gedeeld...")
        time.sleep(0)

    def distribute_player_cards(self, deck):
        for _ in range(2):
            for i in range(len(self.players)):
                player = self.players[(self.dealer_position + 1 + i) % len(self.players)]
                player.hand.append(deck.deal())
                time.sleep(0)

    def distribute_community_cards(self, deck, num_cards):
        for _ in range(num_cards):
            card = deck.deal()
            self.community_cards.append(card)
            time.sleep(0)
    
    def get_player_order(self):
        return self.players[(self.dealer_position + 1):] + self.players[:(self.dealer_position + 1)]
    
    def print_community_cards(self):
        print("\nLaten we gaan kijken naar de kaarten op tafel:")
        time.sleep(0)
        if len(self.community_cards) >= 3:  
            flop = f"Flop: \t" + ' '.join(card_to_string(card) for card in self.community_cards[:3])
            print(flop)
            time.sleep(0)
        if len(self.community_cards) >= 4:  
            turn = f"Turn: \t" + card_to_string(self.community_cards[3])
            print(turn)
            time.sleep(0)
        if len(self.community_cards) >= 5:  
            river = f"River: \t" + card_to_string(self.community_cards[4]) + '\n'
            print(river)
            time.sleep(0)
        time.sleep(0)

    def reset_table(self):
        for player in self.players:
            player.hand = []
        self.community_cards = []
        
    def evaluate_player_hands(self):
        for player in self.players:
            best_hand, rank = player.get_best_hand(self.community_cards)
            print(f"{player.name}'s beste hand: {best_hand} met rang: {rank}")

class Deck:
    def __init__(self):
        suits = ['♥', '♦', '♣', '♠']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, value) for suit in suits for value in values]
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop() if self.cards else None
    
class HandEvaluator:
    def __init__(self, hand):
        self.hand = hand

    def get_hand_rank(self):
        hand = sorted(self.hand, key=lambda card: Card.card_value(card.value), reverse=True)
        ranks = [Card.card_value(card.value) for card in hand]
        suits = [card.suit for card in hand]

        rank_counts = collections.Counter(ranks)
        is_flush = len(set(suits)) == 1
        is_straight = self.is_sequence(ranks)

        if is_flush and is_straight:
            return (HAND_RANKS["Straight Flush"], self.select_best_hand(hand))

        if 4 in rank_counts.values():
            four = self._get_n_of_a_kind(hand, 4)
            kicker = self._get_kickers(hand, exclude_cards=four, count=1)
            return (HAND_RANKS["Four of a Kind"], four + kicker)

        if sorted(rank_counts.values(), reverse=True) == [3, 2]:
            three = self._get_n_of_a_kind(hand, 3)
            two = self._get_n_of_a_kind(hand, 2, exclude_cards=three)
            return (HAND_RANKS["Full House"], three + two)

        if is_flush:
            return (HAND_RANKS["Flush"], self.select_best_hand(hand))

        if is_straight:
            return (HAND_RANKS["Straight"], self.select_best_hand(hand))

        if 3 in rank_counts.values():
            three = self._get_n_of_a_kind(hand, 3)
            kickers = self._get_kickers(hand, exclude_cards=three, count=2)
            return (HAND_RANKS["Three of a Kind"], three + kickers)

        if sorted(rank_counts.values(), reverse=True) == [2, 2, 1]:
            first_pair = self._get_n_of_a_kind(hand, 2)
            second_pair = self._get_n_of_a_kind(hand, 2, exclude_cards=first_pair)
            kicker = self._get_kickers(hand, exclude_cards=first_pair + second_pair, count=1)
            return (HAND_RANKS["Two Pair"], first_pair + second_pair + kicker)

        if 2 in rank_counts.values():
            pair = self._get_n_of_a_kind(hand, 2)
            kickers = self._get_kickers(hand, exclude_cards=pair, count=3)
            return (HAND_RANKS["One Pair"], pair + kickers)

        return (HAND_RANKS["High Card"], self.select_best_hand(hand))

    def _get_n_of_a_kind(self, hand, n, exclude_cards=[]):
        rank_counts = collections.Counter(Card.card_value(card.value) for card in hand if card not in exclude_cards)
        for rank, count in rank_counts.items():
            if count == n:
                return [card for card in hand if Card.card_value(card.value) == rank][:n]
        return []

    def _get_kickers(self, hand, exclude_cards=[], count=1):
        return [card for card in hand if card not in exclude_cards][:count]

    def select_best_hand(self, hand):
        return sorted(hand, key=lambda card: Card.card_value(card.value), reverse=True)[:5]

    @staticmethod
    def is_sequence(ranks):
        return ranks in [list(range(ranks[0], ranks[0] - 5, -1)), [14, 5, 4, 3, 2]]

def card_to_string(card):
    suit_to_symbol = {'♣': '♣', '♦': '♦', '♥': '♥', '♠': '♠'}
    value_to_face = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    
    suit = suit_to_symbol[card.suit]
    value = value_to_face[card.value] if card.value in value_to_face else str(card.value)
    
    return f"{suit} {value}"

def main():
    names = ["Nick", "Willem", "Maarten", "Jorn", "Kevin", "Glenn"]
    num_rounds = int(input("Hoeveel rondes wil je spelen? "))
    
    try:
        for i in range(num_rounds):
            print(f"\n--- Ronde {i+1} ---")
            if i == 0:
                table = PokerTable(names)
                table.dealer_button()
            else:
                table.move_dealer_button()

            table.reset_table()
            deck = Deck()
            table.distribute_player_cards(deck)
            print("\nDe handen zijn bekend:")
            for player in table.get_player_order():
                player.hand.sort(reverse=True)
                player_hand = ', '.join(str(card) for card in player.hand)
                print(f"{player.name.ljust(10)}: {player_hand}")

            table.distribute_community_cards(deck, 5)
            table.print_community_cards()
            table.evaluate_player_hands()
            
    except KeyboardInterrupt:
        print("\nSpel gestopt.")

if __name__ == "__main__":
    main()