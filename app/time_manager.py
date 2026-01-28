"""
Sistema completo de gestión temporal para el juego Spacegom.

Maneja:
- Calendario del juego (Año/Mes/Día) con sistema personalizado
- Operaciones con fechas (sumar, restar, comparar)
- Cola de eventos ordenados por fecha

El calendario del juego usa un sistema personalizado:
- 35 días por mes
- 12 meses por año
- Formato de fechas: "dd-mm-yy" (día-mes-año)

Dependencias:
    - math: Para cálculos de ceil en funciones de contratación
    - typing: Type hints para anotaciones de tipo

Notas de implementación:
    - Calendario personalizado: 35 días/mes, 12 meses/año
    - Formato de fechas: "dd-mm-yy" (día-mes-año)
    - Event Queue: Ordenada por fecha, luego por ID
    - Overflow Handling: Maneja correctamente cambios de mes/año
"""

import math
from typing import Tuple, Optional, List, Dict


class GameCalendar:
    """
    Maneja calendario y operaciones con fechas del juego Spacegom.
    
    El calendario del juego usa un sistema personalizado diferente al calendario
    gregoriano: 35 días por mes y 12 meses por año. Las fechas se representan
    como strings en formato "dd-mm-yy".
    
    Todos los métodos son estáticos ya que son operaciones puras sin estado.
    
    Attributes:
        DAYS_PER_MONTH: Constante con días por mes (35)
        MONTHS_PER_YEAR: Constante con meses por año (12)
    """
    
    DAYS_PER_MONTH = 35  # Días por mes en el calendario del juego
    MONTHS_PER_YEAR = 12  # Meses por año en el calendario del juego
    
    @staticmethod
    def parse_date(date_str: str) -> Tuple[int, int, int]:
        """
        Convierte string de fecha a tupla (año, mes, día).
        
        El formato esperado es "dd-mm-yy" donde:
        - dd: Día del mes (1-35)
        - mm: Mes del año (1-12)
        - yy: Año del juego
        
        Args:
            date_str: Fecha en formato "dd-mm-yy" (ejemplo: "05-01-1")
        
        Returns:
            Tupla (año, mes, día) en ese orden
        
        Example:
            >>> GameCalendar.parse_date("05-01-1")
            (1, 1, 5)
        """
        parts = date_str.split('-')
        day = int(parts[0])    # Primero es día
        month = int(parts[1])  # Segundo es mes
        year = int(parts[2])   # Tercero es año
        return (year, month, day)
    
    @staticmethod
    def date_to_string(year: int, month: int, day: int) -> str:
        """
        Convierte tupla de fecha a string en formato "dd-mm-yy".
        
        Args:
            year: Año del juego
            month: Mes del año (1-12)
            day: Día del mes (1-35)
        
        Returns:
            String en formato "dd-mm-yy" (ejemplo: "05-01-1")
        
        Example:
            >>> GameCalendar.date_to_string(1, 1, 5)
            '05-01-1'
        """
        return f"{day:02d}-{month:02d}-{year}"
    
    @staticmethod
    def add_days(date_str: str, days: int) -> str:
        """
        Añade días a una fecha del juego, manejando overflow de meses y años.
        
        Si al añadir días se supera el límite del mes (35 días), avanza al
        mes siguiente. Si se supera el límite del año (12 meses), avanza al
        año siguiente.
        
        Args:
            date_str: Fecha inicial en formato "dd-mm-yy"
            days: Número de días a añadir (puede ser negativo, ver subtract_days)
        
        Returns:
            Nueva fecha en formato "dd-mm-yy" después de añadir los días
        
        Example:
            >>> GameCalendar.add_days("30-01-1", 10)
            '05-02-1'  # 30 + 10 = 40, overflow a mes siguiente
        """
        year, month, day = GameCalendar.parse_date(date_str)
        
        day += days
        
        # Manejar overflow de días (más de 35 días en el mes)
        while day > GameCalendar.DAYS_PER_MONTH:
            day -= GameCalendar.DAYS_PER_MONTH
            month += 1
            
            # Manejar overflow de meses (más de 12 meses en el año)
            if month > GameCalendar.MONTHS_PER_YEAR:
                month = 1
                year += 1
        
        return GameCalendar.date_to_string(year, month, day)
    
    @staticmethod
    def subtract_days(date_str: str, days: int) -> str:
        """
        Resta días a una fecha del juego, manejando underflow de meses y años.
        
        Si al restar días se queda por debajo del día 1, retrocede al mes
        anterior. Si se queda por debajo del mes 1, retrocede al año anterior.
        
        Args:
            date_str: Fecha inicial en formato "dd-mm-yy"
            days: Número de días a restar
        
        Returns:
            Nueva fecha en formato "dd-mm-yy" después de restar los días
        
        Example:
            >>> GameCalendar.subtract_days("05-02-1", 10)
            '26-01-1'  # 5 - 10 = -5, underflow a mes anterior
        """
        year, month, day = GameCalendar.parse_date(date_str)
        
        day -= days
        
        # Manejar underflow de días (menos de 1 día)
        while day < 1:
            day += GameCalendar.DAYS_PER_MONTH
            month -= 1
            
            # Manejar underflow de meses (menos de mes 1)
            if month < 1:
                month = GameCalendar.MONTHS_PER_YEAR
                year -= 1
        
        return GameCalendar.date_to_string(year, month, day)
    
    @staticmethod
    def compare_dates(date1: str, date2: str) -> int:
        """
        Compara dos fechas del juego.
        
        Compara año, mes y día en ese orden para determinar qué fecha es anterior,
        igual o posterior.
        
        Args:
            date1: Primera fecha en formato "dd-mm-yy"
            date2: Segunda fecha en formato "dd-mm-yy"
        
        Returns:
            -1 si date1 < date2 (date1 es anterior)
             0 si date1 == date2 (fechas iguales)
             1 si date1 > date2 (date1 es posterior)
        
        Example:
            >>> GameCalendar.compare_dates("05-01-1", "10-01-1")
            -1
            >>> GameCalendar.compare_dates("05-01-1", "05-01-1")
            0
        """
        y1, m1, d1 = GameCalendar.parse_date(date1)
        y2, m2, d2 = GameCalendar.parse_date(date2)
        
        if y1 != y2:
            return -1 if y1 < y2 else 1
        if m1 != m2:
            return -1 if m1 < m2 else 1
        if d1 != d2:
            return -1 if d1 < d2 else 1
        return 0
    
    @staticmethod
    def is_day_35(date_str: str) -> bool:
        """
        Verifica si la fecha es día 35 (día de pago de salarios).
        
        El día 35 es el último día de cada mes y es cuando se pagan los salarios
        del personal. Esta función se usa para detectar cuándo procesar pagos.
        
        Args:
            date_str: Fecha a verificar en formato "dd-mm-yy"
        
        Returns:
            True si es día 35, False en caso contrario
        
        Example:
            >>> GameCalendar.is_day_35("35-01-1")
            True
            >>> GameCalendar.is_day_35("05-01-1")
            False
        """
        _, _, day = GameCalendar.parse_date(date_str)
        return day == 35
    
    @staticmethod
    def next_day_35(date_str: str) -> str:
        """
        Retorna la fecha del próximo día 35 (próximo pago de salarios).
        
        Si la fecha actual es antes del día 35 del mes actual, retorna el día 35
        del mes actual. Si ya es día 35 o posterior, retorna el día 35 del mes
        siguiente.
        
        Args:
            date_str: Fecha actual en formato "dd-mm-yy"
        
        Returns:
            Fecha del próximo día 35 en formato "dd-mm-yy"
        
        Example:
            >>> GameCalendar.next_day_35("05-01-1")
            '35-01-1'  # Día 35 del mes actual
            >>> GameCalendar.next_day_35("35-01-1")
            '35-02-1'  # Día 35 del mes siguiente
        """
        year, month, day = GameCalendar.parse_date(date_str)
        
        if day < 35:
            # Dentro del mismo mes
            return GameCalendar.date_to_string(year, month, 35)
        else:
            # Mes siguiente
            month += 1
            if month > GameCalendar.MONTHS_PER_YEAR:
                month = 1
                year += 1
            return GameCalendar.date_to_string(year, month, 35)
    
    @staticmethod
    def days_between(date1: str, date2: str) -> int:
        """
        Calcula el número de días entre dos fechas.
        
        Convierte ambas fechas a días absolutos desde el inicio del calendario
        (año 1, mes 1, día 1) y calcula la diferencia.
        
        Args:
            date1: Fecha inicial en formato "dd-mm-yy"
            date2: Fecha final en formato "dd-mm-yy"
        
        Returns:
            Número de días entre las fechas:
            - Positivo si date2 > date1 (date2 es posterior)
            - Negativo si date2 < date1 (date2 es anterior)
            - Cero si las fechas son iguales
        
        Example:
            >>> GameCalendar.days_between("05-01-1", "10-01-1")
            5
            >>> GameCalendar.days_between("10-01-1", "05-01-1")
            -5
        """
        y1, m1, d1 = GameCalendar.parse_date(date1)
        y2, m2, d2 = GameCalendar.parse_date(date2)
        
        # Convertir fechas a días absolutos desde año 1, mes 1, día 1
        days1 = (y1 - 1) * GameCalendar.MONTHS_PER_YEAR * GameCalendar.DAYS_PER_MONTH
        days1 += (m1 - 1) * GameCalendar.DAYS_PER_MONTH
        days1 += d1
        
        days2 = (y2 - 1) * GameCalendar.MONTHS_PER_YEAR * GameCalendar.DAYS_PER_MONTH
        days2 += (m2 - 1) * GameCalendar.DAYS_PER_MONTH
        days2 += d2
        
        return days2 - days1


