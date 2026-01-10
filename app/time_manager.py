"""
Sistema de gestión temporal para el juego Spacegom

Maneja:
- Calendario del juego (Año/Mes/Día)
- Operaciones con fechas
- Cola de eventos ordenados
"""

import math
from typing import Tuple, Optional, List, Dict


class GameCalendar:
    """Maneja calendario y eventos del juego Spacegom"""
    
    DAYS_PER_MONTH = 35
    MONTHS_PER_YEAR = 12
    
    @staticmethod
    def parse_date(date_str: str) -> Tuple[int, int, int]:
        """
        Convierte fecha en string a tupla (año, mes, día)
        
        Args:
            date_str: Fecha en formato "1-01-05" o "1-1-5"
        
        Returns:
            Tupla (año, mes, día)
        """
        parts = date_str.split('-')
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        return (year, month, day)
    
    @staticmethod
    def date_to_string(year: int, month: int, day: int) -> str:
        """
        Convierte tupla de fecha a string
        
        Args:
            year, month, day: Componentes de la fecha
        
        Returns:
            String en formato "1-01-05"
        """
        return f"{year}-{month:02d}-{day:02d}"
    
    @staticmethod
    def add_days(date_str: str, days: int) -> str:
        """
        Añade días a una fecha del juego
        
        Args:
            date_str: Fecha inicial en formato "1-01-05"
            days: Número de días a añadir
        
        Returns:
            Nueva fecha en formato string
        """
        year, month, day = GameCalendar.parse_date(date_str)
        
        day += days
        
        # Manejar overflow de días
        while day > GameCalendar.DAYS_PER_MONTH:
            day -= GameCalendar.DAYS_PER_MONTH
            month += 1
            
            # Manejar overflow de meses
            if month > GameCalendar.MONTHS_PER_YEAR:
                month = 1
                year += 1
        
        return GameCalendar.date_to_string(year, month, day)
    
    @staticmethod
    def subtract_days(date_str: str, days: int) -> str:
        """
        Resta días a una fecha del juego
        
        Args:
            date_str: Fecha inicial
            days: Número de días a restar
        
        Returns:
            Nueva fecha en formato string
        """
        year, month, day = GameCalendar.parse_date(date_str)
        
        day -= days
        
        # Manejar underflow de días
        while day < 1:
            day += GameCalendar.DAYS_PER_MONTH
            month -= 1
            
            # Manejar underflow de meses
            if month < 1:
                month = GameCalendar.MONTHS_PER_YEAR
                year -= 1
        
        return GameCalendar.date_to_string(year, month, day)
    
    @staticmethod
    def compare_dates(date1: str, date2: str) -> int:
        """
        Compara dos fechas
        
        Args:
            date1, date2: Fechas a comparar
        
        Returns:
            -1 si date1 < date2
             0 si date1 == date2
             1 si date1 > date2
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
        Verifica si la fecha es día 35 (día de pago de salarios)
        
        Args:
            date_str: Fecha a verificar
        
        Returns:
            True si es día 35
        """
        _, _, day = GameCalendar.parse_date(date_str)
        return day == 35
    
    @staticmethod
    def next_day_35(date_str: str) -> str:
        """
        Retorna la fecha del próximo día 35
        
        Args:
            date_str: Fecha actual
        
        Returns:
            Fecha del próximo día 35
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
        Calcula días entre dos fechas
        
        Args:
            date1: Fecha inicial
            date2: Fecha final
        
        Returns:
            Número de días (positivo si date2 > date1, negativo si date2 < date1)
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
    """Gestor de cola de eventos ordenados por fecha"""
    
    @staticmethod
    def add_event(events: List[Dict], event_type: str, date: str, data: Dict) -> List[Dict]:
        """
        Añade un evento a la cola y la ordena
        
        Args:
            events: Lista actual de eventos
            event_type: Tipo de evento ("task_completion", "salary_payment", etc.)
            date: Fecha del evento
            data: Datos específicos del evento
        
        Returns:
            Lista de eventos actualizada y ordenada
        """
        event = {
            "type": event_type,
            "date": date,
            "data": data
        }
        events.append(event)
        
        # Ordenar por fecha
        events.sort(key=lambda e: GameCalendar.parse_date(e["date"]))
        
        return events
    
    @staticmethod
    def get_next_event(events: List[Dict]) -> Optional[Dict]:
        """
        Obtiene el próximo evento (el primero en la cola)
        
        Args:
            events: Lista de eventos
        
        Returns:
            Próximo evento o None si la cola está vacía
        """
        if not events:
            return None
        
        # Ya está ordenada, retornar el primero
        return events[0]
    
    @staticmethod
    def remove_event(events: List[Dict], event: Dict) -> List[Dict]:
        """
        Elimina un evento de la cola
        
        Args:
            events: Lista de eventos
            event: Evento a eliminar
        
        Returns:
            Lista actualizada
        """
        if event in events:
            events.remove(event)
        return events
    
    @staticmethod
    def get_events_by_type(events: List[Dict], event_type: str) -> List[Dict]:
        """
        Filtra eventos por tipo
        
        Args:
            events: Lista de eventos
            event_type: Tipo a filtrar
        
        Returns:
            Lista de eventos del tipo especificado
        """
        return [e for e in events if e["type"] == event_type]


def calculate_hire_time(dice_formula: str, experience_level: str, dice_roller) -> int:
    """
    Calcula el tiempo de búsqueda según fórmula de dados y nivel de experiencia
    
    Args:
        dice_formula: Formula de dados ("1d6", "2d6", "3" para fijo)
        experience_level: "Novato", "Estándar", "Veterano"
        dice_roller: Instancia de DiceRoller
    
    Returns:
        Días de búsqueda (mínimo 1)
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
    Calcula el salario según nivel de experiencia
    
    Args:
        base_salary: Salario base del puesto
        experience_level: "Novato", "Estándar", "Veterano"
    
    Returns:
        Salario final (sin decimales, redondeado al alza)
    """
    if experience_level == "Novato":
        salary = math.ceil(base_salary / 2)  # Mitad redondeando al alza
    elif experience_level == "Veterano":
        salary = base_salary * 2  # Doble
    else:  # Estándar
        salary = base_salary
    
    return salary
