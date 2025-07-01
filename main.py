from PokerSimulationManager import PokerSimulationManager

def mostrar_menu():
    print("Estrategias disponibles:")
    print("1. Tight-Aggressive")
    print("2. Loose-Aggressive")
    print("3. Conservative")
    print("4. Bluffing")

def seleccionar_estrategia(jugador):
    estrategias = {
        "1": "Tight-Aggressive",
        "2": "Loose-Aggressive",
        "3": "Conservative",
        "4": "Bluffing"
    }

    while True:
        print(f"\nSelecciona la estrategia para el {jugador}:")
        mostrar_menu()
        opcion = input("Ingresa el número de la estrategia: ").strip()
        if opcion in estrategias:
            return estrategias[opcion]
        else:
            print("Opción inválida. Intenta de nuevo.")

def main():
    print("Simulador de Poker Heads-Up (Uno contra Uno)")

    estrategia1 = seleccionar_estrategia("Jugador 1")
    estrategia2 = seleccionar_estrategia("Jugador 2")

    while True:
        try:
            num_partidas = int(input("\n¿Cuántas partidas deseas simular? (ej: 10000): "))
            if num_partidas <= 0:
                raise ValueError
            break
        except ValueError:
            print("Por favor, ingresa un número entero válido.")

    print(f"\nSimulando {num_partidas} partidas entre {estrategia1} y {estrategia2}...\n")

    sim = PokerSimulationManager(estrategia1, estrategia2, num_partidas)
    sim.run_simulation()
    results = sim.get_results()
    print(results)

if __name__ == "__main__":
    main()
