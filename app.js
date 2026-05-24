const CONFIG = {
    API_URL: (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") 
        ? "http://127.0.0.1:8000" 
        : "/api"
};


const AppState = {
    mensajes: [
        { autor: "criss", texto: "¡Hola! Ya envié 2 links de pago de velas esta mañana y estoy negociando un envío por WhatsApp. Dejá todo en mis manos. 😎" }
    ]
};

document.addEventListener("DOMContentLoaded", () => {
    renderizarMensajes();
    setupChatEvents();
    if (typeof lucide !== 'undefined') lucide.createIcons();
});

// Función de Navegación para las 5 Pantallas
function navegar(pantalla, elemento) {
    document.querySelectorAll(".pantalla-app").forEach(p => p.classList.remove("activa"));
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    
    // Mostramos la pantalla correcta
    const targetPantalla = document.getElementById(`pantalla-${pantalla}`);
    if (targetPantalla) {
        targetPantalla.classList.add("activa");
    }
    
    elemento.classList.add("active");

    // Lógicas dinámicas especiales al abrir cada pestaña
    if (pantalla === "stock" && typeof cargarMenuStock === "function") {
        cargarMenuStock();
    } else if (pantalla === "finanzas" && typeof cargarMenuFinanzas === "function") {
        cargarMenuFinanzas();
    }
}

function renderizarMensajes() {
    const history = document.getElementById("chat-history");
    if (!history) return;
    history.innerHTML = AppState.mensajes.map(m => `
        <div class="chat-bubble ${m.autor === 'criss' ? 'criss' : 'user'}">
            ${m.texto}
        </div>
    `).join("");
    history.scrollTop = history.scrollHeight;
}

function setupChatEvents() {
    const sendBtn = document.getElementById("chat-send-btn");
    const input = document.getElementById("chat-input-text");

    if (!sendBtn || !input) return;

    const enviar = async () => {
        const txt = input.value.trim();
        if (!txt) return;

        // 1. Mensaje del usuario
        AppState.mensajes.push({ autor: "user", texto: txt });
        input.value = "";
        renderizarMensajes();

        // 2. Cargando sutil
        AppState.mensajes.push({ autor: "criss", texto: "Procesando... ⚡" });
        renderizarMensajes();

        try {
            // Conexión con tu backend de CRISS
            const res = await fetch(`${CONFIG.API_URL}/api/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensaje: txt })
            });
            const data = await res.json();
            
            // Sacamos el "Procesando..."
            AppState.mensajes.pop();

            let resp = data.respuesta;
            
            // Gestión de acciones autónomas (como links de pago)
            if (resp.includes("[ACCION:GENERAR_LINK_PAGO]")) {
                resp = resp.replace("[ACCION:GENERAR_LINK_PAGO]", "").trim();
                setTimeout(() => {
                    alert("💸 CRISS ha generado un Link de Pago (Mercado Pago) de forma autónoma.");
                }, 1000);
            }

            AppState.mensajes.push({ autor: "criss", texto: resp });
            renderizarMensajes();
        } catch (e) {
            AppState.mensajes.pop();
            AppState.mensajes.push({ autor: "criss", texto: "Sin conexión con mi servidor local. ¿Está uvicorn encendido? 🔄" });
            renderizarMensajes();
        }
    };

    sendBtn.addEventListener("click", enviar);
    input.addEventListener("keypress", (e) => { if (e.key === "Enter") enviar(); });
}
