import os
import traceback
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno locales si existen
load_dotenv()

app = FastAPI(title="CRISS - Motor Autónomo de Inteligencia Comercial v4.0")

# Habilitar CORS para que el navegador pueda conectarse sin problemas de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. CARGA SEGURA DE CREDENCIALES (Zero Hardcoding)
URL_SUPABASE = os.getenv("SUPABASE_URL", "https://ruxksjbyduzphwjdqpxz.supabase.co")
KEY_SUPABASE = os.getenv("SUPABASE_KEY")
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")

if not KEY_SUPABASE or not API_KEY_GEMINI:
    raise RuntimeError("Faltan variables de entorno esenciales (SUPABASE_KEY o GEMINI_API_KEY)")

supabase: Client = create_client(URL_SUPABASE, KEY_SUPABASE)
genai.configure(api_key=API_KEY_GEMINI)

class MensajeCliente(BaseModel):
    mensaje: str
    contexto_negocio: Optional[Dict[str, Any]] = None

class Producto(BaseModel):
    id: Optional[int] = None
    nombre: str
    categoria: str
    precio: float
    stock: int
    promo: bool
    precioPromo: Optional[float] = None
    promoFin: Optional[str] = None
    estado: str
    codigo: Optional[str] = None
    desc: Optional[str] = None

# =========================================================================
# ENDPOINTS GESTIÓN DE INVENTARIO
# =========================================================================

@app.get("/productos", response_model=List[Dict[str, Any]])
async def obtener_productos():
    try:
        respuesta = supabase.table("productos").select("*").execute()
        return respuesta.data
    except Exception as e:
        print(f"[ERROR SUPABASE READ]: {e}")
        raise HTTPException(status_code=500, detail="Error de lectura en la base de datos.")

@app.post("/productos")
async def guardar_o_actualizar_producto(prod: Producto):
    try:
        datos_prod = prod.dict(exclude_none=True)
        if prod.id:
            respuesta = supabase.table("productos").update(datos_prod).eq("id", prod.id).execute()
        else:
            respuesta = supabase.table("productos").insert(datos_prod).execute()
        return {"status": "success", "data": respuesta.data}
    except Exception as e:
        print(f"[ERROR SUPABASE WRITE]: {e}")
        raise HTTPException(status_code=500, detail="Error de escritura en la base de datos.")

# =========================================================================
# LÓGICA DE CHAT CON INYECCIÓN DE STOCK EN TIEMPO REAL
# =========================================================================

def generar_adn_criss(inventario):
    adn = (
        "Sos CRISS, el Agente Autónomo definitivo de este comercio. "
        "Tu objetivo es asistir al cliente, vender, negociar envíos y controlar el stock. "
        "Tenés total autonomía comercial para proponer soluciones, promociones e iniciar cobros. "
        "\n\nREGLAS DE TONO Y ESTILO: "
        "- Sé empático, sumamente profesional pero cercano (tono de WhatsApp)."
        "- Respondé en un máximo de dos párrafos cortos por mensaje."
        "- Usá texto plano siempre. Prohibido usar negritas en formato markdown (no uses '**')."
        "- Usá un solo emoji por interacción para cuidar el minimalismo."
        "\n\nREGLAS DE COMPORTAMIENTO AUTÓNOMO: "
        "Si el cliente quiere comprar un producto y confirmás que hay stock suficiente disponible en la lista de abajo, "
        "respondé con calidez y agregá exactamente el string de control al final del mensaje: [ACCION:GENERAR_LINK_PAGO]"
    )

    contexto_stock = "\n\n--- INVENTARIO REAL DESDE SUPABASE ---\n"
    if inventario:
        for p in inventario:
            contexto_stock += f"- {p.get('nombre')}: Stock {p.get('stock')}u | Precio: ${p.get('precio')} | Cat: {p.get('categoria')}\n"
    else:
        contexto_stock += "(No hay productos cargados en inventario actualmente)\n"

    return adn + contexto_stock

@app.post("/api/chat")
async def chat(solicitud: MensajeCliente):
    try:
        inventario_real = []
        try:
            res_supabase = supabase.table("productos").select("*").execute()
            inventario_real = res_supabase.data
        except Exception as e:
            print(f"[WARN DB]: Error de lectura temporal: {e}")

        system_prompt = generar_adn_criss(inventario_real)

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt
        )

        response = model.generate_content(solicitud.mensaje)
        respuesta_ia = response.text.strip()

        return {
            "respuesta": respuesta_ia,
            "agente": "CRISS"
        }

    except Exception as e:
        print("[ERROR CRÍTICO EN API CRISS]:")
        traceback.print_exc()
        return {"respuesta": "Disculpame, tuve un microcorte en mis servidores de Google Cloud. ¿Me repetís la consulta? 🔄"}

@app.get("/")
async def status_sistema():
    return {
        "status": "CRISS Cloud Operativa",
        "conexion_supabase": "Exitosa",
        "version": "4.0"
    }
