# Sistema Unificado de Dados - Estado Actual y Recomendaciones

## 📊 Estado Actual del Sistema de Dados

Después de revisar todo el código del proyecto, el sistema de dados **NO es coherente** y tiene múltiples implementaciones paralelas. A continuación, el análisis completo:

---

## 🔍 Implementaciones Existentes

### 1. **DiceRoller (Python Backend)**
**Ubicación**: [`app/dice.py`](docs/dice.md)

**Características**:
- ✅ Clase `DiceRoller` con métodos estáticos
- ✅ Generación automática de dados
- ✅ Soporte para dados manuales
- ✅ Utilidades para códigos planetarios (3d6)
- ✅ Conversión de densidad de mundos (2d6)
- ✅ Historial de tiradas (`DiceHistoryEntry`)

**Uso**: Principalmente en setup inicial y algunos endpoints

### 2. **DiceRollerUI (JavaScript Frontend)**
**Ubicación**: [`app/static/js/dice-roller.js`](docs/dice-roller.md)

**Características**:
- ✅ Interfaz unificada para todas las tiradas
- ✅ Modal de selección: Automático vs Manual
- ✅ Visualización individual de dados
- ✅ Soporte para modificadores
- ✅ Callback asíncrono
- ✅ Llamada al backend `/api/dice/roll`

**Uso**: Personal, transporte de pasajeros, algunas acciones futuras

### 3. **Setup Manual (JavaScript Directo)**
**Ubicación**: [`app/templates/setup.html`](docs/setup.html.md)

**Características**:
- ❌ No usa DiceRollerUI
- ❌ Lógica de dados embebida en el template
- ❌ Solo modo automático (sin opción manual)
- ❌ No visualización de dados individuales

**Problema**: Inconsistente con el resto del sistema

### 4. **Endpoint Universal**
**Ubicación**: [`app/main.py`](docs/main.md) - `/api/dice/roll`

**Características**:
- ✅ Endpoint universal para tiradas
- ✅ Soporte para dados manuales y automáticos
- ✅ Validación de entrada
- ✅ Compatible con DiceRollerUI

---

## ⚠️ Problemas de Coherencia Identificados

### 1. **Múltiples Sistemas Paralelos**
- **Setup**: Usa lógica propia, no DiceRollerUI
- **Personal/Transporte**: Usa DiceRollerUI correctamente
- **Futuras features**: Podrían usar cualquier sistema

### 2. **Formatos de Datos Inconsistentes**
```javascript
// Setup envía como string separado por comas
formData.append('area_manual', areaData.dice.join(','));

// Passenger transport envía igual
formData.append('manual_dice', diceResult.dice.join(','));

// Pero algunos lugares esperan arrays
manual_values: [3, 5]  // en /api/dice/roll
```

### 3. **Modos de Juego No Consistentes**
- **Setup**: Solo automático (sin opción manual)
- **Personal/Transporte**: Ambos modos disponibles
- **Manual de Spacegom**: Siempre permite dados físicos

### 4. **Visualización Inconsistente**
- **DiceRollerUI**: Muestra dados individuales bellamente
- **Setup**: Solo muestra suma como "4 + 3"
- **Backend**: No hay visualización

---

## 🎯 Recomendaciones para Unificación

### **FASE 1: Migrar Setup a DiceRollerUI**

Actualizar `setup.html` para usar DiceRollerUI en lugar de lógica propia:

```javascript
// En setup.html - Reemplazar lógica actual
async function rollArea() {
    await DiceRollerUI.requestRoll({
        numDice: 2,
        diceSides: 6,
        title: "Determinación de Área",
        description: "Tirada para determinar el área espacial (2-12)",
        onResult: async (result) => {
            // Procesar resultado...
            document.getElementById('area-dice').textContent = result.dice.join(' + ');
            // Enviar al backend...
        }
    });
}
```

### **FASE 2: Estandarizar Formato de Datos**

**Decisión**: Usar **string separado por comas** como estándar universal:

