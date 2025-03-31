from PIL import Image, ImageTk
import os

class CardDisplay:
    def __init__(self):
        self.unicode_cards = {
            'Hearts': {'2':'🂲', '3':'🂳', '4':'🂴', '5':'🂵', '6':'🂶', '7':'🂷', 
                      '8':'🂸', '9':'🂹', '10':'🂺', 'J':'🂻', 'Q':'🂽', 'K':'🂾', 'A':'🂱'},
            'Diamonds': {'2':'🃂', '3':'🃃', '4':'🃄', '5':'🃅', '6':'🃆', '7':'🃇', 
                        '8':'🃈', '9':'🃉', '10':'🃊', 'J':'🃋', 'Q':'🃍', 'K':'🃎', 'A':'🃁'},
            'Clubs': {'2':'🃒', '3':'🃓', '4':'🃔', '5':'🃕', '6':'🃖', '7':'🃗', 
                     '8':'🃘', '9':'🃙', '10':'🃚', 'J':'🃛', 'Q':'🃝', 'K':'🃞', 'A':'🃑'},
            'Spades': {'2':'🂢', '3':'🂣', '4':'🂤', '5':'🂥', '6':'🂦', '7':'🂧', 
                      '8':'🂨', '9':'🂩', '10':'🂪', 'J':'🂫', 'Q':'🂭', 'K':'🂮', 'A':'🂡'}
        }
        self.card_back = '🂠'

    def get_card_symbol(self, card):
        if isinstance(card, str) or card is None:
            return self.card_back
        return self.unicode_cards[card.suit][card.value]            