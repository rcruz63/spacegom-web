/**
 * Passenger Transport Logic - Módulo de Transporte de Pasajeros
 * 
 * Maneja la acción de transporte de pasajeros en el juego SpaceGOM.
 * Proporciona un flujo completo de UI para tirar dados, determinar afluencia
 * de pasajeros, ejecutar la acción vía API y mostrar resultados en un modal.
 * 
 * Flujo de datos:
 * 1. Usuario hace clic en botón de transporte
 * 2. Sistema carga información actual de transporte
 * 3. Se solicita tirada de dados (2d6 + modificadores)
 * 4. Resultado se envía al servidor para procesamiento
 * 5. Servidor calcula pasajeros, ingresos y cambios de personal
 * 6. Resultados se muestran en un modal
 * 7. UI se refresca y página se recarga después de cerrar modal
 * 
 * Dependencias:
 * - DiceRollerUI: Componente universal de tiradas de dados
 * - showToast: Función global para notificaciones
 * - Fetch API: Para llamadas al backend
 * - TailwindCSS: Para estilos
 * - Clases CSS custom: neon-green, space-800, etc.
 * 
 * Endpoints API utilizados:
 * - GET /api/games/{gameId}/passenger-transport/info
 * - POST /api/games/{gameId}/passenger-transport/execute
 */