```javascript
// ESTÁNDAR RECOMENDADO
formData.append('manual_dice', diceResult.dice.join(','));
// Resultado: "3,5" para dados [3, 5]

// Backend siempre parsea:
dice_values = [int(x) for x in manual_dice.split(',')]
```

### **FASE 3: Extender DiceRollerUI**

Agregar features faltantes:

```javascript
// Features a agregar a DiceRollerUI
static async requestRoll(config) {
    const {
        numDice,
        diceSides = 6,
        title = "Tirada de Dados",
        description = "",
        modifiers = {},
        allowSkipManual = false,  // Para setup: forzar automático
        customDiceDisplay = null, // Función custom de visualización
        onResult
    } = config;
    
    // Si allowSkipManual=false, saltar directamente a automático
    // ...
}
```

### **FASE 4: Centralizar Historial**

Crear sistema unificado de historial:

```python
# En game_state.py o nuevo módulo
class DiceHistoryManager:
    def record_roll(self, game_id, num_dice, results, mode, purpose, modifiers=None):
        # Guardar en BD con timestamp
        
    def get_history(self, game_id, limit=10):
        # Obtener últimas tiradas
```

---

## 📋 Plan de Implementación

### **Semana 1: Análisis y Diseño**
- [ ] Documentar todos los usos actuales de dados
- [ ] Definir API unificada
- [ ] Crear especificaciones de migración

### **Semana 2: Migración Setup**
- [ ] Actualizar `setup.html` para usar DiceRollerUI
- [ ] Mantener compatibilidad con datos existentes
- [ ] Probar flujo completo de setup

### **Semana 3: Estandarización Backend**
- [ ] Unificar parsing de dados en todos los endpoints
- [ ] Crear utilidad centralizada para dados manuales
- [ ] Actualizar documentación

### **Semana 4: Features Avanzadas**
- [ ] Implementar historial unificado
- [ ] Agregar estadísticas de dados
- [ ] Crear modo "simulación" para testing

---

## 🔧 API Unificada Propuesta

### **Frontend (DiceRollerUI.requestRoll)**
```javascript
await DiceRollerUI.requestRoll({
    numDice: 2,
    diceSides: 6,
    title: "Título descriptivo",
    description: "Explicación del propósito",
    modifiers: {"Modificador": valor},
    allowSkipManual: false,  // Default: true
    onResult: async (result) => {
        // result.dice: [3, 5]
        // result.sum: 8
        // result.total: 8 + modificadores
        // result.mode: 'auto' o 'manual'
    }
});
```

### **Backend (Envío a API)**
```javascript
// Formato estándar
if (result.mode === 'manual') {
    formData.append('manual_dice', result.dice.join(','));
}
// Backend: dice_values = [int(x) for x in manual_dice.split(',')]
```

### **Historial Unificado**
```javascript
// Automático en todas las tiradas
await DiceHistoryManager.record(game_id, {
    num_dice: result.dice.length,
    results: result.dice,
    mode: result.mode,
    purpose: "descripción",
    modifiers: result.modifiers,
    total: result.total
});
```

---

## 📈 Beneficios de la Unificación

### **Para Desarrolladores**
- ✅ **Un solo sistema** para aprender y mantener
- ✅ **Consistencia** en toda la aplicación
- ✅ **Reutilización** de componentes
- ✅ **Debugging** simplificado

### **Para Jugadores**
- ✅ **Experiencia consistente** en todas las tiradas
- ✅ **Flexibilidad** para usar dados físicos o digitales
- ✅ **Visualización clara** de resultados
- ✅ **Historial** de todas las tiradas

### **Para el Proyecto**
- ✅ **Mantenibilidad** mejorada
- ✅ **Extensibilidad** para nuevas features
- ✅ **Testing** simplificado
- ✅ **Documentación** unificada

---

## 🚀 Implementación Inmediata Recomendada

Para mantener la coherencia **inmediata**, recomiendo:

