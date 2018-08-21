from environments.base import Environment
from random import shuffle
from blackjack_utils import assess_card, calculate_score
import numpy as np
from blackjack_policy import BlackjackPlayer
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd


class CardDeck:
    def __init__(self):
        self.available_cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] * 4
        shuffle(self.available_cards)
    def draw_card(self):
        return self.available_cards.pop()


class Blackjack(Environment):
    def __init__(self, num_other_players=5):
        super(Environment, self).__init__()
        self.seen_cards = []
        self.my_hand = []
        self.dealer_hand = []
        self.deck = CardDeck()
        self.num_other_players = 5


    def default_policy(self, cur_score):
        if cur_score < 16:
            return 1
        else:
            return 0

    def naiive_policy(self, my_hand, seen_cards, dealer_hand):
        cur_score = calculate_score(my_hand)
        if cur_score < 16:
            return 1
        elif cur_score > 16:
            return 0
        else:
            if "A" in my_hand:
                return 1
            else:
                return 0

    def dealer_draw(self):
        card = self.deck.draw_card()
        self.seen_cards.append(card)
        self.dealer_hand.append(card)

    def other_player_draw(self):
        card = self.deck.draw_card()
        self.seen_cards.append(card)
        return card

    def my_draw(self):
        card = self.deck.draw_card()
        self.seen_cards.append(card)
        self.my_hand.append(card)

    def dealer_play(self):
        dealer_score = calculate_score(self.dealer_hand, return_minimum=True)
        decision = 1
        while dealer_score < 17 and decision:
            self.dealer_draw()
            decision = self.naiive_policy(self.dealer_hand, self.seen_cards, self.dealer_hand)
        return calculate_score(self.dealer_hand)

    def play_hand(self, policy):
        # deal cards and let all other players play
        self.initialize_hand()

        # inputs are number of each card seen, my minimum hand score, how many aces I have
        # run policy repeatedly until policy returns either 0 (stay) or player score exceeds 21
        policy_result = 1
        score = 0
        while policy_result and calculate_score(self.my_hand) < 21:
            self.my_draw()
            policy_result = policy(self.my_hand, self.seen_cards, self.dealer_hand)
            score = calculate_score(self.my_hand)
        if score == 21:
            return 1
        if score > 21:
            return -1
        dealer_score = self.dealer_play()
        if dealer_score > 21:
            return 1
        if score > dealer_score:
            return 1
        if score == dealer_score:
            return 0
        else:
            return -1


    def run_policy(self, policy, **kwargs):
        return policy(kwargs)


    def initialize_hand(self):
        self.deck = CardDeck()
        self.seen_cards = []
        self.my_hand = []
        self.dealer_hand = []
        # distribute cards to other players
        for other_player in range(self.num_other_players):
            other_player_hand = []
            other_player_score = 0
            while other_player_score < 21:
                if self.default_policy(other_player_score):
                    other_player_hand.append(self.other_player_draw())
                    other_player_score = calculate_score(other_player_hand)
                else:
                    break
        self.dealer_draw()
        self.my_draw()

if __name__ == "__main__":
    bj_env = Blackjack()
    bj_player = BlackjackPlayer()
    bj_player.create_model()
    results = []
    for i in range(1000):
        results.append(bj_env.play_hand(bj_player.run_policy))

    total = np.sum(results)
    print("naiive_policy total: ", total)


    hidden_size = 10
    # cards seen (13) + my score (1) + my aces (1) + dealer score (1) + dealer aces (1)
    num_inputs = 13 + \
                 1 + \
                 1 + \
                 1 + \
                 1



