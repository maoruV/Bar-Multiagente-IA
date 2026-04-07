from sqlalchemy.orm import Session
from database_models.models import Pedido, Factura, Cuenta


class BillingService:
    def calcular_total(self, db: Session, cuenta_id: int) -> float:
        """
        Calcula el total de una cuenta sumando sus pedidos.
        """

        pedidos = db.query(Pedido).filter(Pedido.cuenta_id == cuenta_id).all()

        total = sum(pedido.precio * pedido.cantidad for pedido in pedidos)

        return total

    def generar_factura(self, db: Session, cuenta_id: int) -> Factura:
        """
        Genera una factura para una cuenta y la cierra.
        Usa bloqueo de fila para evitar race conditions.
        """

        cuenta = (
            db.query(Cuenta).filter(Cuenta.id == cuenta_id).with_for_update().first()
        )

        if not cuenta:
            raise ValueError("Cuenta no encontrada")

        if cuenta.estado != "abierta":
            raise ValueError("La cuenta ya está cerrada")

        total = self.calcular_total(db, cuenta_id)

        if total == 0:
            raise ValueError("La cuenta no tiene pedidos")

        factura = Factura(cuenta_id=cuenta_id, total=total, estado="pendiente")

        db.add(factura)

        cuenta.estado = "cerrada"

        db.commit()
        db.refresh(factura)

        return factura

    def pagar_factura(self, db: Session, factura_id: int) -> Factura:
        """
        Marca una factura como pagada.
        """

        factura = db.query(Factura).filter(Factura.id == factura_id).first()

        if not factura:
            raise ValueError("Factura no encontrada")

        if factura.estado == "pagada":
            raise ValueError("La factura ya fue pagada")

        factura.estado = "pagada"

        db.commit()

        return factura
