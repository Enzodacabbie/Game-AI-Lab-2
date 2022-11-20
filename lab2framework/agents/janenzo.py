from hanabi import *
import util
import agent
import random

def format_hint(h):
    if h == HINT_COLOR:
        return "color"
    return "rank"

class Janenzo(agent.Agent):
    def __init__(self, name, pnr): # initializes the agent
        self.name = name
        self.hints = {} # what hints the agent gave about other players' cards
        self.pnr = pnr # equivalent to nr (the agent's number)
        self.explanation = []

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        for player,hand in enumerate(hands): # nested for loop, goes through the hands of every player
            for card_index,_ in enumerate(hand): # for every card in the hand
                if (player,card_index) not in self.hints:
                    self.hints[(player,card_index)] = set() # if there is no set of hints for this card, make one
        known = [""]*5
        for h in self.hints:
            pnr, card_index = h 
            if pnr != nr: # checks that it is the other player (not the agent)
                known[card_index] = str(list(map(format_hint, self.hints[h]))) 
        self.explanation = [["hints received:"] + known] # for every card in the other player's hand, explanation of hints they got

        my_knowledge = knowledge[nr] # the agent's knowledge of its own cards
        
        potential_discards = []
        for i,k in enumerate(my_knowledge): # goes through all the agent's cards and plays or adds to potential discards
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)
            if util.is_useless(k, board):    
                potential_discards.append(i)
                
        if potential_discards: # if there are potential discards, get rid of a random one
            return Action(DISCARD, card_index=random.choice(potential_discards))
         
        playables = []        
        for player,hand in enumerate(hands):
            if player != nr: # for every player's hand if it is not the agent, checks if cards are playable
                for card_index,card in enumerate(hand):
                    if card.is_playable(board):                              
                        playables.append((player,card_index)) 
        
        playables.sort(key=lambda which: -hands[which[0]][which[1]].rank) # sorts others' playable cards in descending rank
        while playables and hints > 0: # while there are still playable cards for the other player and you have hint tokens
            player,card_index = playables[0]
            knows_rank = True
            real_color = hands[player][card_index].color
            real_rank = hands[player][card_index].rank
            k = knowledge[player][card_index]
            
            hinttype = [HINT_COLOR, HINT_RANK]
            
            
            for h in self.hints[(player,card_index)]:
                hinttype.remove(h) # if the other play already received a certain hint about a card, do not consider that hint anymore
            
            t = None
            if hinttype:
                t = random.choice(hinttype) # if there are potential hints to still give, choose a random one
            
            # does whatever hint it selected
            if t == HINT_RANK:
                for i,card in enumerate(hands[player]):
                    if card.rank == hands[player][card_index].rank:
                        self.hints[(player,i)].add(HINT_RANK)
                return Action(HINT_RANK, player=player, rank=hands[player][card_index].rank)
            if t == HINT_COLOR:
                for i,card in enumerate(hands[player]):
                    if card.color == hands[player][card_index].color:
                        self.hints[(player,i)].add(HINT_COLOR)
                return Action(HINT_COLOR, player=player, color=hands[player][card_index].color)
            
            playables = playables[1:] # gets rid of the first playable (index 0)
 
        if hints > 0: # remembers which hints were given by the agent
            hints = util.filter_actions(HINT_COLOR, valid_actions) + util.filter_actions(HINT_RANK, valid_actions)
            hintgiven = random.choice(hints)
            if hintgiven.type == HINT_COLOR:
                for i,card in enumerate(hands[hintgiven.player]):
                    if card.color == hintgiven.color:
                        self.hints[(hintgiven.player,i)].add(HINT_COLOR)
            else:
                for i,card in enumerate(hands[hintgiven.player]):
                    if card.rank == hintgiven.rank:
                        self.hints[(hintgiven.player,i)].add(HINT_RANK)
                
            return hintgiven

        return random.choice(util.filter_actions(DISCARD, valid_actions))

    def inform(self, action, player): # updates what is known about cards in the other player's hand after playing or discarding
        if action.type in [PLAY, DISCARD]:
            if (player,action.card_index) in self.hints:
                self.hints[(player,action.card_index)] = set()
            for i in range(5):
                if (player,action.card_index+i+1) in self.hints:
                    self.hints[(player,action.card_index+i)] = self.hints[(player,action.card_index+i+1)]
                    self.hints[(player,action.card_index+i+1)] = set()

agent.register("janenzo", "Janenzo Agent", Janenzo)