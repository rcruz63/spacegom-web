# Transporte de pasajeros

## Requisito 
La nave debe encontrarse en un mundo y situado en la superficie. En el dashboard se distingue entre varias localizaciones en un planeta: Mundo, Puerto (EspacioPuerto), Orbital (Instalación Orbital), En Ruta (a la Estacion de HiperDisparo) y Estación (de HiperDisparo).

## NOTA IMPORTANTE

En este momento del desarrollo, el setup inicial nos encontramos en la superficie de nuestro planeta base, pero más adelante en el juego visitaremos otros planetas y entonces tendremos que tener en cuenta que tanto para aterrizar en el planeta como para amarrar la nave al EspacioPuerto o a las Instalaciones Orbitales el "piloto" debe efectuar una tirada de dados (ya lo describiremos más adelante). 

Tambien habrá que comprobar si hay MEGACORPORACIONES, en este momento no vamos a implementar nada al repecto, pero más adelante tendremos que tenerlo en cuenta.

## Acción "Transporte de basajeros"

Para ejecutar la accion de transporte de pasajeros hay que proceder de la siguiente manera:

1. Se lanza 2D6 (el procedimeinto es muy similar al que se uso para la busqueda de personal) aplicando los bonificadores del responsable de soporte a pasajeros segun su nivel de experiencia, moral y reputación/2 de la compañía.

* Si el resultado es inferior a 7, se obtiene la mitad de pasajeros promedio indicados en la información del planeta, redondeando decimales a la baja. Se alojan los pasajeros que se desen siempre que la la cantidad no supere el aforo disponible en la nave. Además, el responsable de soporte a pasjeros podrá perder moral segun lo explicado en el documento @primer_objetivo.md en el parrafo "Cambios en la Moral y la Experiencia de los trabajadores", esto será una costante en el juego en todas las acciones.
* Si el resultado es entre 7 y 9, se obtendran exactamente la cantidad promedio que se refleja en la información del planeta, se alojaran los que el jugador quiera siempre que no se supere la capacidad de la nave.
* Si el resultado es entre 10 y 12, se obtendran el doble de la cantidad promedio que se refleja en la información del planeta, se alojaran los que el jugador quiera siempre que no se supere la capacidad de la nave. Además el responable de soporte a pasajeros podrá ganar moral y experiencia segun lo explicado en el documento @primer_objetivo.md en el parrafo "Cambios en la Moral y la Experiencia de los trabajadores", esto será una costante en el juego en todas las acciones.

2. Si tienes 3 auxiliares de vuelo en la plantilla se podrán dar mejores servicios a los pasajeros y cobrar más por ello. Si tienes tres auxiliares multiplica el numero de pasajeros alojados po 4 SC (importe de un pasaje), si tienes 2 auxiliares, multiplica el numero de psajeros por 3 SC, si tienes 1 auxiliar de vuelo, multiplica por 2 SC y si no tienes auxiliares de vuelo, multiplica por 1 SC.

3. Por cada auxiliar de vuelo de nivel "novato" resta 5 SC al total calculado y por cada auxiliar de vuelo con experiencia "veterano" suma 5 SC al total calculado.

4. Se suma la cantidad obtenida a la tesorería. Los pasajes se cobran por adelantado. Se entiende que los pasajeros abandona tu nae al llegar al proximo planeta, no se puede conseguir más pasajeros en este mundo hasta que no se va a otro cuadrante y se regrese, en cuyo caso hay que volver a repetir el procedimiento.

## Decisiones del juego

Cuando estemos en un mundo, el jugador podrá ejecutar algunas acciones, las acciones disponibles son:

- Transporte de pasajeros
- comercio de mercancias
- Misiones especiales
- Adquisición de equipo y material
- contratación de personal
- Interacciones en el Espaciopuerto, si existe
- Interacciones en las Instalaciones Orbitales, si existen

Algunas acciones ya las tenemos implementadas en el juego, como por ejemplo la contratación de personal, que se realiza en la pantalla de personal o la de Misiones especiales, que se realiza en la pantalla de Misiones.Pero ahora mismo no tenemos forma de indicar el resto de acciones en el dashboard.

Lo iremos resolviendo poco a poco.

Para el Transporte de pasajeros debemos incluir en el dasboard un control que nos muestre el numero de pasajeros que se pueden alojar en la nave y el numero de pasajeros alojados. Debemos incluir un boton de acción para ejecutar la acción de Transporte de pasajeros.

## Ejecución de la acción

Cuando se contrata personal se produce tambien una tirada de dados para resolver la contratación, se realiza cuando se avanza el tiempo y se produce el evento de contratación.

Al ejecutar la acción de Transporte de pasajeros se debe mostrar el mismo modulo de tirada de dados, que permite al usaurio usar una tirada automática o manual, muestra el resultado de la tirada, aplica los modificadores y muestra el resultado final.

no sé si podemos usar la misma o tendremos que crear una nueva ya que la información del resultado es diferente.

En este caso debemos decir el numero de pasajeros que se podrían alojar en la nave, el numero de pasajeros que finalmente se alojaron y el importe total de los pasajes. Tambien debemos proporcionar informacion de los modificadores aplicados y si ha habido cambios en la moral o la experienciadel responsable de soporte a pasajeros.

