from langchain_core.tools import tool
from database_models.db import SessionLocal
from database_models.models import Cuenta, Factura
from sqlalchemy import func
from datetime import date


@tool
def ver_ventas_dia_tool():
    """
    Retorna el total de ventas del día (facturas pagadas hoy).
    """

    db = SessionLocal()

    try:
        hoy = date.today()

        total = (
            db.query(func.sum(Factura.total))
            .filter(func.date(Factura.fecha) == hoy, Factura.estado == "pagada")
            .scalar()
        )

        if total is None:
            total = 0

        return f"Ventas totales del día: ${total:,} COP"

    finally:
        db.close()


@tool
def consultar_todas_cuentas_tool():
    """
    Retorna todas las cuentas del sistema, tanto abiertas como cerradas.
    """
    db = SessionLocal()
    try:
        cuentas = db.query(Cuenta).all()
        if not cuentas:
            return "No hay cuentas registradas."

        resultado = []
        for c in cuentas:
            resultado.append(
                f"ID: {c.id} | Cliente: {c.cliente_nombre} | Mesa: {c.mesa or 'N/A'} | "
                f"Estado: {c.estado} | Apertura: {c.fecha_apertura}"
            )
        return "\n".join(resultado)
    finally:
        db.close()


@tool
def consultar_cuentas_por_nombre_tool(nombre: str):
    """
    Busca cuentas por el nombre del cliente.
    Args:
        nombre: Nombre del cliente a buscar (búsqueda parcial, no sensible a mayúsculas).
    """
    db = SessionLocal()
    try:
        cuentas = (
            db.query(Cuenta).filter(Cuenta.cliente_nombre.ilike(f"%{nombre}%")).all()
        )
        if not cuentas:
            return f"No se encontraron cuentas con el nombre '{nombre}'."

        resultado = []
        for c in cuentas:
            resultado.append(
                f"ID: {c.id} | Cliente: {c.cliente_nombre} | Mesa: {c.mesa or 'N/A'} | "
                f"Estado: {c.estado} | Apertura: {c.fecha_apertura}"
            )
        return "\n".join(resultado)
    finally:
        db.close()


@tool
def consultar_cuenta_por_id_tool(cuenta_id: int):
    """
    Busca una cuenta específica por su ID.
    Args:
        cuenta_id: ID numérico de la cuenta a consultar.
    """
    db = SessionLocal()
    try:
        cuenta = db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()
        if not cuenta:
            return f"No se encontró la cuenta con ID {cuenta_id}."

        return (
            f"ID: {cuenta.id} | Cliente: {cuenta.cliente_nombre} | Mesa: {cuenta.mesa or 'N/A'} | "
            f"Estado: {cuenta.estado} | Apertura: {cuenta.fecha_apertura}"
        )
    finally:
        db.close()


@tool
def consultar_todas_facturas_tool():
    """
    Retorna todas las facturas del sistema, tanto pagadas como pendientes.
    """
    db = SessionLocal()
    try:
        facturas = db.query(Factura).all()
        if not facturas:
            return "No hay facturas registradas."

        resultado = []
        for f in facturas:
            cuenta = f.cuenta
            cliente = cuenta.cliente_nombre if cuenta else "Desconocido"
            resultado.append(
                f"ID: {f.id} | Cuenta ID: {f.cuenta_id} | Cliente: {cliente} | "
                f"Total: ${f.total:,.0f} COP | Estado: {f.estado} | Fecha: {f.fecha}"
            )
        return "\n".join(resultado)
    finally:
        db.close()


@tool
def consultar_facturas_por_nombre_tool(nombre: str):
    """
    Busca facturas por el nombre del cliente asociado a la cuenta.
    Args:
        nombre: Nombre del cliente a buscar (búsqueda parcial, no sensible a mayúsculas).
    """
    db = SessionLocal()
    try:
        facturas = (
            db.query(Factura)
            .join(Cuenta)
            .filter(Cuenta.cliente_nombre.ilike(f"%{nombre}%"))
            .all()
        )
        if not facturas:
            return f"No se encontraron facturas con el nombre '{nombre}'."

        resultado = []
        for f in facturas:
            cuenta = f.cuenta
            cliente = cuenta.cliente_nombre if cuenta else "Desconocido"
            resultado.append(
                f"ID: {f.id} | Cuenta ID: {f.cuenta_id} | Cliente: {cliente} | "
                f"Total: ${f.total:,.0f} COP | Estado: {f.estado} | Fecha: {f.fecha}"
            )
        return "\n".join(resultado)
    finally:
        db.close()


@tool
def consultar_factura_por_id_tool(factura_id: int):
    """
    Busca una factura específica por su ID.
    Args:
        factura_id: ID numérico de la factura a consultar.
    """
    db = SessionLocal()
    try:
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        if not factura:
            return f"No se encontró la factura con ID {factura_id}."

        cuenta = factura.cuenta
        cliente = cuenta.cliente_nombre if cuenta else "Desconocido"
        return (
            f"ID: {factura.id} | Cuenta ID: {factura.cuenta_id} | Cliente: {cliente} | "
            f"Total: ${factura.total:,.0f} COP | Estado: {factura.estado} | Fecha: {factura.fecha}"
        )
    finally:
        db.close()
