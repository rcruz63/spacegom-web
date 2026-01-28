"""
Utilidades de tiradas de dados para el juego Spacegom.

Este módulo proporciona utilidades para todas las mecánicas de dados del juego.
Maneja tiradas automáticas y manuales, generación de códigos de planetas, y conversión
de resultados.

Dependencias:
    - random: Generación de números aleatorios
    - typing: Type hints para anotaciones de tipo
"""
import random
from typing import List, Tuple, Optional, Dict, Any


class DiceRoller:
    """
    Clase para manejar todas las tiradas de dados del juego Spacegom.
    
    Proporciona métodos estáticos para:
    - Tiradas de dados genéricas (soporta diferentes números de caras)
    - Generación de códigos de planetas (3d6, rango 111-666)
    - Conversión de resultados a códigos
    - Cálculo de densidad de mundos desde tiradas 2d6
    
    Notas de implementación:
        - Soporta tiradas manuales (dados físicos) y automáticas
        - Implementa secuencia 3d6 para búsqueda consecutiva de planetas
        - Validación de límites de dados (1-6 para dados estándar)
        - Integración con sistema de logging de GameState
    """
    
    @staticmethod
    def roll_dice(num_dice: int = 1, sides: int = 6) -> List[int]:
        """
        Tira múltiples dados y retorna resultados en orden.
        
        Soporta dados con diferentes números de caras, aunque por defecto usa d6.
        Los resultados se retornan en el orden en que fueron generados.
        
        Args:
            num_dice: Número de dados a tirar (default: 1)
            sides: Número de caras por dado (default: 6)
        
        Returns:
            Lista de resultados en orden, cada uno entre 1 y sides
        
        Example:
            >>> DiceRoller.roll_dice(2, 6)
            [4, 6]
            >>> DiceRoller.roll_dice(3, 6)
            [1, 3, 5]
        """
        return [random.randint(1, sides) for _ in range(num_dice)]
    
    @staticmethod
    def roll_for_planet_code(manual_results: Optional[List[int]] = None) -> Tuple[int, List[int]]:
        """
        Genera código de planeta tirando 3d6 (rango 111-666).
        
        El código de planeta se compone concatenando los tres resultados de dados.
        Por ejemplo: [4, 6, 6] -> código 466.
        
        Args:
            manual_results: Lista opcional de 3 resultados manuales (dados físicos).
                           Si se proporciona, se usa en lugar de tirar automáticamente.
        
        Returns:
            Tupla (código_planeta, lista_resultados)
            - código_planeta: Entero entre 111 y 666
            - lista_resultados: Lista de 3 enteros (valores de cada dado)
        
        Example:
            >>> DiceRoller.roll_for_planet_code([1, 1, 1])
            (111, [1, 1, 1])
            >>> DiceRoller.roll_for_planet_code()
            (456, [4, 5, 6])  # Ejemplo de resultado aleatorio
        """
        if manual_results and len(manual_results) == 3:
            results = manual_results
        else:
            results = DiceRoller.roll_dice(num_dice=3, sides=6)
        
        # Compone código concatenando los tres dígitos (ej: [4, 6, 6] -> 466)
        code = int(f"{results[0]}{results[1]}{results[2]}")
        
        return code, results
    
    @staticmethod
    def format_results(results: List[int]) -> str:
        """
        Formatea resultados de dados para visualización.
        
        Convierte una lista de resultados en un string legible con formato
        "dado1 + dado2 + dado3".
        
        Args:
            results: Lista de resultados de dados
        
        Returns:
            String formateado (ej: "4 + 6 + 6")
        
        Example:
            >>> DiceRoller.format_results([4, 6, 6])
            '4 + 6 + 6'
        """
        return " + ".join(map(str, results))
    
    @staticmethod
    def results_to_code(results: List[int]) -> int:
        """
        Convierte lista de 3 resultados a código de planeta.
        
        Args:
            results: Lista de exactamente 3 enteros (valores 1-6)
        
        Returns:
            Código de planeta (111-666)
        
        Raises:
            ValueError: Si la lista no tiene exactamente 3 elementos
        
        Example:
            >>> DiceRoller.results_to_code([4, 6, 6])
            466
        """
        if len(results) != 3:
            raise ValueError("Need exactly 3 dice results for planet code")
        return int(f"{results[0]}{results[1]}{results[2]}")
    
    @staticmethod
    def world_density_from_roll(total: int) -> str:
        """
        Convierte total de 2d6 a nivel de densidad de mundos.
        
        Según las reglas del juego:
        - Total 2-4: Densidad Baja
        - Total 5-9: Densidad Media
        - Total 10-12: Densidad Alta
        
        Args:
            total: Suma de 2d6 (rango válido: 2-12)
        
        Returns:
            "Baja", "Media", o "Alta"
        
        Example:
            >>> DiceRoller.world_density_from_roll(3)
            'Baja'
            >>> DiceRoller.world_density_from_roll(7)
            'Media'
            >>> DiceRoller.world_density_from_roll(11)
            'Alta'
        """
        if total <= 4:
            return "Baja"
        elif total <= 9:
            return "Media"
        else:
            return "Alta"
            
    @staticmethod
    def get_next_planet_code(code: int) -> int:
        """
        Obtiene el siguiente código válido en la secuencia 3d6 para búsqueda consecutiva.
        
        Implementa la lógica de incremento manual según el manual de juego:
        - Incrementa el tercer dado primero (111 → 112 → ... → 116)
        - Cuando el tercer dado llega a 6, se reinicia a 1 y avanza el segundo dado
        - Cuando el segundo dado llega a 6, se reinicia a 1 y avanza el primer dado
        - Si el primer dado llega a 6, se reinicia a 1 (wrap around)
        
        Esta función se usa cuando un planeta no es apto para inicio y se necesita
        consultar el siguiente código en orden.
        
        Secuencia ejemplo: 111 → 112 → 113 → ... → 116 → 121 → 122 → ... → 166 → 211 → ...
        
        Args:
            code: Código de planeta actual (111-666)
            
        Returns:
            Siguiente código de planeta en la secuencia (111-666)
            
        Note:
            Si el código no tiene 3 dígitos, retorna 111 por defecto.
        
        Example:
            >>> DiceRoller.get_next_planet_code(111)
            112
            >>> DiceRoller.get_next_planet_code(116)
            121
            >>> DiceRoller.get_next_planet_code(666)
            111  # Wrap around
        """
        s = str(code)
        if len(s) != 3:
            return 111  # Código mínimo por defecto
            
        # Extraer cada dígito (cada dado representa un valor 1-6)
        d1, d2, d3 = int(s[0]), int(s[1]), int(s[2])
        
        # Incrementar el tercer dado primero
        d3 += 1
        if d3 > 6:
            d3 = 1  # Reiniciar a 1
            d2 += 1  # Avanzar el segundo dado
            if d2 > 6:
                d2 = 1  # Reiniciar a 1
                d1 += 1  # Avanzar el primer dado
                if d1 > 6:
                    d1 = 1  # Wrap around (volver al inicio de la secuencia)
                    
        return d1 * 100 + d2 * 10 + d3


