# Primer objetivo

Ahora en el juego aparece el primer objetivo de la campaña (1), contratar a 1 responsable de soporte a pasajeros, 1 auxiliar de vuelo, 1 negociador de compraventa de mercadería, 1 técnico de mantenimiento de astronaves, 1 tecnico de soportes vitales y 1 abogado.

Tendremos que tener un registro de misiones, hay dos tipos de misiones, Objetivos de Campaña y Misiones Especiales.

las misiones de campaña tienen estos campos:

Número de objetivo, Mundo donde se aceptó el encargo, Lugar donde debe ejecutarse, Fecha máxima, Resultado (exito o fracaso o vacio)

las misiones especiales tienen estos campos:
Codigo de Mision y pagina del libro donde se detalla, Mundo donde se aceptó el encargo, Lugar donde debe ejecutarse, Fecha máxima, Resultado (exito o fracaso o vacio)

Parece que el proceso de contratación es secuencial, solo se produce una busqueda de personal a la vez, y necesita un tiempo variable que hay que tener en cuenta.

la partida comienza en el año 1, mes 1, dia 1, los meses tienen 35 dias, los años, doce meses. Los salarios se pagan el día 35 de cada mes, si en el transcurso de las contrataciones se llega al dia 35 hay que descontar los salarios del saldo de tesoreria (se pierde la partida si el saldo llega a ser negativo: CONDICION DE FINALIZACION, ya que se produce la QUIEBRA a no ser que antes solicites algun prestamo, cosa que se verá más adelante).

Los dias 35 hay que anotar el pago de los salarios, incluidos los de las nuevas contrataciones, que se pagan integros.

La unidad minima de tesorería es 1 SC, se omiten todos los decimales redondeando siempre al alza, al entero superior.

La compañia tiene otro tipo de gastos mensuales, pero en este momento del tutorial se considera que se están abonando, no nos preocuparemos por ello.

## Operacion de contratación de personal.

Solo se puede realizar si estás en MUNDO, si no lo estuvieras tienes que estarlo.

La contratación es un encargo que le haces al director gerente, la busqueda se realiza haceindo tiradas de dados y teniendo en cuenta el nivel de experiencia del director gerente, su moral y la reputación de la empresa.

### Regla para cualquier acccion de cualquier trabajador.

Un trabajador NOVATO tiene un modificador de -1 en todas aquellas tiradas en lsa que su experiencia tenga que ser valorada, uno estandar tiene el modificador de +0 y uno VETERANO tiene un modificador de +1.

Un trabajador con la moral Baja tendrá un modificador de -1, con la moral media de +0 y con la moral alta de +1.

### Reglas para las contrataciones

Los puestos laborables se pueden conseguir dependiendo del MUNDO donde te encuentres:
- Mundo <= 1000 habitantes y nivel tecnológico PRIMITIVO
No se puede contratar ningun tipo de personal.
- Mundo > 1000 habitantes y nivel tecnológico RUDIMENTARIO
-- Abogado						1D6 días	5 SC	8+
-- Agente secreto						2d6 días	25 SC	8+
-- Asistente doméstico				#VALUE!	#VALUE!	1 día	1 SC	4+
-- Auxiliar de vuelo						1 día	2 SC	7+
-- Cocinero				#VALUE!	#VALUE!	1D6 días	3 SC	8+
-- Negociador de compraventa de mercadería						1D6 días	10 SC	8+
-- Operario de logística y almacén				#VALUE!	#VALUE!	1 día	1 SC	6+
-- Político demagogo						2d6 días	30 SC	9+
-- Psicólogo						1D6 días	5 SC	8+
-- Responsable de contabilidad y burocracia				#VALUE!	#VALUE!	1D6 días	3 SC	7+
-- Responsable de soporte a pasajeros						1D6 días	4 SC	7+
-- Responsable de suministros de manutención				#VALUE!	#VALUE!	1D6 días	3 SC	7+
-- Soldado mercenario						2 días	5 SC	7+
-- Recursos Humanos						1D6 dias	5 SC	7+
- Mundo > 1000 habitantes y nivel tecnológico ESPACIAL (además de los anteriores)
-- Ingeniero astronavegación					2d6 días	8 SC	9+
-- Ingeniero computacional				2d6 días	15 SC	8+
-- Médico						1D6 días	7 SC	8+
-- Piloto					2d6 días	10 SC	7+
-- Técnico de mantenimiento de astronaves						1D6 días	6 SC	8+
-- Técnico de repostaje y análisis de combustibles				1D6 días	7 SC	8+
-- Técnico de soportes vitales						1D6 días	5 SC	7+
-- Vicedirector gerente						1D6 días	20 SC	7+
- Mundo > 1000 habitantes y nivel tecnológico INT., POL. o N. SUP. (además de los anteriores)
-- Comandante de hipersaltos						3D6 días	15 SC	9+
-- Científico de terraformación						2d6 días	8 SC	9+
-- Director gerente						2d6 días	20 SC	7+

El primer valor es el tiempo base que tardará el director gerente en encontrarlo, esto se verá afectado por el nivel de experiencia del candidato. El director gerente solo puede buscar un candidato a la vez. Tras dedicar todos los dias correspondientes, hacer lo propio con otro, para el mismo puesto o para otro.

