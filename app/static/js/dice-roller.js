/**
 * DiceRollerUI - Sistema Universal de Dados para Spacegom
 * 
 * Interfaz JavaScript consistente para todas las tiradas de dados del juego.
 * Proporciona modo automático/manual y visualización de resultados.
 * 
 * Decisiones de diseño:
 * - SIEMPRE ofrece modo manual/automático: El manual del juego permite usar dados físicos,
 *   por lo que todas las tiradas deben dar esta opción al jugador
 * - Muestra dados individuales: Proporciona sensación de juego más auténtica al ver
 *   cada dado por separado, no solo la suma
 * - Interfaz unificada: Un solo componente para todas las tiradas asegura consistencia
 *   visual y de comportamiento en toda la aplicación
 * - Fallback local: Si falla el backend, hace tirada local para no bloquear el juego
 * 
 * Características principales:
 * - Modo dual: Automático (backend) o manual (dados físicos)
 * - Visualización: Muestra dados individuales con diseño cyberpunk
 * - Modificadores: Soporte para múltiples modificadores nombrados
 * - Responsive: Modales centrados y adaptables
 * - Fallback: Tirada local si falla el backend
 * 
 * Estructura del resultado:
 * {
 *     dice: [3, 5],        // Valores individuales de cada dado
 *     sum: 8,              // Suma de los dados
 *     mode: "manual",      // "manual" o "automatic"
 *     modifiers: {rep: 2}, // Modificadores aplicados
 *     total: 10            // Suma + modificadores
 * }
 * 
 * Dependencias:
 * - Fetch API para llamadas al backend
 * - DOM manipulation para creación de modales
 * 
 * Estilos utilizados:
 * - glass-panel: Panel con efecto glassmorphism
 * - tech-border: Bordes neón
 * - font-orbitron: Tipografía técnica
 * - neon-blue/green: Colores temáticos
 * 
 * Disponible globalmente como window.DiceRollerUI
 * 
 * @example
 * const result = await DiceRollerUI.requestRoll({
 *     numDice: 2,
 *     title: "Tirada de Combate",
 *     modifiers: {fuerza: 2, armadura: -1}
 * });
 */
class DiceRollerUI {
    /**
     * Solicita una tirada de dados con interfaz consistente
     * 
     * @param {Object} config - Configuración de la tirada
     * @param {Number} config.numDice - Número de dados (ej: 2)
     * @param {Number} config.diceSides - Caras del dado (default: 6)
     * @param {String} config.title - Título del modal (ej: "Búsqueda de Personal")
     * @param {String} config.description - Descripción adicional (opcional)
     * @param {Object} config.modifiers - Modificadores opcionales {name: value}
     * @param {Function} config.onResult - Callback(result) cuando se obtiene resultado
     * 
     * @returns {Promise<Object>} Resultado de la tirada
     */
    static async requestRoll(config) {
        const {
            numDice,
            diceSides = 6,
            title = "Tirada de Dados",
            description = "",
            modifiers = {},
            onResult
        } = config;

        return new Promise((resolve) => {
            // Mostrar modal de selección de modo
            this.showModeSelectionModal({
                numDice,
                diceSides,
                title,
                description,
                onModeSelected: async (mode) => {
                    let diceValues;

                    if (mode === 'manual') {
                        // Solicitar entrada manual
                        diceValues = await this.showManualInputModal({
                            numDice,
                            diceSides,
                            title
                        });
                    } else {
                        // Tirada automática
                        diceValues = await this.rollAutomatic(numDice, diceSides);
                    }

                    // Preparar resultado
                    const result = {
                        dice: diceValues,
                        sum: diceValues.reduce((a, b) => a + b, 0),
                        mode: mode,
                        modifiers: modifiers
                    };

                    // Calcular total con modificadores
                    let modifierSum = 0;
                    for (const [name, value] of Object.entries(modifiers)) {
                        modifierSum += value;
                    }
                    result.total = result.sum + modifierSum;

                    // Mostrar resultado
                    this.showResultModal({
                        ...config,
                        result
                    });

                    // Ejecutar callback
                    if (onResult) {
                        onResult(result);
                    }

                    resolve(result);
                }
            });
        });
    }

