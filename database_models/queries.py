import logging
from .db import engine
from .models import Base
from .conversation_models import Base as ConvBase

logger = logging.getLogger(__name__)


def crear_tablas():
    Base.metadata.create_all(bind=engine)
    ConvBase.metadata.create_all(bind=engine)
    logger.info("Tablas creadas correctamente")
