import json
from transformers import pipeline

_pipe = None

def _get_pipe():
    global _pipe
    if _pipe is None:
        _pipe = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct",
                         max_new_tokens=500, do_sample=False, return_full_text=False)
    return _pipe

def write_insights(own, own_name, comp, comp_name):
    prompt = (
        "Eres analista de moda y escribes para una buyer que no es técnica.\n"
        f"Datos de {own_name} (marca propia): {json.dumps(own)}\n"
        f"Datos de {comp_name} (competidor): {json.dumps(comp)}\n"
        "Los porcentajes de prendas son la proporción de fotos que contienen esa prenda.\n"
        "Escribe exactamente 5 insights, uno por línea, numerados. Cada insight: "
        "una frase simple que compare ambas marcas y termine con una acción sugerida "
        "para la buyer. Usa SOLO los números dados, no inventes datos."
    )
    out = _get_pipe()([{"role": "user", "content": prompt}])[0]["generated_text"]
    if isinstance(out, list):
        out = out[-1]["content"]
    return out

import re

def phrase_fact(fact):
    prompt = (
        "Eres analista de moda. Reescribe este dato para una buyer no técnica en UNA frase "
        "simple y añade una acción sugerida. Usa exactamente los mismos porcentajes, "
        f"sin añadir otros números.\nDato: {fact}"
    )
    out = _get_pipe()([{"role": "user", "content": prompt}])[0]["generated_text"]
    if isinstance(out, list):
        out = out[-1]["content"]
    out = out.strip()
    if set(re.findall(r"\d+", out)) <= set(re.findall(r"\d+", fact)):
        return out
    return fact + "."          # si inventó números, usamos el dato tal cual