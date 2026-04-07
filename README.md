# Bar IA - Sistema Multi-Agente con IA

Sistema de atención de bar impulsado por inteligencia artificial, construido con **LangChain**, **LangGraph** y **Groq LLM**. Simula un bar real con agentes especializados que actúan como mesero, cajero y administrador, coordinados por un supervisor que enruta las solicitudes del cliente al agente correcto.

## Tabla de Contenidos

- [Características](#características)
- [Arquitectura de Agentes](#arquitectura-de-agentes)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Flujo de Funcionamiento](#flujo-de-funcionamiento)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Base de Datos](#base-de-datos)
- [Menú de Productos](#menú-de-productos)
- [Tecnologías](#tecnologías)

## Características

- **Atención conversacional natural**: Interactúa con el bar mediante lenguaje natural como si hablaras con un mesero real
- **Múltiples agentes especializados**:
  - **Mesero**: Toma pedidos, crea cuentas, muestra el menú
  - **Cajero**: Genera facturas y procesa pagos
  - **Admin**: Consulta ventas del día, cuentas y facturas
- **Supervisor inteligente**: Clasifica la intención del cliente y lo dirige al agente correcto
- **Historial de conversaciones persistente**: Las conversaciones se guardan en base de datos con soporte para múltiples sesiones
- **Interfaz web con temática de bar**: UI construida con Streamlit y estilos neón
- **Moneda en pesos colombianos (COP)**
- **Detección de temas fuera de contexto**: Rechaza amablemente preguntas no relacionadas con el bar

## Arquitectura de Agentes

El sistema utiliza una arquitectura de **grafo dirigido con LangGraph**, donde un **Supervisor** actúa como nodo central de enrutamiento:

```
┌─────────────────────────────────────────────────────┐
│                    USUARIO                          │
│              (Interfaz Streamlit)                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   SUPERVISOR    │
              │    (Router)     │
              │  Groq LLM 20B   │
              └────────┬────────┘
                       │
          ┌────────────┼────────────────┐
          │            │                │
          ▼            ▼                ▼
   ┌──────────┐  ┌──────────┐    ┌──────────┐
   │  MESERO  │  │  CAJERO  │    │  ADMIN   │
   │  (ReAct) │  │  (ReAct) │    │  (ReAct) │
   └──────────┘  └──────────┘    └──────────┘
```

### Supervisor (Router)

- **Modelo**: Groq LLM 20B (temperatura 0)
- **Función**: Analiza los últimos 5 mensajes del usuario y decide a qué agente enviarlo
- **Decisiones posibles**:
  - `mesero` → Pedidos, menú, abrir cuentas, verificar cuentas
  - `cajero` → Pagos y facturas
  - `admin` → Reportes, consultas de cuentas y facturas
  - `fuera_de_servicio` → Temas no relacionados con el bar

### Agente Mesero

- **Modelo**: Groq LLM 20B (temperatura 0.2)
- **Tipo**: Agente ReAct con herramientas
- **Herramientas**:
  - `crear_cuenta_tool` → Crea una nueva cuenta para un cliente
  - `verificar_cuenta_activa_tool` → Verifica si ya existe una cuenta abierta
  - `listar_categorias_tool` → Muestra categorías disponibles
  - `listar_productos_por_categoria_tool` → Muestra productos y precios de una categoría
  - `crear_pedido_tool` → Agrega productos a la cuenta del cliente
- **Protocolo**:
  1. Verifica si el cliente ya tiene cuenta activa
  2. Crea cuenta si es nuevo (pide nombre y mesa)
  3. Ofrece categorías del menú
  4. Muestra productos de la categoría elegida
  5. Crea el pedido y confirma

### Agente Cajero

- **Modelo**: Groq LLM 20B (temperatura 0)
- **Tipo**: Agente ReAct con herramientas
- **Herramientas**:
  - `generar_factura_tool` → Genera la factura de una cuenta y la cierra
  - `pagar_factura_tool` → Marca una factura como pagada

### Agente Admin

- **Modelo**: Groq LLM 20B (temperatura 0)
- **Tipo**: Agente ReAct con herramientas
- **Herramientas**:
  - `ver_ventas_dia_tool` → Consulta ventas del día
  - `consultar_todas_cuentas_tool` → Lista todas las cuentas
  - `consultar_cuentas_por_nombre_tool` → Busca cuentas por nombre
  - `consultar_cuenta_por_id_tool` → Consulta cuenta por ID
  - `consultar_todas_facturas_tool` → Lista todas las facturas
  - `consultar_facturas_por_nombre_tool` → Busca facturas por nombre
  - `consultar_factura_por_id_tool` → Consulta factura por ID

## Estructura del Proyecto

```
bar_ia_agents/
├── agents_bar/                  # Agentes del bar
│   ├── __init__.py
│   ├── supervisor.py            # Grafo supervisor con routing
│   ├── mesero_agent.py          # Agente mesero (pedidos)
│   ├── cajero_agent.py          # Agente cajero (pagos)
│   └── admin_agent.py           # Agente admin (reportes)
├── database_models/             # Modelos y consultas de base de datos
│   ├── __init__.py
│   ├── db.py                    # Configuración SQLAlchemy + engine SQLite
│   ├── models.py                # Modelos: Cuenta, Pedido, Factura
│   ├── conversation_models.py   # Modelos: Conversacion, MensajeChat
│   ├── queries.py               # Funciones CRUD para cuentas/pedidos/facturas
│   └── conversation_queries.py  # Funciones CRUD para conversaciones
├── services/                    # Capa de lógica de negocio
│   ├── __init__.py
│   ├── order_service.py         # Gestión de cuentas y pedidos
│   ├── billing_service.py       # Generación y pago de facturas
│   └── product_service.py       # Carga y búsqueda de productos desde JSON
├── tools/                       # Herramientas para agentes LangChain
│   ├── order_tools.py           # Tools del mesero
│   ├── billing_tools.py         # Tools del cajero
│   └── admin_tools.py           # Tools del admin
├── ui/                          # Interfaz de usuario
│   ├── __init__.py
│   ├── streamlit_ui.py          # Aplicación Streamlit principal
│   └── styles/
│       └── neon_bar.css         # Estilos temáticos neón
├── data/
│   └── productos.json           # Menú del bar (categorías, productos, precios)
├── memory/                      # Base de datos de memoria (LangGraph checkpoint)
│   └── memory.db
├── database_bar/                # Base de datos principal del bar
│   └── bar_database.db
├── config.py                    # Configuración de variables de entorno
├── requirements.txt             # Dependencias Python
├── .env.example                 # Ejemplo de variables de entorno
└── .gitignore
```

## Flujo de Funcionamiento

1. **Inicio**: El usuario abre la interfaz Streamlit y saluda
2. **Routing**: El Supervisor analiza la intención del mensaje usando Groq LLM
3. **Ejecución del agente**:
   - El agente correspondiente recibe el historial de mensajes
   - Usa sus herramientas (tools) para interactuar con la base de datos
   - Genera una respuesta contextualizada
4. **Respuesta**: La respuesta se muestra en la UI y se guarda en el historial
5. **Persistencia**: Cada conversación se almacena con su `thread_id` para mantener contexto entre mensajes
6. **Memoria**: LangGraph usa `SqliteSaver` para mantener el estado del grafo entre invocaciones

### Ejemplo de interacción

```
Usuario: "Hola, quiero abrir una cuenta"
  → Supervisor detecta "mesero" → Mesero Agent
  → Mesero pregunta nombre y mesa
  → Crea cuenta y ofrece categorías

Usuario: "Quiero una cerveza"
  → Supervisor detecta "mesero" → Mesero Agent
  → Muestra cervezas disponibles
  → Usuario elige → Se agrega al pedido

Usuario: "Quiero pagar"
  → Supervisor detecta "cajero" → Cajero Agent
  → Genera factura con total
  → Usuario paga → Factura marcada como pagada

Usuario: "¿Cuánto se vendió hoy?"
  → Supervisor detecta "admin" → Admin Agent
  → Consulta ventas del día y muestra reporte
```

## Requisitos Previos

- **Python 3.10+** (probado con Python 3.13)
- **API Key de Groq**: Obtén una en [console.groq.com](https://console.groq.com)
- **pip** (gestor de paquetes Python)

## Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone <url-del-repositorio>
cd bar_ia_agents
```

O descarga el ZIP y extrae el contenido en tu directorio preferido.

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Configuración

### 1. Crear archivo de entorno

Copia el archivo de ejemplo y configura tus variables:

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

### 2. Configurar variables de entorno

Edita el archivo `.env` con tus datos:

```env
GROQ_API_KEY=tu_api_key_de_groq
MODEL_LLAMA_8B=llama-3.1-8b-instant
MODEL_LLAMA_70B=llama-3.1-70b-versatile
MODEL_GPT_120B=openai/gpt-oss-120b
MODEL_GPT_20B=openai/gpt-oss-20b
```

> **Nota**: Los nombres de los modelos pueden variar. Consulta los modelos disponibles en [docs.groq.com](https://console.groq.com/docs/models). El modelo principal usado es `MODEL_GPT_20B`.

### 3. Obtener API Key de Groq

1. Ve a [console.groq.com](https://console.groq.com)
2. Crea una cuenta o inicia sesión
3. Genera una API Key en la sección de API Keys
4. Copia la key en tu archivo `.env`

## Ejecución

### Iniciar la aplicación

```bash
streamlit run ui/streamlit_ui.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

### Primer uso

1. Saluda al mesero virtual (ej: "Hola, Buenas noches"), te preguntara si quieres abrir una cuenta
2. El sistema creará tu cuenta y te mostrará las categorías disponibles
3. Explora el menú y haz tus pedidos
4. Cuando quieras pagar, di "Quiero pagar" o "Cierra mi cuenta"
5. Para consultar reportes (admin), pregunta por ventas del día o cuentas

## Base de Datos

El proyecto utiliza **SQLite** con **SQLAlchemy** como ORM. Dos bases de datos separadas:

| Base de datos | Ubicación | Propósito |
|---|---|---|
| `bar_database.db` | `database_bar/` | Cuentas, pedidos, facturas |
| `memory.db` | `memory/` | Checkpoints de LangGraph (estado del grafo) |

### Modelos principales

- **Cuenta**: Representa la cuenta de un cliente (nombre, mesa, estado, fecha)
- **Pedido**: Items ordenados por un cliente (producto, precio, cantidad)
- **Factura**: Factura generada al cerrar una cuenta (total, estado)
- **Conversacion**: Sesión de chat con el usuario (thread_id, título)
- **MensajeChat**: Mensajes individuales de cada conversación (role, content)

Las tablas se crean automáticamente al iniciar la aplicación por primera vez.

## Menú de Productos

El menú se define en `data/productos.json` y es editable. Estructura:

```json
{
    "cervezas": [
        {"nombre": "Corona", "precio": 10000},
        {"nombre": "Club Colombia", "precio": 7000}
    ],
    "cocteles": [
        {"nombre": "Mojito", "precio": 18000}
    ],
    "comida": [
        {"nombre": "Hamburguesa", "precio": 25000}
    ]
}
```

Puedes agregar nuevas categorías o productos editando este archivo. Los cambios se reflejan al reiniciar la aplicación.

## Tecnologías

| Tecnología | Versión | Propósito |
|---|---|---|
| **LangChain** | 1.2.13 | Framework de orquestación de LLMs |
| **LangGraph** | 1.1.3 | Grafos de agentes con estado |
| **LangChain Groq** | 1.1.2 | Integración con Groq API |
| **Groq LLM** | - | Modelos Llama 3 (8B, 70B, etc.) |
| **Streamlit** | 1.55.0 | Interfaz web |
| **SQLAlchemy** | 2.0.48 | ORM para base de datos |
| **Pydantic** | 2.12.5 | Validación de datos |
| **python-dotenv** | 1.2.2 | Gestión de variables de entorno |
| **SQLite** | - | Base de datos embebida |

## Personalización

### Agregar nuevos productos

Edita `data/productos.json` siguiendo la estructura existente.

### Cambiar el modelo LLM

Modifica las variables `MODEL_*` en tu archivo `.env` con los nombres de modelos disponibles en Groq.

### Modificar el comportamiento de agentes

Cada agente tiene instrucciones en su archivo correspondiente (`mesero_agent.py`, `cajero_agent.py`, `admin_agent.py`). Puedes ajustar los prompts para cambiar su personalidad o reglas.

### Estilos de la interfaz

Los estilos neón se encuentran en `ui/styles/neon_bar.css`.
