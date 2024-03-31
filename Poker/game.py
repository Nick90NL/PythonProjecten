import random
from itertools import combinations
import time
import pandas as pd
import collections
import os
from openpyxl import writer
import zipfile
        
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

    def __lt__(self, other):
        # Vergelijking op basis van kaartwaarde, dan op suit
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
        evaluator = HandEvaluator(self.hand + community_cards)
        return evaluator.get_best_hand(community_cards)

class PokerTable:
    def __init__(self, players):
        self.players = [Player(name) for name in players]
        print(f"Laten we gaan pokeren!")
        time.sleep(0)
        print(f"De spelers van vandaag zijn: {', '.join(players)}.")
        time.sleep(0)
        random.shuffle(self.players)  # Schud de spelers voor willekeurige zitplaatsen
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
        # Geeft een lijst van spelers terug, beginnend bij de speler na de dealer
        return self.players[(self.dealer_position + 1):] + self.players[:(self.dealer_position + 1)]
    
    def print_community_cards(self):
        print("\nLaten we gaan kijken naar de kaarten op tafel:")
        time.sleep(0)
        if len(self.community_cards) >= 3:  # Controleer of er ten minste 3 community cards zijn
            flop = f"Flop: \t" + ' '.join(card_to_string(card) for card in self.community_cards[:3])
            print(flop)
            time.sleep(0)
        if len(self.community_cards) >= 4:  # Controleer of er ten minste 4 community cards zijn
            turn = f"Turn: \t" + card_to_string(self.community_cards[3])
            print(turn)
            time.sleep(0)
        if len(self.community_cards) >= 5:  # Controleer of er ten minste 5 community cards zijn
            river = f"River: \t" + card_to_string(self.community_cards[4]) + '\n'
            print(river)
            time.sleep(0)
        time.sleep(0)

    def reset_table(self):
        # Reset de spelershanden en de community cards voor een nieuwe ronde
        for player in self.players:
            player.hand = []
        self.community_cards = []

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
        self.hand = sorted(hand, key=lambda card: Card.card_value(card.value), reverse=True)
        self.ranks = [Card.card_value(card.value) for card in self.hand]
        self.suits = [card.suit for card in self.hand]

    def get_hand_rank(self):
        rank_counts = collections.Counter(self.ranks)
        sorted_ranks = sorted(self.ranks, key=lambda x: (rank_counts[x], x), reverse=True)

        is_flush = len(set(self.suits)) == 1
        is_straight = self.is_sequence(sorted_ranks)

        if is_flush and is_straight:
            if 14 in self.ranks and set(sorted_ranks[:5]) == {10, 11, 12, 13, 14}:
                return (HAND_RANKS["Royal Flush"], self.sort_straight_flush(self.hand))
            return (HAND_RANKS["Straight Flush"], self.sort_straight_flush(self.hand))
        elif 4 in rank_counts.values():
            return (HAND_RANKS["Four of a Kind"], self.sort_four_of_a_kind(self.hand))
        elif 3 in rank_counts.values() and 2 in rank_counts.values():
            return (HAND_RANKS["Full House"], self.sort_full_house(self.hand))
        elif is_flush:
            return (HAND_RANKS["Flush"], self.sort_flush(self.hand))
        elif is_straight:
            return (HAND_RANKS["Straight"], self.sort_straight(self.hand))
        elif 3 in rank_counts.values():
            return (HAND_RANKS["Three of a Kind"], self.sort_three_of_a_kind(self.hand))
        elif list(rank_counts.values()).count(2) == 2:
            return (HAND_RANKS["Two Pair"], self.sort_two_pair(self.hand))
        elif 2 in rank_counts.values():
            return (HAND_RANKS["One Pair"], self.sort_one_pair(self.hand))
        else:
            return (HAND_RANKS["High Card"], self.sort_high_card(self.hand))
    
    def get_hand_rank(self, hand=None):
        if hand is None:
            hand = self.hand
        else:
            # Als een specifieke hand wordt meegegeven, sorteer deze en bepaal de ranks en suits opnieuw
            hand = sorted(hand, key=lambda card: Card.card_value(card.value), reverse=True)
        ranks = [Card.card_value(card.value) for card in hand]
        suits = [card.suit for card in hand]

        rank_counts = collections.Counter(ranks)
        sorted_ranks = sorted(ranks, key=lambda x: (rank_counts[x], x), reverse=True)

        is_flush = len(set(suits)) == 1
        is_straight = self.is_sequence(sorted_ranks)

        # Hier volgt de bestaande logica om de hand rank te bepalen...
        if is_flush and is_straight:
            # Enzovoort voor de rest van de hand type bepalingen...

        # Zorg ervoor dat je de hand rank en de gesorteerde hand teruggeeft
            return best_rank, sorted_hand
    
    # Je sorteermethoden hieronder (ik zal er een paar demonstreren):
    def sort_straight_flush(self, hand):
        # Bij straight flushes willen we gewoon de kaarten sorteren op waarde
        return sorted(hand, key=lambda card: Card.card_value(card.value), reverse=True)

    def sort_four_of_a_kind(self, hand):
        rank = next(rank for rank, count in collections.Counter(self.ranks).items() if count == 4)
        four_cards = sorted([card for card in hand if Card.card_value(card.value) == rank], key=lambda card: Card.card_value(card.value), reverse=True)
        kicker = [card for card in hand if Card.card_value(card.value) != rank]
        return four_cards + kicker

    def sort_full_house(self, hand):
        three_rank = next(rank for rank, count in collections.Counter(self.ranks).items() if count == 3)
        pair_rank = next(rank for rank, count in collections.Counter(self.ranks).items() if count == 2)
        three_cards = sorted([card for card in hand if Card.card_value(card.value) == three_rank], key=lambda card: Card.card_value(card.value), reverse=True)
        pair_cards = sorted([card for card in hand if Card.card_value(card.value) == pair_rank], key=lambda card: Card.card_value(card.value), reverse=True)
        return three_cards + pair_cards

    def sort_flush(self, hand):
        # Bij een flush sorteren we gewoon op kaartwaarde
        return sorted(hand, key=lambda card: Card.card_value(card.value), reverse=True)

    def sort_straight(self, hand):
        # Bij een straight sorteren we op kaartwaarde; speciale aandacht voor de A-2-3-4-5 straight
        hand_values = [Card.card_value(card.value) for card in hand]
        if set(hand_values) == {14, 2, 3, 4, 5}:
            # Verplaats A (waarde 14) naar het einde van de hand
            ace = [card for card in hand if card.value == 'A'][0]
            hand.remove(ace)
            hand.append(ace)
        return hand

    def sort_three_of_a_kind(self, hand):
        three_rank = next(rank for rank, count in collections.Counter(self.ranks).items() if count == 3)
        three_cards = sorted([card for card in hand if Card.card_value(card.value) == three_rank], key=lambda card: Card.card_value(card.value), reverse=True)
        kickers = sorted([card for card in hand if Card.card_value(card.value) != three_rank], key=lambda card: Card.card_value(card.value), reverse=True)
        return three_cards + kickers

    def sort_two_pair(self, hand):
        pair_ranks = [rank for rank, count in collections.Counter(self.ranks).items() if count == 2]
        high_pair_rank = max(pair_ranks)
        low_pair_rank = min(pair_ranks)
        high_pair = sorted([card for card in hand if Card.card_value(card.value) == high_pair_rank], key=lambda card: Card.card_value(card.value), reverse=True)
        low_pair = sorted([card for card in hand if Card.card_value(card.value) == low_pair_rank], key=lambda card: Card.card_value(card.value), reverse=True)
        kicker = [card for card in hand if Card.card_value(card.value) not in pair_ranks]
        return high_pair + low_pair + kicker

    def sort_one_pair(self, hand):
        pair_value = next(rank for rank, count in collections.Counter(self.ranks).items() if count == 2)
        pair_cards = [card for card in hand if Card.card_value(card.value) == pair_value]
        kicker_cards = [card for card in hand if Card.card_value(card.value) != pair_value]
        kicker_cards_sorted = sorted(kicker_cards, key=lambda card: Card.card_value(card.value), reverse=True)
        return pair_cards + kicker_cards_sorted

    def sort_high_card(self, hand):
        # Bij high card sorteren we gewoon op de kaartwaarde
        return sorted(hand, key=lambda card: Card.card_value(card.value), reverse=True)

    @staticmethod
    def is_sequence(ranks):
        sorted_ranks = sorted(ranks)
        return len(set(ranks)) == 5 and (sorted_ranks[-1] - sorted_ranks[0] == 4 or sorted_ranks == [2, 3, 4, 5, 14])

