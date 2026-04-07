from langchain_core.tools import tool
from services.billing_service import BillingService
from database_models.db import SessionLocal


billing_service = BillingService()


@tool
def generar_factura_tool(cuenta_id: int):
    """
    Genera la factura de una cuenta.

    Args:
        cuenta_id: ID de la cuenta a facturar
    """

    db = SessionLocal()

    try:
        result = billing_service.generar_factura(db=db, cuenta_id=cuenta_id)

        return f"Factura generada. Total a pagar: ${result.total:,} COP. Factura ID: {result.id}"

    except ValueError as e:
        return f"Error: {e}"

    finally:
        db.close()


@tool
def pagar_factura_tool(factura_id: int):
    """
    Marca una factura como pagada.

    Args:
        factura_id: ID de la factura a pagar
    """

    db = SessionLocal()

    try:
        result = billing_service.pagar_factura(db=db, factura_id=factura_id)

        return (
            f"Factura {factura_id} pagada correctamente. Total: ${result.total:,} COP"
        )

    except ValueError as e:
        return f"Error: {e}"

    finally:
        db.close()
