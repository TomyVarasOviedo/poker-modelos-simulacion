# Poker game
> Juego de poker para realizar las simulaciones de la materia de modelos y simulacion
> ## codigo base:
```python
    WIDTH, HEIGHT = 800, 600
    FPS = 30
    WHITE = (255, 255, 255)
    GREEN = (0, 128, 0)
    BLACK = (0, 0, 0)
    
    # Clase que representa una carta
    class Card:
        def __init__(self, suit, rank):
            self.suit = suit
            self.rank = rank
            self.image = None  # Se podría cargar la imagen de la carta si se desea
    
    def __str__(self):
        return f"{self.rank} de {self.suit}"

    # Clase que representa una baraja
    class Deck:
        suits = ['Corazones', 'Diamantes', 'Tréboles', 'Picas']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self, num):
        dealt_cards = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt_cards

    # Clase que representa a un jugador
    class Player:
        def __init__(self, name, chips=1000):
            self.name = name
            self.chips = chips
            self.hand = []
            self.current_bet = 0
    
    def decide_action(self, game_state):
        """
        Este método se podrá sobrescribir o parametrizar en el futuro para incorporar
        la simulación de estrategias. Por ahora, se define una acción por defecto.
        game_state es un diccionario con información actual del juego.
        """
        return "call"  # Ejemplo: siempre igualar la apuesta
    
    def reset_hand(self):
        self.hand = []
        self.current_bet = 0
    # Clase que maneja la lógica del juego de póker
    class PokerGame:
        def __init__(self, players):
            self.players = players
            self.deck = Deck()
            self.community_cards = []
            self.pot = 0
            self.current_bet = 0

    def start_round(self):
        """
        Reinicia el estado del juego para una nueva ronda.
        Se baraja la baraja, se reinician las manos de los jugadores
        y se reparte la mano inicial (2 cartas por jugador).
        """
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        for player in self.players:
            player.reset_hand()
            player.hand = self.deck.deal(2)
    
    def deal_community_cards(self, stage):
        """
        Reparte las cartas comunitarias según la etapa del juego:
        - "flop": 3 cartas
        - "turn" y "river": 1 carta cada una
        """
        if stage == "flop":
            self.community_cards += self.deck.deal(3)
        elif stage in ["turn", "river"]:
            self.community_cards += self.deck.deal(1)
    
    def betting_round(self):
        """
        Ejecuta una ronda de apuestas simple.
        Se recorre cada jugador y se solicita una acción basada en el estado del juego.
        La función 'decide_action' en cada jugador se puede modificar para implementar
        estrategias avanzadas o utilizar un módulo de simulación.
        """
        game_state = {
            "pot": self.pot,
            "current_bet": self.current_bet,
            "community_cards": self.community_cards,
        }
        for player in self.players:
            action = player.decide_action(game_state)
            print(f"{player.name} decide: {action}")
            # Lógica muy simplificada: si el jugador decide "call", iguala la apuesta actual.
            if action == "call":
                bet = self.current_bet - player.current_bet
                player.chips -= bet
                player.current_bet += bet
                self.pot += bet
            elif action == "raise":
                # Aquí se puede implementar la lógica de 'raise'
                pass
            elif action == "fold":
                # Aquí se puede implementar la lógica de 'fold'
                pass
    # Clase que maneja la interfaz gráfica del juego utilizando Pygame
    class PokerUI:
        def __init__(self, game):
            pygame.init()
            self.game = game
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Juego de Póker")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Arial", 20)   
    def draw(self):
        self.screen.fill(GREEN)
        # Dibujar cartas comunitarias
        x_start = 200
        y_start = 50
        card_width = 60
        card_height = 90
        spacing = 10
        for idx, card in enumerate(self.game.community_cards):
            rect = pygame.Rect(x_start + idx*(card_width+spacing), y_start, card_width, card_height)
            pygame.draw.rect(self.screen, WHITE, rect)
            # Se dibuja una abreviatura de la carta (primer carácter del rango y del palo)
            text = self.font.render(f"{card.rank[0]}{card.suit[0]}", True, BLACK)
            self.screen.blit(text, (rect.x + 5, rect.y + 5))        
        # Dibujar las cartas de cada jugador
        for i, player in enumerate(self.game.players):
            x = 50
            y = 200 + i*(card_height+50)
            player_text = self.font.render(f"{player.name} - Fichas: {player.chips}", True, WHITE)
            self.screen.blit(player_text, (x, y - 30))
            for j, card in enumerate(player.hand):
                rect = pygame.Rect(x + j*(card_width+spacing), y, card_width, card_height)
                pygame.draw.rect(self.screen, WHITE, rect)
                text = self.font.render(f"{card.rank[0]}{card.suit[0]}", True, BLACK)
                self.screen.blit(text, (rect.x + 5, rect.y + 5))       
        # Mostrar el pozo actual
        pot_text = self.font.render(f"Pozo: {self.game.pot}", True, WHITE)
        self.screen.blit(pot_text, (WIDTH - 200, HEIGHT - 50))  
    def update(self):
        pygame.display.flip()
        self.clock.tick(FPS)  
    def run(self):
        running = True
        round_started = False       
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # Aquí se podría agregar la lógica para avanzar el juego o responder a eventos de usuario.
            if not round_started:
                self.game.start_round()
                print("Nueva ronda iniciada")
                # Ronda de apuestas pre-flop
                self.game.betting_round()
                # Flop
                self.game.deal_community_cards("flop")
                self.game.betting_round()
                # Turn
                self.game.deal_community_cards("turn")
                self.game.betting_round()
                # River
                self.game.deal_community_cards("river")
                self.game.betting_round()
                round_started = True          
            self.draw()
            self.update()     
        pygame.quit()
        sys.exit()
    def main():
        # Crear jugadores
        player1 = Player("Jugador 1")
        player2 = Player("Jugador 2")
        players = [player1, player2] 
        # Crear instancia del juego de póker
        game = PokerGame(players)
        # Inicializar la interfaz gráfica
        ui = PokerUI(game)
        ui.run()
```