    /**
     * Muestra modal para elegir entre modo automático o manual.
     * 
     * Crea un modal con dos opciones:
     * - Automática: El sistema tira los dados en el backend
     * - Manual: El usuario introduce resultados de dados físicos
     * 
     * @param {Object} config - Configuración del modal
     * @param {Number} config.numDice - Número de dados a tirar
     * @param {Number} config.diceSides - Caras por dado (default: 6)
     * @param {String} config.title - Título del modal
     * @param {String} config.description - Descripción opcional
     * @param {Function} config.onModeSelected - Callback(mode) cuando se selecciona modo
     */
    static showModeSelectionModal({ numDice, diceSides, title, description, onModeSelected }) {
        const modal = document.createElement('div');
        modal.id = 'dice-mode-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';

        modal.innerHTML = `
            <div class="glass-panel tech-border p-8 rounded-lg max-w-md w-full">
                <h3 class="text-2xl font-orbitron text-neon-blue mb-4">🎲 ${title}</h3>
                <p class="text-gray-400 mb-2">${numDice}D${diceSides}</p>
                ${description ? `<p class="text-sm text-gray-500 mb-6">${description}</p>` : '<div class="mb-6"></div>'}
                
                <div class="space-y-3">
                    <button onclick="window.diceRollerSelectMode('auto')" 
                        class="w-full py-4 bg-neon-blue bg-opacity-20 border-2 border-neon-blue text-neon-blue rounded hover:bg-opacity-30 font-orbitron transition-all">
                        🤖 AUTOMÁTICA
                        <div class="text-xs text-gray-400 mt-1">El sistema tira los dados</div>
                    </button>
                    <button onclick="window.diceRollerSelectMode('manual')" 
                        class="w-full py-4 bg-neon-green bg-opacity-20 border-2 border-neon-green text-neon-green rounded hover:bg-opacity-30 font-orbitron transition-all">
                        🎯 MANUAL
                        <div class="text-xs text-gray-400 mt-1">Introduce tus dados físicos</div>
                    </button>
                </div>
                
                <button onclick="window.diceRollerCancel()" 
                    class="w-full mt-4 py-2 bg-gray-700 border border-gray-600 text-gray-300 rounded hover:bg-gray-600">
                    Cancelar
                </button>
            </div>
        `;

        document.body.appendChild(modal);

        // Callback global temporal
        window.diceRollerSelectMode = (mode) => {
            modal.remove();
            delete window.diceRollerSelectMode;
            delete window.diceRollerCancel;
            onModeSelected(mode);
        };

        window.diceRollerCancel = () => {
            modal.remove();
            delete window.diceRollerSelectMode;
            delete window.diceRollerCancel;
        };
    }

