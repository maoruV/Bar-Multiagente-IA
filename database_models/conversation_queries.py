import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .db import SessionLocal
from .conversation_models import Conversacion, MensajeChat

logger = logging.getLogger(__name__)


def generar_titulo(texto: str, max_palabras: int = 20) -> str:
    palabras = texto.split()[:max_palabras]
    titulo = " ".join(palabras)
    if len(texto.split()) > max_palabras:
        titulo += "..."
    return titulo


def crear_conversacion(
    thread_id: str, titulo: str = "Nueva conversación"
) -> Conversacion:
    db = SessionLocal()
    try:
        nueva = Conversacion(
            thread_id=thread_id,
            titulo=titulo,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        logger.info(f"Conversacion creada: {thread_id}")
        return nueva
    finally:
        db.close()


def obtener_conversaciones() -> list[Conversacion]:
    db = SessionLocal()
    try:
        return db.query(Conversacion).order_by(Conversacion.updated_at.desc()).all()
    finally:
        db.close()


def obtener_conversacion_por_id(conversacion_id: int) -> Conversacion | None:
    db = SessionLocal()
    try:
        return db.query(Conversacion).filter(Conversacion.id == conversacion_id).first()
    finally:
        db.close()


def obtener_conversacion_por_thread_id(thread_id: str) -> Conversacion | None:
    db = SessionLocal()
    try:
        return (
            db.query(Conversacion).filter(Conversacion.thread_id == thread_id).first()
        )
    finally:
        db.close()


def obtener_mensajes(conversacion_id: int) -> list[MensajeChat]:
    db = SessionLocal()
    try:
        return (
            db.query(MensajeChat)
            .filter(MensajeChat.conversacion_id == conversacion_id)
            .order_by(MensajeChat.timestamp.asc())
            .all()
        )
    finally:
        db.close()


def guardar_mensaje(
    conversacion_id: int, role: str, content: str, timestamp: datetime
) -> MensajeChat:
    db = SessionLocal()
    try:
        mensaje = MensajeChat(
            conversacion_id=conversacion_id,
            role=role,
            content=content,
            timestamp=timestamp,
        )
        db.add(mensaje)

        conversacion = (
            db.query(Conversacion).filter(Conversacion.id == conversacion_id).first()
        )
        if conversacion:
            conversacion.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(mensaje)
        return mensaje
    finally:
        db.close()


def obtener_titulo_actual(conversacion_id: int) -> str | None:
    db = SessionLocal()
    try:
        conversacion = (
            db.query(Conversacion).filter(Conversacion.id == conversacion_id).first()
        )
        return conversacion.titulo if conversacion else None
    finally:
        db.close()


def actualizar_titulo(conversacion_id: int, titulo: str) -> None:
    db = SessionLocal()
    try:
        conversacion = (
            db.query(Conversacion).filter(Conversacion.id == conversacion_id).first()
        )
        if conversacion:
            conversacion.titulo = titulo
            conversacion.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Titulo actualizado: {titulo}")
    finally:
        db.close()


def eliminar_conversacion(conversacion_id: int) -> bool:
    db = SessionLocal()
    try:
        conversacion = (
            db.query(Conversacion).filter(Conversacion.id == conversacion_id).first()
        )
        if conversacion:
            db.delete(conversacion)
            db.commit()
            logger.info(f"Conversacion eliminada: {conversacion_id}")
            return True
        return False
    finally:
        db.close()