El segundo valor es el salario base que se pagará al candidato, esto se verá afectado por el nivel de experiencia del candidato.

El tercer valor es el que debe igualar o superar el director gerente para contratar al candidato tirando 2d6 y aplicando los modificadores de experiencia y moral del director gerente y la reputación de la empresa.

Ejemplo, el director genrente incial tiene moral Alta y es Veterano y la reputación de la empresa es 0, por lo que el director gerente tiene un modificador de +1 en experiencia y +1 en moral y un modificador de 0 en reputación, por lo que el director gerente tiene un modificador total de +2. que sera lo que se sume al resultado de la tirada de 2d6.

La moral inical de los nuevos trabajadores siempre es Media.

Si buscas un candidato Novato, el sueldo será la mitad del salario base y tardarás la mitad del tiempo base para contratarlo. Si depende de una tirada de dados, primero se tira los dados y despues se divide entre dos redondeando al alza. La duración minima es de un día.

Si buscas un candidato Estandar, el sueldo será el salario base y tardarás el tiempo base para contratarlo.

Si buscas un candidato Veterano, el sueldo será el salario base y tardarás el doble del tiempo base para contratarlo. Si depende de una tirada de dados, primero se tira los dados y despues se multiplica por dos.

Cuando se contrate al candidato habrá que registratarlo en la tabla de personal e incrementar el importe al Total de Salrios mensuales para descontar de la tesorería. 

Se utilizará un nombre aleatorio de la lista de nombres de la tabla de nombres. Aunque se debe permitir que el jugador escriba el nombre del candidato o solicite otro nombre de la lista de nombres.  

### Cambios en la Moral y la Experiencia de los trabajadores.

Siempre que un trabajador efectue una tirada de dados 2d6 está sujeto a lo siguiente:

- ganará 1 nivel de moral si el resultado total, sumado todos los modificadores iguala o supera el valor de 10. Tambien se incrementa la experiencia si obtiene 2 seises en los dados independientemente de los modificadores.
- perderá 1 nivel de moral si el resultado total, sumado todos los modificadores es igual o inferior a 4. 
- No se puede superar el nivel maximo de moral ni el nivel minimo de moral.
- La expercia solo se incrementa, nunca se decrementa. Y no se puede superar el nivel maximo de experiencia.

### Despido de trabajadores.

En todo momento se puede despido de un trabajador (excepcion: durante el Tutorial, se explica maás adelante).

Se puede despedir en cualquier momento, sin coste ni salario, pero la empresa perdera 1 de reputación y el resto del personal bajará si nivel de moral en 1.

Otra forma es abonar la mensualidad y otras 4 mensualidades, en este caso no se produce ninguna penalización.

## Aclaraciones Técnicas para la Implementación

### Sistema de Eventos y Avance del Tiempo

El juego debe implementar un **sistema de cola de eventos ordenados por tiempo**. Los días se saltan automáticamente hasta el siguiente evento:

- Finalización de búsqueda de personal
- Día 35 del mes (pago de salarios)
- Futuros eventos que se añadan

### Proceso Completo de Contratación

1. **Inicio de búsqueda**: El jugador especifica:
   - Puesto a contratar
   - Nivel de experiencia deseado (Novato/Estándar/Veterano)

2. **Cálculo de tiempo de búsqueda**:
   - Se tiran los dados indicados (1D6, 2D6 o 3D6 según el puesto)
   - Para **Novato**: resultado ÷ 2 (redondeando al alza, mínimo 1 día)
   - Para **Estándar**: resultado sin modificar
   - Para **Veterano**: resultado × 2

3. **Espera**: El tiempo avanza hasta que se completa la búsqueda o llega el día 35 (pago de salarios)

4. **Resolución de contratación**:
   - Tirada 2D6 + modificadores del Director Gerente
   - **Modificadores**: Experiencia + Moral + Reputación de la empresa
   - **Éxito**: resultado ≥ objetivo del puesto → se contrata al candidato
   - **Fallo**: se pierde el tiempo invertido, el jugador puede iniciar nueva búsqueda (mismo puesto u otro diferente)

5. **Registro del nuevo empleado**:
   - Nombre aleatorio del sistema de sugerencias (con opción de cambiarlo)
   - Moral inicial: Media
   - Incremento del total de salarios mensuales

### Sistema de Reputación

- **Valor inicial**: 0
- **Rango**: -5 a +5 (según documentación de campaña)
- **Modificador en tiradas**: se suma directamente a las tiradas del Director Gerente
- Ya debe estar o debería estar en el estado del juego y en el dashboard

### Componente de Dados Reusable

Dos modos de operación:
- **Automático**: el sistema tira los dados y muestra el resultado
- **Manual**: el jugador introduce los valores de cada dado individualmente

**Sin animaciones**, solo mostrar el resultado final claramente. Este componente se usará en múltiples fases del juego.

### Ocupación del Director Gerente

Por ahora, el Director Gerente está completamente ocupado durante la búsqueda de personal y no puede realizar otras tareas hasta que finalice.