# Review de la aplicacion Spacegom

- GRAVE: En la contratación de trabajadores el calculo de los días de búsqueda se resuelve con una tirada de dados, cuando se inicia la busqueda se produce esta tirada de forma automática y se muestra la suma de los dados. Esto NO es el comportamiento deseado, en todas las tiradas de dados se debe dar la opción que el jugador tire los dados fisicamente y proporcione el resultado. Y cuando se escoja tirada automatica SIEMPRE se debe mostrar que ha salido en cada uno de los dados ademas de la suma de los dados. Esto proporciona una sensación de juego más parecida a la que se pretende. DONE
- NECESARIO: En el dahboard principal la información del planeta está codificada. Prefiero que la información sea más explicita. en lugar de el soporte vital como codigo prefiero que se muestre el texto de lo que significa el codigo.Los campos Soporte Vital y Nivel Tecnologico. El campo Espacio puerto debe separarse en los tres valores que lo forman y mostrarse como un texto. DONE
- DESEABLE: Las fechas las prefiero en formato dd-mm-yyyy. DONE
- DESEABLE: Me gustaría que en el dashboard el saldo de tesoreria tenga un codigo de color, en verde si es positivo y vamos a tener para pagar más de 6 meses, en naranja si es positivo pero el numero de mese que vamos a poder pagar está entre 4 y 6 meses, en rojo si es positivo y el numero de meses que vamos a poder pagar es 3 o menos. Si vamos a entrar en negativo en el proximo pago o el siguiente debe cambiarse el color del marco del saldo de tesoreria a rojo. PENDING
- NECESARIO: En el alta de misiones el campo Mundo de Origen debe rellenarse con el mundo actual. DONE
- NECESARIO: En el alta de misiones el campo Lugar de ejecución debe ofrecer la lista de planetas. DISMISS
- DESEABLE: En el alta de misiones el campo fecha Maxima debe estar en formato dd-mm-yyyy. DONE
- NECESARIO: En el alta de misiones el Número de Objetivo debe tener el siguiente entero disponible. DONE
- DESEABLE: Me gustaría que en todas las pantallas hubiera botones de acceso rápido al resto, no solo al Dashboard, quizás tipo pestañas. o botones, lo que sea más fácil. DONE
- DESEABLE: En todas las pantallas ademas del ID de la partida y la fecha, debe aparecer el nombre del mundo actual y el saldo de tesoreria (con su codigo de color). DONE (salvo el codigo de color de Tesoreria)
- DESEABLE: En la pantalla de gestión de personal la fecha del proximo evento debe aparecer en formato dd-mm-yyyy. TODAS las fechas del juego deben aparecer en formato dd-mm-yyyy. DONE
- NECESARIO: En todas las pantallas debe haber a la derecha una zona scrollable con los últimos eventos. DISMISS (en su lugar hemos implementado un log)
- GRAVE: La fecha que aparece en todas las pantallas en la esquina superior derecha no corresponde con la fecha del juego, ni se actualiza con el transcurso del juego. DONE
- DESEABLE: En la pantalla de gestión de personal al presionar el boton de avanzar el tiempo se pide confirmacion mediante un popup, no me gusta, parece un mensaje de error y es feo. DONE
- GRAVE: En la pantalla de gestion de personal en el listado de personal activo la experiencia muestra "Experto" cuando debería decir "Estandar". Los otros estados son correctos. DONE
- GRAVE; Al mostrar el resultado de una contratación se está mostrando el resultado correctamente, pero los modificadores se están mostrando mal, dice en todo caso "MODIFICADORES: 0", aunque luego se están calculando correctamente. DONE
- DESEABLE: En la pantalla de Misiones al presionar el boton de completar en una misión se pide confirmacion mediante un popup, no me gusta, parece un mensaje de error y es feo. DONE
- NECESARIO: En el Dashboard el calendario no muestra el día ni el año solo el mes. DONE
- NECESARIO: Se necesita proporcionar un mecanismo para ver la informacion de otras areas que ya se conozcan. PENDING
- Deseable: Necesitamos una pantalla de entrada que permita seleccionar la partida a la que se desea acceder y borrar partidas si se desea. PENDING
- DESEABLE: No se ve el fondo estrellado en la visualizacion del area. PENDING

## Review 2

- GRAVE: La fecha que aparece en todas las pantallas en la esquina superior derecha no corresponde con la fecha del juego, ni se actualiza con el transcurso del juego. DONE
- NECESARIO: ficheros de codigo demasiado grandes, dificiles de mantener, se recomienda refactorizar el codigo. PENDING

## Review 3

- DETAIL: la zona scrollable con últimos eventos quisiera que fuera una zona de log, donde pudiera ver todos los eventos y consultar el historico, debe ser muy sencilla, fecha del juego: mensaje de texto "Iniciada busqqueda Piloto Novato tardará dos dias" "Se paga los salarios por un total de XX y el saldo resultante es YYY" "Contratado Axistente de vuelo ..." "Fallo en la busqueda de Piloto Experto..." y en el futuro se iria agregando mas eventos. DONE

## Review 4

- DESEABLE: En la tiradas de dados de accciones del personal cuando se muestre el resultado además de Exito o Fracaso se debe indicar si ha habido modificación en la experiencia o la moral.
- NECESARIO: He añadido una nueva busqueda de personal cuando ya había otras y ha añadido el primero en la cola de busqueda, no sé en que circustancias se ha producido, porque las veces anteriores se ha comportado como se esperaba añadiendo al final de la cola.
- NECESARIO: Los ID de los trabajadores deben ser únicos por partida.

## Pagina inicial

La pagina inicial se quedó obsoleta, tiene una primera sección denominada COMMAND CENTER donde me permite iniciar una nueva partida y Acceder a un Panel de control ¡¡Vacio!!

En la parte de abajo tiene un modulo de DICE que no tiene uso y un panel de Mission LOG que juraría que es de atrezzo.

Me gustan los adornos, te introducen en el juego, pero además necesitaría que me dejara continuar con la última partida o acceder a otras. El modulo del dado no sirve ni para dar ambiente.

## Accion de comercio

- NECESARIO: - Detectado problema en embarque de pasajeros sigue permitiendo repetir el embarque en el mismo mundo.

