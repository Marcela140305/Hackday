import os
import requests
import json

# Tu clave API de Gemini
API_KEY = "AIzaSyAwicw6e-4imoMHq1HOYV9a_9UfDp3IgoA"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"

def leer_archivo(path):
    if not path or not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def construir_prompt(transcripcion_path, inicio_path, final_path):
    transcripcion = leer_archivo(transcripcion_path)
    descripcion_final = leer_archivo(final_path)

    prompt = f"""Actúa como un asistente virtual que observa la pantalla de un usuario y escucha su voz.
Tienes la transcripción de lo que dijo el usuario y la descripción de lo que se ve en pantalla después de hablar.

TRANSCRIPCIÓN DE VOZ:
{transcripcion}

DESCRIPCIÓN DE PANTALLA FINAL:
{descripcion_final}

Responde al usuario de forma clara, útil y contextual.
"""
    return prompt

def procesar_interaccion(transcripcion_path, inicio_path, final_path):
    prompt = construir_prompt(transcripcion_path, inicio_path, final_path)

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(ENDPOINT, json=payload)
        response.raise_for_status()
        data = response.json()
        respuesta = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        respuesta = respuesta.strip()

        print(f"\nRESPUESTA DEL ASISTENTE:\n{respuesta}\n")
        with open("respuesta.txt", "w", encoding="utf-8") as f:
            f.write(respuesta)
    except Exception as e:
        print(f"Error al consultar la API de Gemini: {e}")