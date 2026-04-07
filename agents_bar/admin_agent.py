from config import GROQ_API_KEY, MODEL_GPT_20B
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from tools.admin_tools import (
    ver_ventas_dia_tool,
    consultar_todas_cuentas_tool,
    consultar_cuentas_por_nombre_tool,
    consultar_cuenta_por_id_tool,
    consultar_todas_facturas_tool,
    consultar_facturas_por_nombre_tool,
    consultar_factura_por_id_tool,
)


# Modelo LLM
llm = ChatGroq(model=MODEL_GPT_20B, temperature=0, api_key=GROQ_API_KEY)


# Tools disponibles
tools = [
    ver_ventas_dia_tool,
    consultar_todas_cuentas_tool,
    consultar_cuentas_por_nombre_tool,
    consultar_cuenta_por_id_tool,
    consultar_todas_facturas_tool,
    consultar_facturas_por_nombre_tool,
    consultar_factura_por_id_tool,
]


admin_agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=(
        "Eres el administrador del bar. "
        "Tu trabajo es consultar información del negocio. "
        ""
        "Puedes: "
        "- Ver ventas del día con ver_ventas_dia_tool "
        "- Consultar información de facturas y estadísticas "
        "- Cosultar todas las cuentas con consultar_todas_cuentas_tool()"
        ""
        "Reglas: "
        "1. Usa ver_ventas_dia_tool cuando te pregunten por las ventas. "
        "2. Responde de forma clara con datos numéricos. "
        "3. Moneda en pesos colombianos (COP). "
        ""
        "Ejemplos: "
        "Usuario: 'cuánto se ha vendido hoy' -> ver_ventas_dia_tool() "
        "Usuario: 'ventas del día' -> ver_ventas_dia_tool() "
        "Usuario: 'consultar todas las cuentas' -> consultar_todas_cuentas_tool() "
        "Usuario: 'consultar cuentas por nombre: Maria' -> consultar_cuentas_por_nombre_tool('Maria') "
        "Usuario: 'consultar cuentas por nombre: Maria' -> consultar_cuentas_por_nombre_tool('Maria', estado='abierta') "
        "Usuario: 'consultar cuenta por id: 5' -> consultar_cuenta_por_id_tool(5) "
        "Usuario: 'consultar cuenta por id: 5' -> consultar_cuenta_por_id_tool(5, estado='abierta') "
        "Usuario: 'consultar todas las facturas' -> consultar_todas_facturas_tool() "
        "Usuario: 'consultar facturas por nombre: Carlos' -> consultar_facturas_por_nombre_tool('Carlos') "
        "Usuario: 'consultar facturas por nombre: Carlos' -> consultar_facturas_por_nombre_tool('Carlos', estado='pendiente') "
        "Usuario: 'consultar factura por id: 12' -> consultar_factura_por_id_tool(12) "
        "Usuario: 'consultar factura por id: 12' -> consultar_factura_por_id_tool(12, estado='pagada') "
    ),
)