class EventQueue:
    """
    Gestor de cola de eventos ordenados por fecha.
    
    Maneja una lista de eventos futuros que deben procesarse en fechas específicas.
    Los eventos se ordenan automáticamente por fecha (año, mes, día) y luego por ID
    para mantener un orden determinístico.
    
    Todos los métodos son estáticos ya que operan sobre listas pasadas como parámetros.
    La cola se mantiene ordenada después de cada operación.
    """
    
    @staticmethod
    def add_event(events: List[Dict], event_type: str, date: str, data: Dict) -> List[Dict]:
        """
        Añade un evento a la cola y la ordena por fecha + ID.
        
        Asigna un ID secuencial al evento y lo añade a la lista. Luego ordena
        la lista completa por fecha (año, mes, día) y luego por ID para mantener
        un orden determinístico cuando hay eventos en la misma fecha.
        
        Args:
            events: Lista actual de eventos (se modifica in-place)
            event_type: Tipo de evento que mapea a un handler (ej: "salary_payment", "task_completion")
            date: Fecha del evento en formato "dd-mm-yy"
            data: Diccionario con datos específicos del evento
        
        Returns:
            Lista de eventos actualizada y ordenada (misma referencia que events)
        
        Example:
            >>> events = []
            >>> EventQueue.add_event(events, "salary_payment", "35-01-1", {"amount": 500})
            [{'id': 1, 'type': 'salary_payment', 'date': '35-01-1', 'data': {'amount': 500}}]
        """
        # Calcular próximo ID secuencial
        next_id = max([e.get("id", 0) for e in events], default=0) + 1
        
        event = {
            "id": next_id,
            "type": event_type,
            "date": date,
            "data": data
        }
        events.append(event)
        
        # Ordenar por fecha (tupla año,mes,día), luego por ID para orden determinístico
        events.sort(key=lambda e: (GameCalendar.parse_date(e["date"]), e.get("id", 0)))
        
        return events
    
    @staticmethod
    def get_next_event(events: List[Dict]) -> Optional[Dict]:
        """
        Obtiene el próximo evento (el primero en la cola ordenada).
        
        Como la cola está ordenada por fecha, el primer evento es siempre
        el próximo a procesar.
        
        Args:
            events: Lista de eventos ordenada por fecha
        
        Returns:
            Próximo evento (diccionario) o None si la cola está vacía
        """
        if not events:
            return None
        
        # Ya está ordenada, retornar el primero
        return events[0]
    
    @staticmethod
    def remove_event(events: List[Dict], event: Dict) -> List[Dict]:
        """
        Elimina un evento específico de la cola.
        
        Args:
            events: Lista de eventos (se modifica in-place)
            event: Evento a eliminar (debe ser la misma referencia o igual)
        
        Returns:
            Lista actualizada (misma referencia que events)
        """
        if event in events:
            events.remove(event)
        return events
    
    @staticmethod
    def get_events_by_type(events: List[Dict], event_type: str) -> List[Dict]:
        """
        Filtra eventos por tipo.
        
        Útil para encontrar todos los eventos de un tipo específico, por ejemplo
        para verificar si ya existe un evento de pago de salarios.
        
        Args:
            events: Lista de eventos
            event_type: Tipo de evento a filtrar
        
        Returns:
            Lista de eventos del tipo especificado (nueva lista, no modifica events)
        """
        return [e for e in events if e["type"] == event_type]