1. **Congelar** nuevos usos de dados hasta completar migración
2. **Documentar** todos los puntos de uso actuales
3. **Crear** wrapper functions para unificar llamadas
4. **Implementar** historial básico antes de migrar

¿Procedemos con la migración del setup a DiceRollerUI primero?

---

## 📋 **PLAN DE TRABAJO PARA UNIFICACIÓN DEL SISTEMA DE DADOS**

### 🎯 **Objetivos Específicos**

Basado en los requisitos del libro-juego Spacegom, el sistema unificado debe garantizar:

1. **🎲 Opción Física Obligatoria**: Toda tirada debe permitir dados físicos
2. **👁️ Visualización Individual**: Mostrar dados individuales, nunca solo la suma
3. **📊 Escalabilidad**: Soporte para 1-3 dados (preparado para más)
4. **⚡ Modificadores Complejos**: Impacto en acciones, moral y experiencia

---

### **FASE 1: Diseño del Sistema Unificado (1 semana)**

#### **1.1 Definir API Universal**
```javascript
// API unificada para TODAS las tiradas
await DiceRollerUI.requestRoll({
    numDice: 2,              // 1-3 dados (preparado para más)
    diceSides: 6,            // Siempre 6 caras (d6)
    title: "Título descriptivo",
    description: "Explicación del propósito",
    modifiers: {
        "Modificador Acción": valor,     // Afecta resultado principal
        "Moral": valor,                  // Afecta moral del personaje
        "Experiencia": valor             // Afecta experiencia
    },
    effects: {                          // Efectos secundarios
        morale: true,                   // Esta tirada afecta moral
        experience: true                // Esta tirada afecta experiencia
    },
    onResult: async (result) => {
        // result.dice: [3, 5] - INDIVIDUALES, nunca suma
        // result.total: suma + modificadores de acción
        // result.effects: {morale: +1, experience: -1}
        // result.mode: 'manual' (obligatorio mostrar opción)
    }
});
```

#### **1.2 Sistema de Visualización Gráfica**
```javascript
// Componente de dados con gráficos
DiceDisplay.show({
    dice: [3, 5, 2],        // Array de valores individuales
    style: 'large',         // 'small', 'medium', 'large'
    animated: true,         // Animación de "caída"
    showSum: false          // NUNCA mostrar suma sola
});
```

#### **1.3 Backend Unificado**
```python
# Endpoint único para todas las tiradas
@app.post("/api/dice/roll-unified")
async def roll_dice_unified(request: Request):
    data = await request.json()
    num_dice = data['num_dice']  # 1-3 (validar)
    
    # SIEMPRE permitir manual
    if 'manual_values' in data:
        dice_values = data['manual_values']
    else:
        dice_values = DiceRoller.roll_dice(num_dice, 6)
    
    # Calcular efectos
    effects = calculate_effects(dice_values, data.get('modifiers', {}))
    
    return {
        "dice": dice_values,           # INDIVIDUALES
        "total": sum(dice_values),     # Para acciones
        "effects": effects,            # Para moral/experiencia
        "mode": "manual" if 'manual_values' in data else "auto"
    }
```

---

### **FASE 2: Implementación Core (2 semanas)**

#### **2.1 Extender DiceRollerUI**
- ✅ **Forzar modo manual**: Eliminar opción de saltar manual
- ✅ **Validación estricta**: Solo 1-3 dados, siempre d6
- ✅ **Visualización gráfica**: Dados individuales con iconos/animaciones
- ✅ **Efectos secundarios**: Soporte para moral y experiencia

#### **2.2 Backend Unificado**
- ✅ **Validación**: Solo 1-3 dados, siempre d6
- ✅ **Cálculo de efectos**: Lógica para moral/experiencia
- ✅ **Historial**: Registrar todas las tiradas con efectos

