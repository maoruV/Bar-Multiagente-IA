import json
from pathlib import Path
from typing import Dict, List, Optional


class ProductService:
    """
    Servicio encargado de gestionar los productos del bar.

    Este servicio actúa como la fuente de verdad para:
    - precios
    - nombres de productos
    - categorías
    """

    def __init__(self, file_path: str = "data/productos.json"):
        self.file_path = Path(file_path)
        self.productos = self._cargar_productos()

    def _cargar_productos(self) -> Dict:
        """
        Carga los productos desde el archivo JSON.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def listar_productos(self) -> List[Dict]:
        """
        Retorna todos los productos en formato lista.
        """
        lista = []

        for categoria, productos in self.productos.items():
            for producto in productos:
                lista.append({
                    "nombre": producto["nombre"],
                    "precio": producto["precio"],
                    "categoria": categoria
                })

        return lista

    def buscar_producto(self, nombre_producto: str) -> Optional[Dict]:
        """
        Busca un producto por nombre.
        """

        nombre_producto = nombre_producto.lower()

        for categoria, productos in self.productos.items():
            for producto in productos:

                if producto["nombre"].lower() == nombre_producto:
                    return {
                        "nombre": producto["nombre"],
                        "precio": producto["precio"],
                        "categoria": categoria
                    }

        return None

    def listar_por_categoria(self, categoria: str) -> List[Dict]:
        """
        Retorna productos de una categoría.
        """

        categoria = categoria.lower()

        if categoria not in self.productos:
            return []

        return self.productos[categoria]