def calculate_hire_time(dice_formula: str, experience_level: str, dice_roller) -> int:
    """
    Calcula el tiempo de búsqueda de contratación según fórmula y nivel de experiencia.
    
    El tiempo base se calcula desde una fórmula de dados (ej: "2d6") o un número fijo.
    Luego se aplica un modificador según el nivel de experiencia:
    - Novato: ceil(base/2) - Mitad del tiempo base
    - Estándar: base - Tiempo base sin modificar
    - Veterano: base * 2 - Doble del tiempo base
    
    Args:
        dice_formula: Fórmula de dados ("1d6", "2d6") o número fijo como string ("3")
        experience_level: Nivel de experiencia ("Novato", "Estándar", "Veterano")
        dice_roller: Instancia de DiceRoller para tirar dados si es necesario
    
    Returns:
        Días de búsqueda (mínimo 1 día)
    
    Example:
        >>> calculate_hire_time("2d6", "Novato", dice_roller)
        3  # Si 2d6 = 6, entonces ceil(6/2) = 3
        >>> calculate_hire_time("3", "Veterano", dice_roller)
        6  # 3 * 2 = 6
    """
    # Si es un número fijo
    if dice_formula.isdigit():
        base_days = int(dice_formula)
    else:
        # Tirar dados - parse formula like "1d6" or "2d6"
        parts = dice_formula.lower().split('d')
        num_dice = int(parts[0])
        if len(parts) > 1:
            sides = int(parts[1])
        else:
            sides = 6
        result = dice_roller.roll_dice(num_dice, sides)
        base_days = sum(result)
    
    # Aplicar modificador de experiencia
    if experience_level == "Novato":
        search_days = math.ceil(base_days / 2)  # Mitad redondeando al alza
    elif experience_level == "Veterano":
        search_days = base_days * 2  # Doble
    else:  # Estándar
        search_days = base_days
    
    # Mínimo 1 día
    return max(1, search_days)


def calculate_hire_salary(base_salary: int, experience_level: str) -> int:
    """
    Calcula el salario según nivel de experiencia.
    
    Aplica un modificador al salario base según el nivel de experiencia:
    - Novato: ceil(base/2) - Mitad del salario base
    - Estándar: base - Salario base sin modificar
    - Veterano: base * 2 - Doble del salario base
    
    Args:
        base_salary: Salario base del puesto en Créditos Spacegom (SC)
        experience_level: Nivel de experiencia ("Novato", "Estándar", "Veterano")
    
    Returns:
        Salario final en SC (sin decimales, redondeado al alza para Novatos)
    
    Example:
        >>> calculate_hire_salary(100, "Novato")
        50  # ceil(100/2) = 50
        >>> calculate_hire_salary(100, "Estándar")
        100  # Sin modificar
        >>> calculate_hire_salary(100, "Veterano")
        200  # 100 * 2 = 200
    """
    if experience_level == "Novato":
        salary = math.ceil(base_salary / 2)  # Mitad redondeando al alza
    elif experience_level == "Veterano":
        salary = base_salary * 2  # Doble
    else:  # Estándar
        salary = base_salary
    
    return salary
