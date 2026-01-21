# Acción de interacción de "Comercio de mercancías"

> NOTA IMPORTANTE Cuando veamos como viajar, por ahora lo ignoramos: Recuerda que, tanto para aterrizar sobre la superficie de un MUNDO como para amarrar la nave al espaciopuerto o las instalaciones orbitales que pudiera tener, el "piloto" debe efectuar una tirada (ver Est1 2 de "Pasos a seguir si quieres interactuar con el MUNDO de interés" en la página 13 de este libro).
> NOTA IMPORTANTE (por ahora la ignoramos): Comprueba ahora si este MUNDO está ubicado en un CUADRANTE dominado por alguna megacorporación. Esto será así si previamente has escrito algún número rodeado por un círculo en este CUADRANTE (por ejemplo, 1, 2, etc.). En caso de estar controlado por una megacorporación, para poder transportar viajeros deberás tener una Reputación de 5; además, tendrás que lanzar 1D6: Si el resultado es impar no podrás efectuar ninguna interacción de "comercio de mercancías" en esta ocasión. Si deseas intentarlo de nuevo deberás salir del CUADRANTE, volver más adelante y realizar de nuevo la tirada. Si el CUADRANTE no está dominado por alguna megacorporación omite esta nota.
Revisa el marcador situado debajo de la "HOJA DE CUADRANTES (2/2)" y sitúa el clip sobre la posición de "MUNDO" en caso de que no lo estuviera:

## Comercio de mercancías

Para ejecutar la acción de "Comercio de mercancías" tendrás que poner a trabajar al negociador de compraventa de mercadería, que se encargará de comprar o vender mercancías en este MUNDO. Procede de la siguiente forma:

### Comprar mercancías

Para poder ejecutar la acción de "Comercio de mercancías" debes esta situado en la superficie del mundo.

También debes tener al negociador de compraventa de mercadería que se encargará de comprar o vender mercancías en este MUNDO.

Esto es una transcripción de lo que pone el libro, no corresponde con nuestros sistema, **habrá que proporcionar herramientas que cumplan la misma función**. Por ejemplo, en nuestro sistema si una tarea requiere de un tiempo para ser completada creamos un evento en la cola de tareas ordenada por fecha de ejecución y cuando avanzamos el tiempo se resuelve el evento.

Puede haber referencias a imagenes que no están en el texto. Las referencias a documentos se encuentran en el folder "files".

> NOTA: habrá que implementar un sistema para registrar las negociaciones de compra y venta de mercancías. En el documento de papel la tabla "Comercio de mercaderias" tiene los campos que se registran son:

- Mundo donde se COMPRA la mercancía
- Coódigo de producto y numero de UCN
- Importe total de la compra
- Día, mes y año de la COMPRA
- Mundo donde se VENDE la mercancía
- Importe total de la venta
- Día, mes y año de la VENTA
- Ganancia o perdida
- Cumple trazabilidad Convenio Universal Spacegom (si, no)

La tabla "Comercio de mercaderias" TIENE 25 FILAS

Nuestra solución no tiene por que ser identica a la del documento de papel, pero debe cumplir con la misma funcionalidad.

Si quieres comprar mercancías:

