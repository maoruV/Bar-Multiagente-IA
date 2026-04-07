import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
from datetime import datetime, timezone
import streamlit as st
from langchain_core.messages import HumanMessage
from agents_bar.supervisor import supervisor_graph
from database_models.queries import crear_tablas
from database_models.conversation_queries import (
    crear_conversacion,
    obtener_conversaciones,
    obtener_conversacion_por_id,
    obtener_titulo_actual,
    obtener_mensajes,
    guardar_mensaje,
    actualizar_titulo,
    eliminar_conversacion,
    generar_titulo,
)

# Configuración inicial
crear_tablas()
st.set_page_config(page_title="Bar IA", page_icon="🍺", layout="centered")

# --- CARGAR ESTILOS NEÓN BAR ---
styles_path = os.path.join(os.path.dirname(__file__), "styles", "neon_bar.css")
with open(styles_path, "r", encoding="utf-8") as f:
    neon_styles = f.read()
st.markdown(f"<style>{neon_styles}</style>", unsafe_allow_html=True)


def inicializar_sesion():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if "conversacion_id" not in st.session_state:
        st.session_state.conversacion_id = None

    if "titulo_actualizado" not in st.session_state:
        st.session_state.titulo_actualizado = False


def cargar_conversacion(conversacion_id):
    conv = obtener_conversacion_por_id(conversacion_id)
    if conv:
        st.session_state.conversacion_id = conv.id
        st.session_state.thread_id = conv.thread_id
        st.session_state.titulo_actualizado = False

        mensajes_db = obtener_mensajes(conv.id)
        st.session_state.messages = [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            }
            for m in mensajes_db
        ]
        st.rerun()


def nueva_conversacion():
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.titulo_actualizado = False

    nueva = crear_conversacion(st.session_state.thread_id)
    st.session_state.conversacion_id = nueva.id
    st.rerun()


def eliminar_conversacion_actual(conversacion_id):
    eliminar_conversacion(conversacion_id)

    conversaciones = obtener_conversaciones()
    if conversaciones:
        cargar_conversacion(conversaciones[0].id)
    else:
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.titulo_actualizado = False
        nueva = crear_conversacion(st.session_state.thread_id)
        st.session_state.conversacion_id = nueva.id
    st.rerun()


def guardar_mensaje_actual(role, content, timestamp_str):
    if st.session_state.conversacion_id:
        ts = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
        ts = ts.replace(tzinfo=timezone.utc)
        guardar_mensaje(st.session_state.conversacion_id, role, content, ts)


@st.dialog("Eliminar conversación")
def dialog_confirm_delete(conv_id):
    st.write("¿Estás seguro de que deseas eliminar esta conversación?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Eliminar", type="primary", use_container_width=True):
            eliminar_conversacion_actual(conv_id)
    with col2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()


@st.dialog("Actualizar título")
def dialog_rename_title(conv_id):
    titulo_actual = obtener_titulo_actual(conv_id) or ""
    nuevo_titulo = st.text_input("Nombre de la conversación", value=titulo_actual)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Guardar", type="primary", use_container_width=True):
            if nuevo_titulo.strip():
                actualizar_titulo(conv_id, nuevo_titulo.strip())
                st.rerun()
    with col2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()


# --- INICIALIZACIÓN ---
inicializar_sesion()

if st.session_state.conversacion_id is None:
    conversaciones = obtener_conversaciones()
    if conversaciones:
        cargar_conversacion(conversaciones[0].id)
    else:
        nueva = crear_conversacion(st.session_state.thread_id)
        st.session_state.conversacion_id = nueva.id

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("Conversaciones")

    if st.button("➕ Nueva conversación", use_container_width=True):
        nueva_conversacion()

    st.divider()

    conversaciones = obtener_conversaciones()

    for conv in conversaciones:
        activo = st.session_state.conversacion_id == conv.id
        label = conv.titulo if len(conv.titulo) <= 30 else conv.titulo[:27] + "..."

        col_btn, col_menu = st.columns([4, 1])

        with col_btn:
            if st.button(
                label,
                key=f"conv_{conv.id}",
                use_container_width=True,
                type="primary" if activo else "secondary",
            ):
                if not activo:
                    cargar_conversacion(conv.id)

        with col_menu:
            with st.popover("⋮", use_container_width=True):
                if st.button(
                    "✏️ Actualizar título",
                    use_container_width=True,
                    key=f"rename_{conv.id}",
                ):
                    dialog_rename_title(conv.id)
                if st.button(
                    "🗑️ Eliminar conversación",
                    use_container_width=True,
                    key=f"del_{conv.id}",
                ):
                    dialog_confirm_delete(conv.id)

    st.divider()
    st.caption(f"Sesión: {st.session_state.thread_id[:8]}...")

st.title("🍺 Bar Multi-Agente con IA")
st.info(
    "¡Bienvenido al Bar IA! Escribe tu pedido o consulta y nuestro sistema de agentes se encargará de atenderte. Puedes pedir bebidas, consultar el menú. Para empezar saluda cordialmente."
)

# --- RENDERIZADO DEL HISTORIAL ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "timestamp" in message:
            st.caption(f"🕒 {message['timestamp']}")

# --- ENTRADA DE USUARIO ---
user_input = st.chat_input("¿Qué deseas pedir?")

if user_input:
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.session_state.messages.append(
        {"role": "user", "content": user_input, "timestamp": timestamp}
    )
    guardar_mensaje_actual("user", user_input, timestamp)

    with st.chat_message("user"):
        st.markdown(user_input)
        st.caption(f"🕒 {timestamp}")

    if not st.session_state.titulo_actualizado:
        titulo = generar_titulo(user_input)
        if st.session_state.conversacion_id:
            actualizar_titulo(st.session_state.conversacion_id, titulo)
            st.session_state.titulo_actualizado = True

    input_data = {"messages": [HumanMessage(content=user_input)]}

    with st.spinner("Bienvenido al Bar. El mesero está generando tu solicitud..."):
        try:
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            response = supervisor_graph.invoke(input_data, config=config)

            final_message = response["messages"][-1]
            ai_message_content = (
                final_message.content
                if hasattr(final_message, "content")
                else str(final_message)
            )

            ai_timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": ai_message_content,
                    "timestamp": ai_timestamp,
                }
            )
            guardar_mensaje_actual("assistant", ai_message_content, ai_timestamp)

            with st.chat_message("assistant"):
                st.markdown(ai_message_content)
                st.caption(f"🕒 {ai_timestamp}")

        except Exception as e:
            st.error(f"Hubo un error con el mesero: {e}")
