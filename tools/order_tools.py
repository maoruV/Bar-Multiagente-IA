from langchain_core.tools import tool
from services.product_service import ProductService
from services.order_service import OrderService
from database_models.db import SessionLocal
from database_models.models import Cuenta
from typing import Optional


product_service = ProductService()
order_service = OrderService()


@tool
def crear_pedido_tool(cuenta_id: int, producto: str, cantidad: int):
    """
    Crea un pedido en la cuenta de un cliente.

    Args:
        cuenta_id: ID de la cuenta del cliente
        producto: Nombre del producto a pedir
        cantidad: Cantidad de unidades
    """

    db = SessionLocal()

    try:
        producto_data = product_service.buscar_producto(producto)

        if not producto_data:
            return f"El producto '{producto}' no existe en el menú."

        pedido = order_service.crear_pedido(
            db=db,
            cuenta_id=cuenta_id,
            producto=producto_data["nombre"],
            precio=producto_data["precio"],
            cantidad=cantidad,
        )

        total = producto_data["precio"] * cantidad

        return (
            f"Pedido agregado: {cantidad}x {producto_data['nombre']} - ${total:,} COP"
        )

    finally:
        db.close()


@tool
def crear_cuenta_tool(cliente_nombre: str, mesa: str):  # <--- Eliminamos el '= None'
    """
    Crea una nueva cuenta para un cliente.
    Nota: Si no conoces la mesa, usa 'Barra'.
    """
    db = SessionLocal()
    try:
        # Aquí ya no llegará None, llegará un string (ej. "Barra")
        cuenta = order_service.crear_cuenta(
            db=db, cliente_nombre=cliente_nombre, mesa=mesa
        )
        return f"Cuenta creada: ID {cuenta.id}, Cliente {cuenta.cliente_nombre}, Mesa {cuenta.mesa}"
    finally:
        db.close()


@tool
def listar_categorias_tool():
    """
    Retorna la lista de todas las categorías de productos disponibles en el bar
    (ej: Cervezas, Cócteles, Entradas). Úsala para ofrecer opciones al cliente.
    """
    # Obtenemos las llaves del diccionario de productos cargado en el service
    categorias = list(product_service.productos.keys())
    return f"Categorías disponibles: {', '.join(categorias)}"


@tool
def listar_productos_por_categoria_tool(categoria: str):
    """
    Retorna los productos y sus precios de una categoría específica.
    Args:
        categoria: El nombre de la categoría (ej: 'Cervezas').
    """
    productos = product_service.listar_por_categoria(categoria)

    if not productos:
        return f"Lo siento, no encontré productos en la categoría '{categoria}'."

    respuesta = f"Productos en {categoria}:\n"
    for p in productos:
        respuesta += f"- {p['nombre']}: ${p['precio']:,} COP\n"

    return respuesta


@tool
def verificar_cuenta_activa_tool(cliente_nombre: str):
    """
    Busca si ya existe una cuenta abierta para un nombre específico.
    Úsala ANTES de crear una cuenta para evitar duplicados.
    """
    db = SessionLocal()
    try:
        # Buscamos la cuenta en la base de datos (puedes ajustar la lógica de búsqueda)

        cuenta = (
            db.query(Cuenta)
            .filter(
                Cuenta.cliente_nombre.ilike(f"%{cliente_nombre}%"),
                Cuenta.estado == "abierta",
            )
            .first()
        )

        if cuenta:
            return f"EXISTE: Cuenta ID {cuenta.id} a nombre de {cuenta.cliente_nombre} en mesa {cuenta.mesa}."
        return "NO_EXISTE: No hay cuentas abiertas con ese nombre."
    finally:
        db.close()