#### **2.3 Base de Datos**
```sql
-- Tabla para historial completo
CREATE TABLE dice_rolls (
    id INTEGER PRIMARY KEY,
    game_id TEXT,
    timestamp DATETIME,
    num_dice INTEGER,
    dice_values TEXT,        -- "3,5,2" (individuales)
    modifiers TEXT,          -- JSON con modificadores
    action_total INTEGER,    -- Suma para acción
    morale_effect INTEGER,   -- Efecto en moral
    experience_effect INTEGER, -- Efecto en experiencia
    mode TEXT,               -- 'manual' o 'auto'
    purpose TEXT             -- Descripción del propósito
);
```

---

### **FASE 3: Migración de Componentes (3 semanas)**

#### **3.1 Setup (Semana 1)**
- ✅ Migrar `setup.html` a DiceRollerUI
- ✅ Mantener compatibilidad con datos existentes
- ✅ Asegurar opción manual (aunque sea setup inicial)

#### **3.2 Personal (Semana 2)**
- ✅ Actualizar contratación para usar sistema unificado
- ✅ Agregar efectos de moral/experiencia
- ✅ Mejorar visualización de dados

#### **3.3 Comercio y Transporte (Semana 3)**
- ✅ Migrar transporte de pasajeros
- ✅ Actualizar terminal comercial
- ✅ Unificar formato de dados

---

### **FASE 4: Testing y Optimización (1 semana)**

#### **4.1 Testing Exhaustivo**
- ✅ **Modo manual**: Verificar que siempre esté disponible
- ✅ **Visualización**: Confirmar dados individuales en todas las tiradas
- ✅ **Efectos**: Validar impacto en moral y experiencia
- ✅ **Escalabilidad**: Probar con 1, 2, 3 dados

#### **4.2 Optimizaciones**
- ✅ **Performance**: Lazy loading de componentes
- ✅ **UX**: Animaciones suaves, feedback claro
- ✅ **Accesibilidad**: Soporte para lectores de pantalla

---

### **📊 Requisitos Técnicos Detallados**

#### **Frontend Requirements**
```javascript
// Requisitos OBLIGATORIOS para toda tirada
const requirements = {
    manualMode: true,              // SIEMPRE disponible
    individualDisplay: true,       // SIEMPRE mostrar dados individuales
    noSumOnly: true,              // NUNCA mostrar solo suma
    maxDice: 3,                   // Máximo 3 dados (por ahora)
    diceType: 'd6',               // Solo dados de 6 caras
    modifiersSupport: true,       // Soporte para modificadores
    effectsSupport: true,         // Soporte para efectos secundarios
    graphicalDisplay: true        // Visualización gráfica preferida
};
```

#### **Backend Requirements**
```python
# Validaciones obligatorias
def validate_dice_roll(data):
    assert 1 <= data['num_dice'] <= 3, "Solo 1-3 dados"
    assert data['dice_sides'] == 6, "Solo dados d6"
    assert 'manual_option' in data, "Debe permitir manual"
    assert 'individual_display' in data, "Debe mostrar individuales"
    return True
```

#### **Database Requirements**
```sql
-- Estructura para efectos complejos
CREATE TABLE dice_effects (
    roll_id INTEGER,
    effect_type TEXT,        -- 'morale', 'experience', 'action'
    effect_value INTEGER,    -- Valor del efecto
    target_id TEXT,          -- ID del personaje/objetivo
    FOREIGN KEY (roll_id) REFERENCES dice_rolls(id)
);
```

---

### **🎨 Especificaciones de UI/UX**

#### **Modal de Tirada Estándar**
```
┌─────────────────────────────────────┐
│ 🎲 TIRADA DE DADOS                 │
├─────────────────────────────────────┤
│ ¿Cómo quieres tirar los dados?     │
│                                     │
│ 🤖 AUTOMÁTICO    🎯 MANUAL         │
│ El sistema tira   Introduce tus    │
│ los dados        dados físicos     │
├─────────────────────────────────────┤
│ [3] [5] [2]  ← Dados individuales  │
│                                     │
│ Suma: 10                           │
│ Mod. Acción: +2 = 12               │
│                                     │
│ 🎭 Efectos Secundarios:            │
│ Moral: +1    Experiencia: -1       │
├─────────────────────────────────────┤
│          [✓ Continuar]             │
└─────────────────────────────────────┘
```

