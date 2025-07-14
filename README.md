# Poker game
> Juego de poker para realizar las simulaciones de la materia de modelos y simulacion
# Resumen de Modelos y Simulacion

## ¿Como se juega el poker texas hold'em?
> Esta variante de las más populares del poker, cuyo objetivo principal es a traves de combinaciones de cartas (No mas de 5 cartas) obtener una serie de puntos que le permiten ganar una ronda, quien mas veces gane en las rondas, gana el juego.
> ### Reglas
> - Los jugadores se le reparte dos cartas boca abajo
> - A lo largo de las rondas se raprten cinco cartas mas boca arriba en el centro de la mesa
> - Las cartas comunitarias pueden ser utilizadas por los jugadores para construir su mano
> 
> Una ronda de poker se termina cuando se llega al Showdown

> El proceso para realizar las simulaciones de los juegos de poker, comienza en el archivo main que se encarga de llamar a la interfaz grafica para que se pueda comparar las estrategias. Las cuales son:

## Bluffing 
> Esta estrategia se centra en el engaño para despistar a los rivales y ganar
## Conservative
> Se enfocan en jugar de manera que unicamente juegan cuando cuentan con una mano premium o con pocas posibilidades de fallar
## LooseAgressive
> Se centra en precionar al rival, aunque no se tenga manos fuertes unicamente para desista 
## TightAgressive
> Su papel principal es presentarse inicialemente como cautelosa para despues subir en intesidad a lo largo de la partida

## Flujo de la informacion
> La aplicacion empieza dentro del archivo main, donde se llama a la interfaz grafica para que el usuario seleccione que estrategias se van a simular, para determinar que estrategia a traves de su win rate es mas efectiva. Al selecionar las estrategias y presionar el boton para comenzar la simulacion, luego de esto se llama a la clase `PokerSimulationManager` que se encarga de instanciar las clases que controlan el comportamiento de las distintas estrategias y por medio de su metodo `run_simulation()` para instanciar la clase `PokerGame` para simular juegos entre las estrategias la cantidad de veces que se indico en la interfaz incialmente

> ### PokerGame
> La clase `PokerGame` cumple la funcion de realizar los calculos correspondientes al mapeo de las cartas con los numeros aleatorios y de gestionar las distintas desiciones que implementan las variadas estrategias.

## Metodo Monte carlo 
> Es un metodo de aproximacion mediante iteraciones donde se aproxima a un resultado determinando un rango de resultados como satisfactorios y resultados desviados, donde el valor acertado tiene una determina probabilidad de acierto.

## Terminos utilizados
> Durante el transcurso del desarrollo usamos distintos terminos para referirnos a situaciones dentro del juego que se utilizan de manera estandarizada, aca definimos algunos de ellos:
> - Flop: Esto se refiere a las tres primeras cartas comunitarias que se revelan en el centro de la mesa despues de la primera ronda 
> - Turn: Es la segunda carta comunitaria mostrada luego del flop
> - River: Es la tercera carta comunitaria mostrada luego del Turn
> - Win rate: Significa tasa de victorias, dentro del poker se utiliza para indicar la probabilidad de lucro de un jugador en una partida
> - Showdown: Es el final de la mano donde se determina que jugador tiene la mejor mano y por lo tanto gana la ronda 
