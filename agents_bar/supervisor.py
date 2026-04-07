from config import GROQ_API_KEY, MODEL_GPT_20B
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, Annotated

from langgraph.graph.message import add_messages

from agents_bar.mesero_agent import mesero_agent
from agents_bar.cajero_agent import cajero_agent
from agents_bar.admin_agent import admin_agent

from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

memory_conn = sqlite3.connect("memory/memory.db", check_same_thread=False)

checkpointer = SqliteSaver(memory_conn)


# Modelo para decidir el routing
llm = ChatGroq(model=MODEL_GPT_20B, temperature=0, api_key=GROQ_API_KEY)


# Estado del grafo
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next: str


# Prompt del supervisor
supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Eres el Supervisor del Bar IA. Tu trabajo es dirigir al cliente al agente correcto:
- 'mesero': pedidos, menú, abrir cuentas, verificar cuentas.
- 'cajero': pagos y facturas.
- 'admin': reportes, consultar cuentas, consultar facturas.
- 'fuera_de_servicio': Si el cliente pregunta cosas que NO son del bar (historia, ciencia, tareas, consejos, etc.)

Responde solo con la palabra clave: mesero, cajero o admin.
""",
        ),
        ("human", "{input}"),
    ]
)


def router(state: AgentState):
    # Pasamos los últimos 5 mensajes para tener contexto pero no saturar
    contexto = state["messages"][-5:]

    prompt = supervisor_prompt.invoke({"input": contexto})
    decision = llm.invoke(prompt)

    next_agent = decision.content.strip().lower()

    # Lógica de redirección
    if "cajero" in next_agent:
        return {"next": "cajero"}
    if "admin" in next_agent:
        return {"next": "admin"}
    if "mesero" in next_agent:
        return {"next": "mesero"}

    # Si detecta que está fuera de lugar, lo mandamos a un mensaje de rechazo
    return {"next": "fuera_de_servicio"}


# Función nodo mesero
def mesero_node(state: AgentState):
    # Invocamos al agente enviándole el historial actual
    result = mesero_agent.invoke({"messages": state["messages"]})

    # Extraemos el ÚLTIMO mensaje (la respuesta final del agente)
    # Esto asegura que enviamos un objeto BaseMessage limpio al grafo principal
    nuevo_mensaje = result["messages"][-1]

    return {"messages": [nuevo_mensaje]}


# Nodo cajero
def cajero_node(state: AgentState):
    result = cajero_agent.invoke({"messages": state["messages"]})
    nuevo_mensaje = result["messages"][-1]
    return {"messages": [nuevo_mensaje]}


# Nodo admin
def admin_node(state: AgentState):
    result = admin_agent.invoke({"messages": state["messages"]})
    nuevo_mensaje = result["messages"][-1]
    return {"messages": [nuevo_mensaje]}


def fuera_de_servicio_node(state: AgentState):
    mensaje = "Estimado cliente, estoy aquí exclusivamente para atenderle en el bar. No puedo responder preguntas de otros temas, pero ¿le gustaría crear una cuenta para empezar o ya tienes una?"
    return {"messages": [("assistant", mensaje)]}


# Crear grafo
workflow = StateGraph(AgentState)

workflow.add_node("router", router)
workflow.add_node("mesero", mesero_node)
workflow.add_node("cajero", cajero_node)
workflow.add_node("admin", admin_node)
workflow.add_node("fuera_de_servicio", fuera_de_servicio_node)
workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    lambda x: x["next"],
    {
        "mesero": "mesero",
        "cajero": "cajero",
        "admin": "admin",
        "fuera_de_servicio": "fuera_de_servicio",
    },
)

workflow.add_edge("mesero", END)
workflow.add_edge("cajero", END)
workflow.add_edge("admin", END)
workflow.add_edge(
    "fuera_de_servicio", END
)  # Después de informar que no puede responder, termina la conversación

supervisor_graph = workflow.compile(checkpointer=checkpointer)