#### **Visualización Gráfica de Dados**
- **Dado 1-3**: Iconos grandes con números
- **Animación**: Efecto de "caída" al mostrar resultado
- **Estados**: Normal, resaltado (para modificadores), animado
- **Responsive**: Adaptable a diferentes tamaños de pantalla

---

### **🔄 Integración con Sistema de Personajes**

#### **Efectos en Moral**
```javascript
// Después de tirada, aplicar efectos
if (result.effects.morale !== 0) {
    await updateCharacterMorale(characterId, result.effects.morale);
    showToast(`Moral ${result.effects.morale > 0 ? '+' : ''}${result.effects.morale}`, 
              result.effects.morale > 0 ? 'success' : 'warning');
}
```

#### **Efectos en Experiencia**
```javascript
if (result.effects.experience !== 0) {
    await updateCharacterExperience(characterId, result.effects.experience);
    showToast(`Experiencia ${result.effects.experience > 0 ? '+' : ''}${result.effects.experience}`, 
              'info');
}
```

---

### **📈 Métricas de Éxito**

#### **Funcionales**
- ✅ **100% de tiradas** permiten modo manual
- ✅ **100% de tiradas** muestran dados individuales
- ✅ **0 tiradas** muestran solo suma
- ✅ **Cobertura completa** de 1-3 dados
- ✅ **Efectos implementados** para moral y experiencia

#### **Técnicas**
- ✅ **0 errores** en validaciones de dados
- ✅ **Performance** < 500ms para tiradas
- ✅ **Compatibilidad** con todos los navegadores
- ✅ **Accesibilidad** WCAG 2.1 AA

#### **UX**
- ✅ **Satisfacción usuario** > 4.5/5 en encuestas
- ✅ **Tiempo de tirada** < 10 segundos
- ✅ **Errores de usuario** < 1%

---

### **🚨 Riesgos y Mitigaciones**

#### **Riesgo: Resistencia al cambio**
- **Mitigación**: Comunicación clara de beneficios, demos interactivas

#### **Riesgo: Complejidad técnica**
- **Mitigación**: Desarrollo incremental, testing exhaustivo

#### **Riesgo: Impacto en performance**
- **Mitigación**: Optimización de componentes, lazy loading

#### **Riesgo: Inconsistencias durante migración**
- **Mitigación**: Congelar features nuevas, migración por módulos

---

### **📅 Cronograma Detallado**

| Semana | Actividad | Entregable | Estado |
|--------|-----------|------------|--------|
| 1 | Diseño API unificada | Especificaciones completas | ⏳ Pendiente |
| 2-3 | Implementación core | DiceRollerUI extendido | ⏳ Pendiente |
| 4-6 | Migración componentes | Setup, Personal, Comercio | ⏳ Pendiente |
| 7 | Testing y optimización | Sistema completamente funcional | ⏳ Pendiente |
| 8 | Validación final | Métricas de éxito cumplidas | ⏳ Pendiente |

---

### **👥 Equipo y Responsabilidades**

- **Product Owner**: Definir requisitos específicos del libro-juego
- **UX Designer**: Diseñar visualización gráfica de dados
- **Frontend Dev**: Implementar DiceRollerUI y migraciones
- **Backend Dev**: Implementar API unificada y lógica de efectos
- **QA Tester**: Validar todos los flujos y edge cases

---

**¿Listo para comenzar con la FASE 1?** El diseño de la API unificada es el foundation para todo el sistema. 🚀

---

**Estado**: Plan completo definido, listo para implementación
**Prioridad**: Crítica - Fundacional para experiencia de juego
**Complejidad**: Alta - Requiere cambios en múltiples sistemas
**Tiempo estimado**: 8 semanas (2 meses)
**Riesgo**: Medio - Migración compleja pero beneficios enormes