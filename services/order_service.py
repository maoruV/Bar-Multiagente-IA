from sqlalchemy.orm import Session
from database_models.models import Pedido, Cuenta


class OrderService:
    def crear_cuenta(self, db: Session, cliente_nombre: str, mesa: str = None):
        """
        Crea una nueva cuenta para un cliente.
        """

        nueva_cuenta = Cuenta(
            cliente_nombre=cliente_nombre, mesa=mesa, estado="abierta"
        )

        db.add(nueva_cuenta)
        db.commit()
        db.refresh(nueva_cuenta)

        return nueva_cuenta

    def obtener_cuenta(self, db: Session, cuenta_id: int):
        """
        Obtiene una cuenta por su ID.
        """

        return db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()

    def crear_pedido(
        self, db: Session, cuenta_id: int, producto: str, precio: float, cantidad: int
    ):
        """
        Crea un pedido en la base de datos.
        """

        cuenta = db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()

        if not cuenta:
            raise ValueError(f"Cuenta {cuenta_id} no encontrada")

        if cuenta.estado != "abierta":
            raise ValueError(f"La cuenta {cuenta_id} está {cuenta.estado}")

        nuevo_pedido = Pedido(
            cuenta_id=cuenta_id, producto=producto, precio=precio, cantidad=cantidad
        )

        db.add(nuevo_pedido)
        db.commit()
        db.refresh(nuevo_pedido)

        return nuevo_pedido

    def obtener_pedidos_cuenta(self, db: Session, cuenta_id: int):
        """
        Obtiene todos los pedidos de una cuenta.
        """

        return db.query(Pedido).filter(Pedido.cuenta_id == cuenta_id).all()