1. Comprueba los códigos de producto que podrías COMPRAR en este MUNDO. Estos códigos los habrás marcado con "X" previamente en la tabla "Mundos de esta área" situada debajo de la cuadrícula de CUADRANTES, pero con la siguiente restricción: __no está permitido comprar aquellos productos que adquiriste recientemente en este mismo MUNDO__ y que, por tanto, no le ha dado tiempo a producir. Comprueba la tabla de "Comercio de mercancías", que tienes en la "Hoja de Cuadrantes (1/2)" y puedes ver en la imagen derecha, y **verifica el "Día, mes y año de la COMPRA"** de los productos que compraste aquí; tras ello, mira la fecha actual del Calendario de la campaña y comprueba si, desde tu última compra, han transcurrido los "Días hasta que un MUNDO vuelve a producir ese producto" según la leyenda situada debajo de la tabla anterior y que puedes ver en la imagen de la izquierda. **Si han pasado los días requeridos podrás comprar esos productos; en caso contrario tendrás que esperar los días necesarios hasta que vuelvan a estar disponibles.**
2. En la tabla "Mundos de esta área" situada debajo de la cuadrícula de CUADRANTES, también puedes ver en la imagen de la derecha, comprueba el número máximo de UCN (Unidades de Carga Normalizadas; columna *8 de la tabla) que podrías comprar de cada uno de los códigos de producto anteriores en cada visita. Si, por ejemplo, aparece un valor de 10 UCN, podrías adquirir hasta 10 UCN de cada código de producto disponible (si hubiera 3 códigos de producto distintos, podrías comprar hasta 30 UCN en total, 10 de cada tipo).
3. El negociador de compraventa de mercadería negocia los precios de compra por UCN de cada uno de los códigos de producto disponibles de forma separada. **Necesitará emplear 1 día de trabajo por cada negociación a realizar** (si te interesaran 3 códigos de producto emplearías 3 días). Para negociar, el negociador de compraventa de mercadería lanza 2D6 y aplica sus modificadores según su nivel de experiencia y moral junto con la REPUTACIÓN/2 de tu Compañía (reputación dividida entre 2 redondeando a la baja el resultado; por ejemplo, si la reputación es -5, aplicarías un -2):

- Si el resultado total es inferior a 7, el coste de compra por UCN será igual al "Precio base de COMPRA por UCN" indicado en la leyenda situada debajo de la tabla de "Comercio de mercancías" multiplicado por un factor 1,2 (redondea al alza). El negociador podrá perder moral segun las reglas de moral descritas en el documento [./REGLAS_MORAL_EXPERIENCIA.md](./REGLAS_MORAL_EXPERIENCIA.md).
- Si el resultado está entre 7 y 9, el coste de compra por UCN será igual al "Precio base de compra por UCN" indicado en la leyenda sin multiplicarlo por ningún factor.
- Si el resultado es de 10 o más, el coste de compra por UCN de esa mercancía será igual al "Precio base de compra por UCN" indicado en la leyenda multiplicado por un factor 0,8 (redondea al alza). Además, el negociador de compraventa de mercadería podrá ganar moral y experiencia según lo indicado en la página 36 de este libro en el apartado "Cambios en la Moral y Experiencia de tus trabajadores".

### Tabla de productos y precios de compraventa

| CÓDIGO Producto | Nombre del Producto | Precio base de COMPRA por UCN | Precio base de VENTA por UCN | Días hasta que un MUNDO vuelve a producir ese producto | Días hasta que un MUNDO vuelve a necesitarlo | Ganancia base |
| --- | --- | --- | --- | --- | --- | --- |
| INDU | Productos industriales y manufacturados comunes | 9 SC | 18 SC | 30 | 50 | 50% |
| BASI | Metal, plásticos, productos químicos y otros materiales básicos elaborados | 11 SC | 21 SC | 40 | 50 | 48% |
| ALIM | Productos de alimentación | 4 SC | 11 SC | 30 | 40 | 64% |
| MADE | Madera y derivados | 6 SC | 17 SC | 30 | 50 | 65% |
| AGUA | Agua potable | 2 SC | 5 SC | 20 | 20 | 60% |
| MICO | Minerales comunes | 5 SC | 9 SC | 30 | 50 | 44% |
| MIRA | Minerales raros y materias primas poco comunes | 13 SC | 30 SC | 50 | 60 | 57% |
| MIPR | Metales preciosos, diamantes, gemas, … | 20 SC | 60 SC | 80 | 80 | 67% |
| PAVA | Productos avanzados, computadores modernos, robótica y otros equipos | 15 SC | 30 SC | 40 | 60 | 50% |
| A | Armas hasta etapa espacial | 7 SC | 15 SC | 40 | 40 | 53% |
| AE | Armas a partir de etapa espacial | 10 SC | 23 SC | 60 | 60 | 57% |
| AEI | Armas modernas a partir de etapa interestelar | 20 SC | 45 SC | 80 | 80 | 56% |
| COM | Combustible para astronavegación | 4 SC | 7 SC | 30 | 20 | 43% |

