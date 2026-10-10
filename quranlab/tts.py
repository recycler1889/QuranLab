"""Synthèse vocale neuronale hors-ligne (Piper).

Piper (https://github.com/rhasspy/piper) exécute des voix neuronales en local
via ``onnxruntime`` : aucune clé, aucun compte, aucun quota. Il fournit
**plusieurs voix françaises** au choix, indépendantes des voix installées dans
le système, et ne risque pas d'épeler lettre à lettre.

Ce module est un mince adaptateur : import paresseux de ``piper`` (pour que
l'application reste utilisable même sans la dépendance), téléchargement à la
demande du modèle, mise en cache du modèle chargé et synthèse en mémoire.
"""

from __future__ import annotations

import io
import threading
import wave
from pathlib import Path

from . import config

_LOCK = threading.Lock()
_SYNTH_LOCK = threading.Lock()
_CACHE: dict[str, object] = {}


def available() -> bool:
    """Vrai si ``piper`` (et donc onnxruntime) est importable."""
    try:
        import piper  # noqa: F401

        return True
    except Exception:  # noqa: BLE001 — dépendance optionnelle
        return False


def model_path(voice_name: str) -> Path:
    """Chemin attendu du modèle ``.onnx`` d'une voix Piper."""
    return Path(config.PIPER_DIR) / f"{voice_name}.onnx"


def ensure_model(voice_name: str) -> Path:
    """Télécharge le modèle de la voix s'il est absent, puis renvoie son chemin.

    Les modèles Piper (~20-60 Mo) proviennent du dépôt HuggingFace officiel
    ``rhasspy/piper-voices`` et sont stockés dans ``config.PIPER_DIR`` (une seule
    fois). Sur un hébergement éphémère, le téléchargement se reproduit au
    redémarrage — d'où la mise en cache mémoire agressive ci-dessous.
    """
    onnx = model_path(voice_name)
    if onnx.exists():
        return onnx
    dest = Path(config.PIPER_DIR)
    dest.mkdir(parents=True, exist_ok=True)
    from piper.download_voices import download_voice

    download_voice(voice_name, dest)
    if not onnx.exists():
        raise FileNotFoundError(
            f"modèle Piper introuvable après téléchargement : {voice_name}"
        )
    return onnx


def load(voice_name: str):
    """Charge (et mémoïse) un modèle Piper."""
    with _LOCK:
        cached = _CACHE.get(voice_name)
        if cached is not None:
            return cached
        onnx = ensure_model(voice_name)
        from piper import PiperVoice

        voice = PiperVoice.load(str(onnx))
        _CACHE[voice_name] = voice
        return voice


def synthesize_wav(text: str, voice_name: str, rate: float = 1.0) -> bytes:
    """Synthétise ``text`` et renvoie les octets d'un fichier WAV.

    ``rate`` suit la convention de l'interface (1.0 = normal ; > 1 plus rapide) ;
    il est converti en ``length_scale`` Piper (inverse de la vitesse).
    """
    text = (text or "").strip()
    if not text:
        return b""
    voice = load(voice_name)
    syn_config = None
    try:
        from piper import SynthesisConfig

        try:
            rate = float(rate)
        except (TypeError, ValueError):
            rate = 1.0
        length_scale = 1.0 / rate if rate > 0 else 1.0
        syn_config = SynthesisConfig(length_scale=length_scale)
    except Exception:  # noqa: BLE001 — API plus ancienne sans SynthesisConfig
        syn_config = None

    buf = io.BytesIO()
    with _SYNTH_LOCK:
        with wave.open(buf, "wb") as wf:
            voice.synthesize_wav(text, wf, syn_config=syn_config)
    return buf.getvalue()
