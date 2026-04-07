import os
from dotenv import load_dotenv

load_dotenv()

__all__ = [
    "GROQ_API_KEY",
    "MODEL_LLAMA_8B",
    "MODEL_LLAMA_70B",
    "MODEL_GPT_120B",
    "MODEL_GPT_20B",
]

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_LLAMA_8B = os.getenv("MODEL_LLAMA_8B")
MODEL_LLAMA_70B = os.getenv("MODEL_LLAMA_70B")
MODEL_GPT_120B = os.getenv("MODEL_GPT_120B")
MODEL_GPT_20B = os.getenv("MODEL_GPT_20B")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY no encontrada. Crea un archivo .env con: GROQ_API_KEY=tu_api_key"
    )
