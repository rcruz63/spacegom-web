# Reglas de Evolución de Moral y Experiencia

Este documento define las reglas universales que aplican **siempre** que un empleado realiza una acción que requiere una tirada de dados (2d6).

## Principios Generales

Cualquier acción resuelta mediante una tirada de dados puede afectar el estado emocional (Moral) y profesional (Experiencia) del empleado que la ejecuta.

### 1. Cambio de Moral

La moral cambia según el **Resultado Total** de la acción (Suma de Dados + Modificadores).

*   **Ganancia de Moral**: Si el **Resultado Total** es **>= 10**.
    *   El empleado sube un nivel de moral (Baja -> Media -> Alta).
    *   Si ya tiene moral Alta, no hay cambios.
*   **Pérdida de Moral**: Si el **Resultado Total** es **<= 4**.
    *   El empleado baja un nivel de moral (Alta -> Media -> Baja).
    *   Si ya tiene moral Baja, no hay cambios.
*   **Sin Cambio**: Si el resultado está entre 5 y 9.

### 2. Aumento de Experiencia

La experiencia cambia exclusivamente según el **Resultado Natural de los Dados**, sin modificadores.

*   **Ganancia de Experiencia**: Si se obtiene un **doble 6 natural** en los dados (6, 6).
    *   El empleado sube un nivel de experiencia (Novato -> Experto -> Veterano).
    *   Si ya es Veterano, no hay cambios.
*   **Nota**: La experiencia **nunca disminuye**.

## Implementación Técnica

El sistema debe proveer un módulo común que reciba:
1.  El empleado (o su ID).
2.  Los valores de los dados (para verificar el doble 6).
3.  El resultado total final (para verificar moral).

Este módulo debe devolver un reporte con los cambios aplicados (ej: "Moral: Media -> Alta") para ser mostrado al usuario junto con el resultado de la acción.