**NOTA: primero negocias el precio y luego decides cuanto compras. Es como una cesta de la compra, añades y luego decides que te quedas y que no!**
4. Tras las negociaciones del punto "3.", elige qué mercancías te interesan y paga el importe correspondiente al coste negociado por el número de UCN que deseas adquirir. Como se ha explicado en el punto "2." existe un máximo de UCN de cada código de producto que puedes adquirir, pero eso no significa que tengas que comprar dicha cantidad. Si lo deseas puedes adquirir un valor menor, pues en este momento aún no se ha efectuado la trazabilidad del pedido. **Cuando realizas la compra es cuando** Resta la cantidad económica total en la TESORERÍA de tu Compañía. Tambien se debe validar que tienes SC para pagar y espacio disponible en el almacen.

5. Anota en la tabla de "Comercio de mercancías" tantas filas como códigos de productos hayas comprado (esta tabla está en la página situada en la "Hoja de Cuadrantes (1/2)" y también puedes verla en la imagen de la derecha). **MUY IMPORTANTE:Cada fila de la mencionada tabla de "Comercio de mercancías" se considera un PEDIDO**. Has de anotar el "MUNDO donde se COMPRA la mercancía", el "Código de producto y número de UCN" adquiridos, el "Importe total de COMPRA" que has pagado en el punto "d" y el "Día, mes y año de la COMPRA". En la última columna de la tabla para este PEDIDO pon un "Sí" si el PEDIDO cumple la trazabilidad del Convenio Universal Spacegom (lo hará si el MUNDO está adscrito a dicho convenio) y pon un "No" en caso contrario. El resto de las columnas de la tabla déjalas vacías por el momento; las rellenarás cuando consigas vender en otro MUNDO la mercancía que acabas de comprar. En este momento tus PEDIDOS habrán quedado registrados en la base de datos global y, a menos que haya un "No" en la última columna, tendrán que cumplir las condiciones de trazabilidad indicadas en la página 24.

**IMPORTANTE:** Si te quedas sin filas vacías en la tabla de "Comercio de mercancías" no podrás efectuar más compras de PEDIDOS en el ÁREA asociada a dicha tabla. El Convenio Universal Spacegom impulsa la máxima libre competencia posible limitando los negocios que una Compañía puede hacer por ÁREA y además promueve el intercambio de mercancías entre CUADRANTES distintos para propiciar la paz a través del comercio entre MUNDOS distantes. Para seguir haciendo compras y poder anotarlas en la tabla de "Comercio de mercancías", tendrías que ir a otra ÁREA y usar la tabla asociada en caso de que tenga filas vacías disponibles. Pero hay una salvedad: podrás realizar más compras de PEDIDOS en el ÁREA, aunque se agoten las filas vacías en la tabla, si las llevas a cabo en MUNDOS no adscritos al Convenio Universal Spacegom. Para ello tendrías que:
 
 - Usar una fila ya rellena de la tabla de "Comercio de mercancías" que contenga el mismo código de producto a comprar pero que aún no se haya vendido.
 - Actualizar en esa fila la columna "Mundo donde se compra la mercancía". Tacha el anterior MUNDO que tuvieras anotado y pon el nombre del nuevo donde ahora compras la mercancía.
 - Actualizar en esa fila la columna "Código de producto y número de UCN". Suma los nuevos productos adquiridos a los UCN que ya aparecían anotados porque los habías comprado previamente, tacha el valor previo y deja anotados los UCN acumulados.
 - Actualizar en esa fila la columna "Importe total de compra". Tacha el valor que había y anota el valor acumulado considerando el valor inicial anotado más el importe de la nueva compra.
 - Actualizar en esa fila la columna "Día, mes y año de la compra". Aquí pondrás la nueva fecha tachando la anterior.
 - Obligatoriamente tendrás que indicar en la última columna que esa fila (y por tanto ese PEDIDO) ya no cumple la trazabilidad del Convenio Universal Spacegom.