def card_to_string(card):
    suit_to_symbol = {'♣': '♣', '♦': '♦', '♥': '♥', '♠': '♠'}
    value_to_face = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    
    suit = suit_to_symbol[card.suit]
    value = value_to_face[card.value] if card.value in value_to_face else str(card.value)
    
    return f"{suit} {value}"

def find_and_print_sorted_best_hands(players, community_cards):
    if len(community_cards) < 3:
        print("Er zijn niet genoeg community cards beschikbaar om handen te evalueren.")
        return []

    best_hands = []
    for player in players:
        best_hand, best_hand_rank = player.get_best_hand(community_cards)
        # Sorteer de kaarten in de hand om vergelijkingen op basis van waarde te vergemakkelijken
        sorted_best_hand = sorted(best_hand, key=lambda card: Card.card_value(card.value), reverse=True)
        best_hands.append((player, sorted_best_hand, best_hand_rank))

    # Sorteer eerst op handrang, dan op de individuele kaartwaarden binnen de hand
    best_hands.sort(key=lambda x: (x[2], [Card.card_value(card.value) for card in x[1]]), reverse=True)

    max_name_length = max(len(player.name) for player, _, _ in best_hands)
    max_hand_type_length = max(len(hand_type) for hand_type, _ in HAND_RANKS.items())

    for index, (player, best_hand, best_rank) in enumerate(best_hands, start=1):
        hand_type = [k for k, v in HAND_RANKS.items() if v == best_rank][0]
        name_padded = player.name.ljust(max_name_length)
        hand_type_padded = hand_type.ljust(max_hand_type_length)
        sorted_best_hand_str = ", ".join(card_to_string(card) for card in best_hand)
        best_hands[index - 1] += (index,)
        print(f"{index}. {name_padded} {hand_type_padded} {sorted_best_hand_str}")

    return best_hands