const PassengerTransport = {
    /** @type {Object|null} Información actual del transporte (cache) */
    currentInfo: null,

    /**
     * Inicializa la funcionalidad de transporte de pasajeros.
     * 
     * Solo se ejecuta si estamos en el dashboard y existe el widget.
     * Configura listeners de eventos y carga información inicial.
     * 
     * @returns {Promise<void>}
     */
    init: async function () {
        // Only run if we are in the dashboard and the widget exists
        if (!document.getElementById('passenger-transport-widget')) return;

        await this.refreshInfo();

        // Attach Event Listeners
        const btn = document.getElementById('btn-transport-passengers');
        if (btn) {
            btn.addEventListener('click', () => this.startTransportAction());
        }
    },

    /**
     * Recarga información de transporte desde el backend.
     * 
     * Obtiene información actualizada sobre:
     * - Naves disponibles y sus capacidades
     * - Asignaciones actuales de personal
     * - Modificadores de transporte (responsable, auxiliares)
     * - Estado de disponibilidad de la acción
     * 
     * Actualiza el cache interno y la UI después de obtener los datos.
     * 
     * @returns {Promise<void>}
     */
    refreshInfo: async function () {
        try {
            const gameId = new URLSearchParams(window.location.search).get('game_id');
            const response = await fetch(`/api/games/${gameId}/passenger-transport/info`);
            const data = await response.json();

            this.currentInfo = data;
            this.updateUI(data);
        } catch (error) {
            console.error("Error fetching passenger info:", error);
        }
    },

    /**
     * Actualiza la UI del widget con los datos recibidos.
     * 
     * Actualiza:
     * - Capacidad de pasajeros (actual / máxima)
     * - Promedio de pasajeros del planeta
     * - Lista de modificadores (responsable, auxiliares)
     * - Estado del botón de acción (habilitado/deshabilitado)
     * 
     * @param {Object} data - Datos de transporte del backend
     * @param {Number} data.current_passengers - Pasajeros actuales
     * @param {Number} data.ship_capacity - Capacidad máxima de la nave
     * @param {Number} data.planet_avg_passengers - Promedio de pasajeros del planeta
     * @param {Object} data.modifiers - Modificadores {has_manager, manager_bonus, attendants_count}
     * @param {Boolean} data.available - Si la acción está disponible
     */
    updateUI: function (data) {
        // Update capacity display
        const capEl = document.getElementById('pt-capacity');
        if (capEl) capEl.textContent = `${data.current_passengers} / ${data.ship_capacity}`;

        // Update planet avg
        const avgEl = document.getElementById('pt-planet-avg');
        if (avgEl) avgEl.textContent = data.planet_avg_passengers;

        // Update Modifiers List
        const modsListEl = document.getElementById('pt-modifiers-list');
        if (modsListEl) {
            let html = '';

            // Manager
            if (data.modifiers.has_manager) {
                const bonus = data.modifiers.manager_bonus >= 0 ? `+${data.modifiers.manager_bonus}` : data.modifiers.manager_bonus;
                html += `<li><span class="text-neon-green">✔ ${data.modifiers.manager_name}</span> (Mod: ${bonus})</li>`;
            } else {
                html += `<li><span class="text-red-400">✘ Sin Responsable</span> (Mod: 0)</li>`;
            }

            // Attendants
            const count = data.modifiers.attendants_count;
            const multiplier = count >= 3 ? 4 : (count === 2 ? 3 : (count === 1 ? 2 : 1));
            html += `<li><span class="text-blue-300">Auxiliares: ${count}</span> (x${multiplier} SC)</li>`;

            modsListEl.innerHTML = html;
        }

        // Handle Action Button Availability
        const btn = document.getElementById('btn-transport-passengers');
        if (btn) {
            if (data.available === false) {
                btn.disabled = true;
                btn.classList.add('opacity-50', 'cursor-not-allowed');
                btn.classList.remove('hover:bg-blue-700', 'shadow-[0_0_10px_rgba(37,99,235,0.5)]');
                btn.textContent = "YA REALIZADO (VIAJA PARA RESETEAR)";
                btn.title = "Debes viajar a otro cuadrante y volver para realizar de nuevo el transporte.";
            } else {
                btn.disabled = false;
                btn.classList.remove('opacity-50', 'cursor-not-allowed');
                btn.classList.add('hover:bg-blue-700', 'shadow-[0_0_10px_rgba(37,99,235,0.5)]');
                btn.textContent = "INICIAR EMBARQUE";
                btn.title = "";
            }
        }
    },

    /**
     * Inicia el flujo de acción de transporte de pasajeros.
     * 
     * Verifica disponibilidad, carga información actual, configura modificadores
     * y solicita tirada de dados a través de DiceRollerUI.
     * 
     * Modificadores aplicados:
     * - Responsable: Bonus según nivel de experiencia y moral del responsable
     * 
     * @returns {Promise<void>}
     */
    startTransportAction: async function () {
        if (!this.currentInfo) await this.refreshInfo();

        if (this.currentInfo.available === false) {
            showToast("Acción no disponible. Viaja a otra área para desbloquear.", 'error');
            return;
        }

        const info = this.currentInfo;
        const managerBonus = info.modifiers.manager_bonus || 0;

        const modifiers = {
            "Responsable": managerBonus
        };

        await DiceRollerUI.requestRoll({
            numDice: 2,
            diceSides: 6,
            title: "Transporte de Pasajeros",
            description: "Tirada para determinar afluencia de pasajeros",
            modifiers: modifiers,
            onResult: async (diceResult) => {
                await this.executeAction(diceResult);
            }
        });
    },

    /**
     * Ejecuta la acción de transporte vía API con el resultado de los dados.
     * 
     * Envía el resultado de la tirada al servidor que calcula:
     * - Número de pasajeros embarcados (según afluencia)
     * - Ingresos generados (base * multiplicador de auxiliares + bonus XP)
     * - Cambios en personal (moral/experiencia)
     * 
     * Si el resultado es exitoso, muestra el modal de resultados.
     * Si hay error, muestra notificación toast.
     * 
     * @param {Object} diceResult - Resultado de la tirada de DiceRollerUI
     * @param {Array<Number>} diceResult.dice - Valores individuales de los dados
     * @param {Number} diceResult.sum - Suma de los dados
     * @param {String} diceResult.mode - "manual" o "automatic"
     * @param {Object} diceResult.modifiers - Modificadores aplicados
     * @param {Number} diceResult.total - Total con modificadores
     * 
     * @returns {Promise<void>}
     */
    executeAction: async function (diceResult) {
        const gameId = new URLSearchParams(window.location.search).get('game_id');
        const formData = new FormData();

        if (diceResult.mode === 'manual') {
            formData.append('manual_dice', diceResult.dice.join(','));
        }

        try {
            const response = await fetch(`/api/games/${gameId}/passenger-transport/execute`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showResultModal(result);
                // Don't modify UI or auto-reload immediately, wait for modal close
            } else {
                showToast(result.detail || "Error en la ejecución", 'error');
            }

        } catch (error) {
            console.error("Error executing transport:", error);
            showToast("Error de comunicación con el servidor", 'error');
        }
    },

    /**
     * Muestra modal completo con resultados del transporte de pasajeros.
     * 
     * El modal incluye:
     * - Visualización de dados individuales
     * - Resultado total de la tirada
     * - Nivel de afluencia (Alta/Media/Baja)
     * - Pasajeros embarcados (actual / capacidad)
     * - Desglose de ingresos (base, multiplicador, bonus XP)
     * - Cambios en personal (moral/experiencia) si los hay
     * 
     * El modal es persistente hasta que el usuario lo cierra. Al cerrar,
     * se refresca la información y se recarga la página para actualizar
     * la barra superior con nuevos valores.
     * 
     * @param {Object} result - Resultado del servidor
     * @param {Array<Number>} result.dice - Valores de los dados
     * @param {Number} result.total_roll - Total de la tirada
     * @param {String} result.outcome - "high", "medium", o "low"
     * @param {Object} result.passengers - {boarded, capacity}
     * @param {Object} result.revenue - {base, multiplier, veteran_bonus, novice_penalty, total}
     * @param {Object} result.personnel_changes - {messages: Array<String>} (opcional)
     */
    showResultModal: function (result) {
        // Visual Dice HTML
        const diceHTML = result.dice.map(d =>
            `<span class="inline-block w-12 h-12 leading-12 text-center bg-white text-space-900 font-bold rounded-lg text-xl shadow-lg flex items-center justify-center">${d}</span>`
        ).join(' ');

        // Personnel Changes HTML
        let personnelMsg = '';
        if (result.personnel_changes && result.personnel_changes.messages.length > 0) {
            personnelMsg = `
                <div class="mt-4 bg-gray-800 p-3 rounded border border-gray-700">
                    <p class="text-[10px] font-bold text-yellow-500 uppercase mb-1">ACTUALIZACIÓN PERSONAL</p>
                    <div class="space-y-1">
                        ${result.personnel_changes.messages.map(m => `<p class="text-xs text-gray-300">• ${m}</p>`).join('')}
                    </div>
                </div>
            `;
        }

        // Modal Content
        const content = `
            <div class="text-center">
                <div class="mb-4">
                    <p class="text-xs text-gray-500 uppercase mb-2">RESULTADO TIRADA</p>
                    <div class="flex items-center justify-center gap-3 mb-2">
                        ${diceHTML}
                    </div>
                    <p class="text-2xl font-orbitron text-white">
                        <span class="text-gray-500 text-sm">Total:</span> ${result.total_roll}
                    </p>
                    <p class="text-xs text-gray-400 mt-1">
                        (Dados: ${result.dice.reduce((a, b) => a + b, 0)} + Mod: ${Object.values(result.modifiers).reduce((a, b) => a + b, 0)})
                    </p>
                    <p class="text-sm font-bold text-neon-blue mt-2 uppercase">
                        Afluencia: ${result.outcome === 'high' ? 'ALTA (x2)' : (result.outcome === 'low' ? 'BAJA (/2)' : 'MEDIA')}
                    </p>
                </div>

                <div class="grid grid-cols-2 gap-3 mb-4 text-left">
                    <div class="bg-space-800 p-2 rounded border border-gray-700">
                        <div class="text-[10px] text-gray-500 uppercase">Pasajeros</div>
                        <div class="text-lg font-orbitron text-white">
                            ${result.passengers.boarded} <span class="text-xs text-gray-500">/ ${result.passengers.capacity}</span>
                        </div>
                    </div>
                    <div class="bg-space-800 p-2 rounded border border-gray-700">
                        <div class="text-[10px] text-gray-500 uppercase">Ingresos</div>
                        <div class="text-lg font-orbitron text-neon-green">
                            +${result.revenue.total} SC
                        </div>
                    </div>
                </div>
                
                <div class="text-xs text-left text-gray-400 ml-1 mb-2">
                    <ul class="list-disc ml-4 space-y-0.5">
                         <li>Base: ${result.revenue.base} x ${result.revenue.multiplier} (Auxiliares)</li>
                         <li>Bonus XP: ${result.revenue.veteran_bonus - result.revenue.novice_penalty} SC</li>
                    </ul>
                </div>

                ${personnelMsg}
            </div>
        `;

        // Create Persistent Modal
        const modalId = 'passenger-result-modal-persistent';
        let existingModal = document.getElementById(modalId);
        if (existingModal) existingModal.remove();

        const modalHtml = `
            <div id="${modalId}" class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 backdrop-blur-sm">
                <div class="glass-panel tech-border p-6 max-w-sm w-full mx-4 rounded-lg border border-neon-green shadow-[0_0_20px_rgba(0,255,157,0.3)] animate-slide-in-up">
                    <h3 class="text-xl font-orbitron text-neon-green mb-4 text-center border-b border-gray-700 pb-2">
                        ✈️ EMBARQUE COMPLETADO
                    </h3>
                    
                    ${content}
                    
                    <button id="btn-close-passenger-result" 
                        class="mt-6 w-full bg-neon-green bg-opacity-20 hover:bg-opacity-30 border border-neon-green text-neon-green font-bold py-3 px-4 rounded transition-all font-orbitron uppercase tracking-wider">
                        ACEPTAR
                    </button>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Handle Close logic
        document.getElementById('btn-close-passenger-result').onclick = async () => {
            const modal = document.getElementById(modalId);
            modal.classList.add('opacity-0', 'transition-opacity', 'duration-300');
            setTimeout(async () => {
                modal.remove();
                await this.refreshInfo(); // Refresh UI to disable button
                showToast(`Ingresos registrados: +${result.revenue.total} SC`, 'success');
                // Optional: Reload page to update top bar
                setTimeout(() => window.location.reload(), 1000);
            }, 300);
        };
    }
};

/**
 * Auto-inicialización cuando el DOM está listo.
 * 
 * Se ejecuta automáticamente al cargar la página si el script está incluido.
 * Solo inicializa si el widget de transporte de pasajeros existe en la página.
 */
document.addEventListener('DOMContentLoaded', () => {
    PassengerTransport.init();
});