class DiceHistoryEntry:
    """
    Representa una entrada individual en el historial de tiradas de dados.
    
    Almacena información completa sobre una tirada para su posterior consulta
    y análisis. Se integra con el sistema de logging de GameState.
    
    Attributes:
        num_dice: Número de dados tirados
        results: Lista de resultados individuales de cada dado
        total: Suma total de todos los resultados
        is_manual: True si fue una tirada manual (dados físicos), False si fue automática
        purpose: Propósito o descripción de la tirada (para debugging y logs)
    
    Example:
        >>> entry = DiceHistoryEntry(2, [4, 6], False, "Negociación de compra")
        >>> entry.total
        10
        >>> entry.to_dict()
        {'num_dice': 2, 'results': [4, 6], 'total': 10, 'is_manual': False, 'purpose': 'Negociación de compra'}
    """
    
    def __init__(self, num_dice: int, results: List[int], is_manual: bool, purpose: str = ""):
        """
        Inicializa una entrada del historial de tiradas.
        
        Args:
            num_dice: Número de dados tirados
            results: Lista de resultados individuales
            is_manual: True si fue tirada manual, False si fue automática
            purpose: Descripción del propósito de la tirada (opcional)
        """
        self.num_dice = num_dice
        self.results = results
        self.total = sum(results)
        self.is_manual = is_manual
        self.purpose = purpose
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna representación diccionario para serialización.
        
        Útil para guardar en JSON o enviar como respuesta API.
        
        Returns:
            Diccionario con todos los atributos de la entrada
        """
        return {
            "num_dice": self.num_dice,
            "results": self.results,
            "total": self.total,
            "is_manual": self.is_manual,
            "purpose": self.purpose
        }