file_path = "poker_results.xlsx"

# Controleer of het bestand bestaat. Zo niet, maak dan een leeg bestand aan.
if not os.path.exists(file_path):
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
        # Maak een leeg DataFrame aan met de juiste kolomnamen
        empty_df = pd.DataFrame(columns=['Round', 'Number', 'Player', 'Player Hand', 'Hand Type', 'Best Hand', 'Flop', 'Turn', 'River'])
        # Schrijf het lege DataFrame naar het Excel-bestand op het werkblad 'Sheet1'
        empty_df.to_excel(writer, sheet_name='Sheet1', index=False)

# Verwijder het bestaande bestand als het corrupt is
if os.path.exists(file_path):
    try:
        # Probeer het bestand te openen om te controleren of het niet corrupt is
        pd.read_excel(file_path)
    except (FileNotFoundError, zipfile.BadZipFile, KeyError, OSError):
        print("Het bestand is corrupt en wordt opnieuw aangemaakt.")
        os.remove(file_path)
else:
    print("Het bestand bestaat nog niet en wordt aangemaakt.")

if __name__ == "__main__":
    names = ["Nick", "Willem", "Maarten", "Jorn", "Kevin", "Glenn"]
    
    while True:
        try:
            num_rounds = int(input("Hoeveel rondes wil je spelen? "))
            table = PokerTable(names)
            writer = None  # Initialiseer de Excel-writer buiten de for-lus
            break  # Als de invoer geldig is, stop met de lus en ga verder met de rest van de code
        except ValueError:
            print("Voer een geldig getal in voor het aantal rondes.")
      
    try:
        for i in range(num_rounds):
            print(f"\n--- Ronde {i+1} ---")
            time.sleep(0)

            if i == 0:
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
                time.sleep(0)

            table.distribute_community_cards(deck, 5)
            table.print_community_cards()
            best_hands = find_and_print_sorted_best_hands(table.get_player_order(), table.community_cards)

            # Open de Excel-writer als deze nog niet is geopend
            if writer is None:
                writer = pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay')

            # Voeg de resultaten van deze ronde toe aan het Excel-bestand
            round_results = pd.DataFrame([{
                'Round': i + 1,
                'Number': position,
                'Player': player.name,
                'Player Hand': ", ".join(card_to_string(card) for card in player.hand),
                'Best Hand': ", ".join(card_to_string(card) for card in best_hand),
                'Hand Type': [k for k, v in HAND_RANKS.items() if v == best_rank][0],
                'Flop': ', '.join(str(card) for card in table.community_cards[:3]),
                'Turn': str(table.community_cards[3]),
                'River': str(table.community_cards[4])
            } for _, (player, best_hand, best_rank, position) in enumerate(best_hands)])

            round_results.to_excel(writer, startrow=writer.sheets['Sheet1'].max_row, index=False,
                                header=False if writer.sheets['Sheet1'].max_row > 0 else True)

    except KeyboardInterrupt:
        print("\n\nHet programma is gestopt. De resultaten worden opgeslagen in het Excel-bestand.")
    finally:
        # Sluit de Excel-writer voordat het programma wordt afgesloten
        if writer is not None:
            writer.close()

# Voeg een lege regel toe aan het einde van het bestand
if writer is not None:
    writer.sheets['Sheet1'].append([''] * len(round_results.columns))