**ESTO TAMPOCO SE HA IMPLEMENTADO**

6. Ha llegado el momento de cargar la mercancía comprada a tu Almacén.
Cada UCN adquirido de cada PEDIDO, sea cual sea el código de producto, ocupará espacio en el Almacén de tu astronave. Nunca puedes superar su Capacidad máxima. Lanza 2D6 para cada Operario de logística y almacén que tengas y aplica sus bonificadores o penalizadores según su nivel de experiencia y moral. Si el resultado es de 7 o más, dicho operario cargará en el Almacén 10 UCN en 1 día y podrá ganar moral y experiencia según lo indicado en la página 36 de este libro en el apartado "Cambios en la Moral y Experiencia de tus trabajadores". Si el resultado es menor que 7, ese operario solo cargará 5 UCN en 1 día y podrá perder moral según lo indicado en la página 36 de este libro en el apartado "Cambios en la Moral y Experiencia de tus trabajadores". Haz tantas tiradas y consume tantos días de carga de mercancías como sea necesario hasta cargar el total de UCN. Cuantos más Operarios de logística y almacén dispongas, más UCN podrás cargar por día de trabajo.

7. Ocupa tantos espacios en tu Almacén como UCN carguen tus operarios en el punto previo. Refléjalo en tu ficha mediante los 3 clips de centenas, decenas y unidades en el marcador "Espacios ocupados almacén mercancías". Un PEDIDO puede tener, por ejemplo, 6 UCN de un código de producto, en este caso ocuparías 6 espacios en tu Almacén.
**(obviamente no vamos a usar el mismo mecanismo para reflejar el espacio ocupado en el Almacén que en el marcador de la ficha)**

## Venta de mercancias

Si quieres vender mercancías:

a. Comprueba los códigos de producto que podrías VENDER en este MUNDO. Estos códigos son los que no hayas marcado con "X" previamente en la tabla "Mundos de esta área" situada debajo de la cuadrícula de CUADRANTES, pero con la siguiente restricción: no puedes vender aquellos productos con los que ya comerciaste aquí recientemente porque no ha pasado el tiempo necesario para que el MUNDO los vuelva a demandar. Comprueba la tabla de "Comercio de mercancías" que tienes en la "Hoja de Cuadrantes (1/2)", que también puedes ver en la imagen de la derecha, y verifica el "Día, mes y año de la VENTA" de los productos que vendiste en este mismo MUNDO. Tras ello, mira la fecha actual del calendario de la campaña y verifica si, desde tu última venta, han transcurrido los "Días hasta que un MUNDO vuelve a necesitarlo" según la leyenda situada debajo de la tabla de "Comercio de mercancías" y que también puedes ver en la imagen de la izquierda. Si han transcurrido los días requeridos podrás vender esos productos; en caso contrario deberás esperar a que vuelvan a ser demandados.

b. En la tabla "Mundos de esta área" situada debajo de la cuadrícula de CUADRANTES y que también puedes ver en la imagen de la derecha, comprueba el número máximo de UCN permitidos que podrías VENDER por visita a este MUNDO sea cual sea el código de producto (columna *8 - "Número de UCN por pedido"). Nunca podrás vender, en cada visita a un MUNDO, más UCN que el número máximo permitido. Para volver a vender este producto en este MUNDO, sea cual sea el número de UCN con el que hayas comerciado, tendrás que salir de su CUADRANTE y volver a entrar una vez transcurrido el tiempo mínimo necesario para que haya nueva demanda de ese producto.

c. Si en la tabla de "Comercio de mercancías" tienes PEDIDOS con productos que puedes vender en este MUNDO, podrás intentar vender el total de los UCN de cada PEDIDO de tus productos. No está permitida la venta parcial de los UCN de un PEDIDO, es decir, para vender tendrás que deshacerte de la totalidad de los UCN anotados en cada una de las filas de la tabla de "Comercio de mercancías", salvo que acudas a MUNDOS no adscritos al Convenio Universal Spacegom (ver nota de la página 24).

