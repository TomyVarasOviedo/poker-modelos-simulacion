import multiprocessing
import csv
import main

CANT_PARTIDAS=10
procesos = []

# FUNCIONES DE PARTIDAS
def iniciar_partida(j1, j2, lock):
    """
    Funcion para ejecutar el varias partidas con unas estrategia determinada

    :param j1: Estrategia que va a utilizar el jugador 1
    :param j2: Estrategia que va a utilizar el jugador 2
    """
    for i in range(0,CANT_PARTIDAS):
        # Llama a la funcion del archivo main para iniciar una partida
        resultados = main.run_console_mode(j1,j2)
        with lock:
            with open('resultado.csv', 'a', newline="") as c:
                """-----------------------
                    Provisorio: guardar los resultados en un archivo csv para posterior analisis
                   -----------------------"""
                writer = csv.writer(c,delimiter=",")
                writer.writerow(
                    [
                     resultados["ganador"], #Estrategia ganadora
                     resultados["montos"][0], #Monto resultante del primer jugador
                     resultados["monto"][1], #Monto resultante del segundo jugador
                     resultados["puntaje"][0], #Puntaje del primer jugador 
                     resultados["puntaje"][1] #Puntaje del segundo jugador
                    ])

# FUNCIONES DE PARTIDAS

# <---THREADS --->
if __name__ == "__main__":
    lock = multiprocessing.Lock()

    partida1 = multiprocessing.Process(target=iniciar_partida, args=(lock,"""INSERTAR LAS ESTRATEGIAS AQUI"""))
    partida2 = multiprocessing.Process(target=iniciar_partida, args=(lock,))
    partida3 = multiprocessing.Process(target=iniciar_partida, args=(lock,))
    procesos.append(partida1,partida2,partida3)
    for hilo in procesos:
        hilo.start()

    # <---THREADS --->
    #Espera a que los todas las partidas sean ejecutadas
    for hilo in procesos:
        hilo.join()
    
    print("<--FIN DE TODAS LAS PARTIDAS-->")