    /**
     * Muestra modal para introducir resultados manuales de dados físicos.
     * 
     * Crea un formulario con un input numérico por cada dado, validando que
     * los valores estén en el rango válido (1 a diceSides).
     * 
     * @param {Object} config - Configuración del modal
     * @param {Number} config.numDice - Número de dados (determina número de inputs)
     * @param {Number} config.diceSides - Caras por dado (determina rango válido)
     * @param {String} config.title - Título del modal
     * 
     * @returns {Promise<Array<Number>|null>} Array con valores de dados o null si se cancela
     */
    static showManualInputModal({ numDice, diceSides, title }) {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.id = 'dice-manual-modal';
            modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';

            let inputsHTML = '';
            for (let i = 0; i < numDice; i++) {
                inputsHTML += `
                    <div class="flex items-center gap-3">
                        <label class="text-neon-green font-orbitron">Dado ${i + 1}:</label>
                        <input type="number" id="manual-dice-${i}" min="1" max="${diceSides}" required
                            class="flex-1 bg-space-800 border border-neon-green rounded px-4 py-2 text-white text-center text-xl font-orbitron">
                    </div>
                `;
            }

            modal.innerHTML = `
                <div class="glass-panel tech-border p-8 rounded-lg max-w-md w-full">
                    <h3 class="text-2xl font-orbitron text-neon-green mb-4">🎯 ${title}</h3>
                    <p class="text-gray-400 mb-6">Introduce el resultado de tus ${numDice}D${diceSides} físicos:</p>
                    
                    <form id="manual-dice-form" class="space-y-4">
                        ${inputsHTML}
                        
                        <div class="flex gap-3 mt-6">
                            <button type="submit" 
                                class="flex-1 py-3 bg-neon-green bg-opacity-20 border-2 border-neon-green text-neon-green rounded hover:bg-opacity-30 font-orbitron">
                                ✓ Confirmar
                            </button>
                            <button type="button" onclick="window.diceManualCancel()" 
                                class="flex-1 py-3 bg-gray-700 border border-gray-600 text-gray-300 rounded hover:bg-gray-600">
                                Cancelar
                            </button>
                        </div>
                    </form>
                </div>
            `;

            document.body.appendChild(modal);

            // Enfocar primer input
            setTimeout(() => {
                document.getElementById('manual-dice-0')?.focus();
            }, 100);

            // Manejar submit
            document.getElementById('manual-dice-form').addEventListener('submit', (e) => {
                e.preventDefault();

                const values = [];
                for (let i = 0; i < numDice; i++) {
                    const value = parseInt(document.getElementById(`manual-dice-${i}`).value);
                    if (value < 1 || value > diceSides) {
                        alert(`Dado ${i + 1} debe estar entre 1 y ${diceSides}`);
                        return;
                    }
                    values.push(value);
                }

                modal.remove();
                delete window.diceManualCancel;
                resolve(values);
            });

            window.diceManualCancel = () => {
                modal.remove();
                delete window.diceManualCancel;
                // Volver al modal de selección de modo
                resolve(null);
            };
        });
    }

    /**
     * Realiza tirada automática llamando al endpoint del backend.
     * 
     * Envía una petición POST a /api/dice/roll con los parámetros de la tirada.
     * Si falla la conexión, hace fallback a una tirada local usando Math.random().
     * 
     * @param {Number} numDice - Número de dados a tirar
     * @param {Number} diceSides - Caras por dado (default: 6)
     * 
     * @returns {Promise<Array<Number>>} Array con valores de cada dado
     * 
     * @throws {Error} Si hay error de red (se maneja con fallback local)
     */
    static async rollAutomatic(numDice, diceSides) {
        try {
            const response = await fetch('/api/dice/roll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    num_dice: numDice,
                    dice_sides: diceSides
                })
            });

            const data = await response.json();
            return data.dice;
        } catch (error) {
            console.error('Error rolling dice:', error);
            // Fallback a tirada local
            return Array.from({ length: numDice }, () =>
                Math.floor(Math.random() * diceSides) + 1
            );
        }
    }

    /**
     * Muestra modal con resultado de la tirada, dados individuales y modificadores.
     * 
     * Crea un modal visual con:
     * - Visualización de cada dado individual
     * - Suma de los dados
     * - Modificadores aplicados (si hay)
     * - Total final (suma + modificadores)
     * - Indicador de modo (manual/automático)
     * 
     * @param {Object} config - Configuración del modal
     * @param {Number} config.numDice - Número de dados tirados
     * @param {Number} config.diceSides - Caras por dado
     * @param {String} config.title - Título del modal
     * @param {Object} config.modifiers - Objeto con modificadores {name: value}
     * @param {Object} config.result - Resultado de la tirada con dice, sum, mode, total
     */
    static showResultModal({ numDice, diceSides, title, modifiers, result }) {
        const modal = document.createElement('div');
        modal.id = 'dice-result-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';

        const diceHTML = result.dice.map(d =>
            `<span class="inline-block w-16 h-16 leading-16 text-center bg-white text-space-900 font-bold rounded-lg text-2xl shadow-lg">${d}</span>`
        ).join(' ');

        let modifiersHTML = '';
        if (Object.keys(modifiers).length > 0) {
            const modParts = Object.entries(modifiers).map(([name, value]) =>
                `${name}(${value >= 0 ? '+' : ''}${value})`
            ).join(' + ');
            const modTotal = Object.values(modifiers).reduce((a, b) => a + b, 0);
            modifiersHTML = `
                <div class="text-xs text-gray-400 mt-3">
                    Modificadores: ${modParts} = ${modTotal >= 0 ? '+' : ''}${modTotal}
                </div>
            `;
        }

        modal.innerHTML = `
            <div class="glass-panel tech-border p-8 rounded-lg max-w-lg w-full">
                <h3 class="text-2xl font-orbitron text-neon-blue mb-6">${title} - ${numDice}D${diceSides}</h3>
                
                <div class="glass-panel tech-border p-6 rounded mb-6">
                    <div class="text-xs text-gray-500 uppercase mb-3 tracking-wider">
                        ${result.mode === 'manual' ? '🎯 Dados Manuales' : '🤖 Tirada Automática'}
                    </div>
                    <div class="flex items-center justify-center gap-3 mb-4">
                        ${diceHTML}
                    </div>
                    <div class="text-center">
                        <span class="text-sm text-gray-400">Suma:</span>
                        <span class="text-3xl font-orbitron text-neon-blue ml-2">${result.sum}</span>
                    </div>
                    ${modifiersHTML}
                    ${Object.keys(modifiers).length > 0 ?
                `<div class="border-t border-gray-700 mt-4 pt-4 text-center">
                            <span class="text-sm text-gray-400">Total:</span>
                            <span class="text-4xl font-orbitron text-neon-green ml-2">${result.total}</span>
                        </div>` : ''
            }
                </div>
                
                <button onclick="document.getElementById('dice-result-modal').remove()" 
                    class="w-full py-3 bg-neon-blue bg-opacity-20 border-2 border-neon-blue text-neon-blue rounded hover:bg-opacity-30 font-orbitron">
                    ✓ Continuar
                </button>
            </div>
        `;

        document.body.appendChild(modal);
    }
}

// Hacer disponible globalmente
window.DiceRollerUI = DiceRollerUI;