d. Para cada uno de los PEDIDOS a vender, el negociador de compraventa de mercadería negocia el "Importe total de VENTA" para cada PEDIDO (reflejado en una fila de la tabla de "Comercio de mercancías"). Necesitará emplear 1D6 días de trabajo por cada negociación a realizar. Por ejemplo, si te interesaran vender 3 PEDIDOS emplearías 1D6 días para el primero, 1D6 días para el segundo y otros 1D6 días para el tercero hasta encontrar compradores interesados. Para determinar el precio, el negociador de compraventa de mercadería lanza 2D6 y aplica sus bonificadores o penalizadores según su nivel de experiencia y moral y la REPUTACIÓN/2 de tu Compañía (reputación dividida entre 2 redondeando a la baja el resultado; por ejemplo, si la reputación es -5, aplicarías un -2):
 - Si el resultado es menor de 7, el "Importe total de VENTA" del PEDIDO será igual al "Precio base de VENTA por UCN" de ese código de producto (consulta la leyenda situada debajo de la tabla de "Comercio de mercancías" y en la imagen de la derecha) multiplicado por el número de UCN que tiene el PEDIDO y multiplicado por un factor 0,8 (redondea al alza). Si, por ejemplo, el "Precio base de VENTA" del producto que vas a vender fuera 10 SC y hubiese 5 UCN en ese PEDIDO, el "Importe de VENTA" que podrías pactar sería 10 x 5 x 0,8 = 40 SC. Además, el negociador de compraventa de mercadería podrá perder moral según lo indicado en la página 36 en el apartado "Cambios en la Moral y Experiencia de tus trabajadores".
 - Si el resultado está entre 7 y 9, el "Importe total de VENTA" del PEDIDO será igual al "Precio base de VENTA por UCN" de ese código de producto multiplicado por el número de UCN que tiene el PEDIDO. Si, por ejemplo, el "Precio base de VENTA" del código de producto que vas a vender fuera de 10 SC y hubiese 5 UCN en ese PEDIDO, el "Importe de VENTA" que podrías pactar sería de 10 x 5 = 50 SC.
 - Si el resultado es de 10 o más, el "Importe total de VENTA" del PEDIDO será igual al "Precio base de VENTA por UCN" de ese código de producto multiplicado por el número de UCN que tiene el PEDIDO y multiplicado por un factor 1,2 (redondea al alza). Si, por ejemplo, el "Precio base de VENTA" del código de producto que vas a vender fuera de 10 SC y hubiese 5 UCN en ese PEDIDO, el "Importe de VENTA" que podrías pactar sería de 10 x 5 x 1,2 = 60 SC. Además, el negociador de compraventa de mercadería podrá ganar moral y experiencia según lo indicado en la página 36 de este libro en el apartado "Cambios en la Moral y Experiencia de tus trabajadores".

e. Si te interesa vender el PEDIDO al precio total de venta que consiguió negociar tu negociador de compraventa de mercadería, suma el "Importe total de VENTA" calculado en el punto previo en la TESORERÍA de tu Compañía y acaba de rellenar la fila de la tabla de "Comercio de mercancías" para dicho PEDIDO cumplimentando las columnas "Mundo donde se VENDE la mercancía", "Importe total de VENTA", "Día, mes y año de la VENTA" y "Ganancia o pérdida". La ganancia o pérdida es la resta entre el "Importe total de VENTA" y el "Importe total de COMPRA", que será positivo cuando obtengas ganancias y negativo cuando tengas pérdidas.

f.Ha llegado el momento de descargar de tu Almacén la mercancía vendida.
Lanza 2D6 para cada Operario de logística y almacén que tengas y aplica sus bonificadores o penalizadores según su nivel de experiencia y moral. Si el resultado es de 7 o más, dicho operario podrá descargar del Almacén 10 UCN en 1 día, así como ganar moral y experiencia según lo indicado en la página 36 de este libro en el apartado "Cambios en la Moral y Experiencia de tus trabajadores". Si el resultado es menor que 7, ese operario solo podrá descargar 5 UCN en 1 día y podrá perder moral según lo indicado en la página 36 de este libro en el apartado

**NOTA SOBRE COMPRAR Y VENDER EN CUADRANTES DE AREAS DISTINTAS**

Es perfectamente posible comprar productos en un MUNDO de un AREA y vender dichs productos en otro de otro AREA distnta. En estos casos, anota el "MUNDO donde se vende la mercancia, el importe total de venta y el dia, mes y año de la venta en las fila de la tabla de comenrcio de mercancias en la que apuntaste la compra de dichos productos. Como sabes, hay una tabla de "comercio de mercancias" para cada area. En este supuesto, anotarias los detalles de la venta no en la tabla de "comercio de mercancias" correspondiente a la area de la que procede la venta, sino en la tabla de "comercio de mercancias" correspondiente a la area de la que procede la compra.

## NOTA SOBRE LA VENTA DE PRODUCTOS EN MUNDOS NO ADSCRITOS AL CONVENIO UNIVERSAL SPACEGOM**

**En los MUNDOS que sí están adscritos al Convenio Universal Spacegom:**

  * No puedes efectuar una venta parcial de los UCN que poseas de un PEDIDO. Es decir, para vender tendrás que deshacerte de la totalidad de los UCN anotados en cada una de las filas de la tabla de "Comercio de mercancías" (recuerda que cada fila corresponde a un PEDIDO). El motivo es la elevanda complejidad logística y administrativa que supone gestionar pedidos parciales, además de vulnerar la trazabilidad de las mercaderías requerida por el Convenio Universal Spacegom. Por todo lo dicho, vigila siempre cuántos UCN te interesa comprar de cada tipo de producto y a qué MUNDOS viajas para venderlos, de tal forma que siempre puedas darles salida. En tu día a día, lo habitual será viajar a MUNDOS que sí están adscritos al Convenio Universal Spacegom. En los MUNDOS adscritos al Convenio Universal Spacegom no podrás vender jamás ningún PEDIDO que tenga anotado un "No" en la última columna de la tabla "Comercio de mercancías".

**En los MUNDOS no adscritos al Convenio Universal Spacegom:**

  * Sí podrás hacer ventas parciales rompiendo la trazabilidad de tus PEDIDOS. Anota un "No" en la última columna de la tabla "Comercio de mercancías" en caso de que no lo tuvieran ya previamente. Ten presente que, una vez rompas la trazabilidad, los UCN no vendidos en la transacción parcial habrán de ser ser vendidos obligatoriamente en MUNDOS no adscritos al Convenio Universal Spacegom (son los únicos que aceptan PEDIDOS con un "No" en la última columna de la tabla "Comercio de mercancías").
  * Lo mismo ocurre con PEDIDOS originalmente no sujetos a la trazabilidad y que, por tanto, tengan desde el principio un “No” en la última columna de la tabla “Comercio de mercancías Dichos PEDIDOS no pueden ser vendidos en MUNDOS adscritos al Convenio Universal Spacegom por considerarse ilegales.

Si has hecho una venta parcial de UCN de un PEDIDO en un MUNDO no adscrito al Convenio Universal Spacegom, actualiza en la tabla de "Comercio de mercancías":

  * El número de UCN aún disponibles de ese PEDIDO (columna "Código de producto y número UCN").
  * Borra el valor de la columna "Importe total de compra" (en caso de no haber sido eliminado anteriormente en una venta parcial previa).
  * En estas ventas parciales no anotes nunca nada en las columnas "Importe total de venta" y "Ganancia o pérdida".

Cuando acabes de vender todos los UCN de un PEDIDO que no cumple la trazabilidad del Conveni Universal Spacegom, tacha toda la fila de ese PEDIDO: queda ya inutilizada para nuevas operaciones de este tipo. El riesgo a que el contrabando sea descubierto será tan alto que no tela jugarás efectuando más transacciones asociadas a esa entrada de la tabla.

