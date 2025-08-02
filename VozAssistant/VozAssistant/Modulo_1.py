import sounddevice as sd
import pvporcupine
import struct
import vosk
import queue
import json
import time
from playsound import playsound

##### MODULOS DE PRUEBA CON IA COMERCIAL (procesamiento) #####
#from modulo_procesamiento.Modulo_3GPT import procesar_interaccion

##### MODULOS DE PRUEBA CON POWER AUTOMATE PARA PROCESAR IMAGENES (vision) #####
#from modulo_vision.Modulo_2PowerAutomate import captura_y_descripcion_llava

##### MODULO 2 DE PROCESAMIENTO DE IMAGEN CON PYTHON Y NO OLLAMA (vision) #####
from modulo_vision.Modulo_2Python import captura_y_descripcion_llava #✅

##### MODULO 3 DE EJECUCION LOCAL CON OLLAMA COMPLETO #####
#from modulo_vision.Modulo_2 import captura_y_descripcion_llava
from modulo_procesamiento.Modulo_3 import procesar_interaccion #✅
from modulo_procesamiento.Modulo_3 import leer_archivo
#from modulo_audio_out.Modulo_4 import leer_respuesta_y_hablar 

##### MODULO 4 DE VOZ PARA RESPUESTAS CON LIBRERIA DIFERENTE A pyttsx3 #####
#from modulo_audio_out.Modulo_4gTTS import leer_respuesta_y_hablar #✅
from modulo_audio_out.Modulo_4Azure import leer_respuesta_y_hablar #✅✅

#### MODULO AGENTE DE ACCIONES CON SELENIUM #####
from modulo_acciones.Modulo_5AccionesAlternativa import ejecutar_accion_externa
from modulo_acciones.Modulo_5AccionesAlternativa import iniciar_driver


# Confiruación inicial 
KeyWord_Start = "ok google"
KeyWord_Stop = "gracias"
Vosk_Model_Path = r"C:\Users\user\Desktop\VozAssistant\models-es\vosk-model-small-es-0.42"

# Complementos auditivos
Beep_Sound_Path = "sound.mp3"
Validacion = "validacion.mp3"
Ayuda = "pedir_ayuda.mp3"
ejecutando_accion = "ayudando.mp3"
NoAyuda = "NoAyudar.mp3"
Presentacion = "Inicio_Presentacion.mp3"
guia = "guia.mp3"
confirma_accion = "accion_realizada.mp3"
atento_a_solicitud = "esperando_otra_solicitud.mp3"


# Configuración de Vosk y el audio
q = queue.Queue()
model = vosk.Model(Vosk_Model_Path)


def start_transcription():
    print("Iniciando transcripción...")
    #captura_y_descripcion_llava(etapa="inicio")
    playsound(Beep_Sound_Path)
    rec = vosk.KaldiRecognizer(model, 16000)
    text_final = []

    def audio_callback(indata, frames, time, status):
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=audio_callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                print(f"> {text}")
                if text: text_final.append(text)
                if KeyWord_Stop in text.lower():
                    print("Comando de cierre detectado.")
                    playsound(Beep_Sound_Path)
                    break
                

#                    text_final.append(text)
    
    final_text = " ".join(text_final).strip()
    if final_text:
        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(final_text)
        return final_text
    else:
        print("No se capturó ningún texto.")
        return ""
    

def leer_transcripcion():
    try:
        with open("transcription.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def consulta_requiere_ayuda(texto):
    texto = texto.lower()
    acciones_clave = [
        "iniciar sesión", "inicia sesión", "crear cuenta", 
        "crear una cuenta", "registrarme", "registro", "buscar",
        "consultar producto", "averiguar", "mis compras", "ofertas",
        "cupones", "supermercado", "moda", "vender", "Ayuda", "PQR",
        "peticiones", "quejas", "reclamos", "carrito", "carro de compras"
    ]
    return any(accion in texto for accion in acciones_clave)


def esperar_confirmacion_usuario():
    print("Esperando confirmación del usuario...")
    rec = vosk.KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1) as stream:
        while True:
            audio_chunk, _ = stream.read(8000)
            data = bytes(memoryview(audio_chunk))

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                respuesta = result.get("text", "").lower()
                print(f"Usuario dijo: {respuesta}")
                if "sí" in respuesta or "dale" in respuesta or "hazlo" in respuesta or "por favor" in respuesta or "ayudame" in respuesta:
                    return True
                elif "no" in respuesta or "tranquilo" in respuesta:
                    return False

def guardar_nueva_peticion(texto):
    with open("nuevapeticion.txt", "w", encoding="utf-8") as f:
        f.write(texto)


def main():
    # Ejecución del driver de chrome
    driver_global = iniciar_driver()
    playsound(Presentacion)
    playsound(guia)
    print("Esperando clave para iniciar asistente...")
    porcupine = pvporcupine.create(
    access_key="cF9n3Sjf/2nCTeNIggDxieL1Raqs7AVUiEXum3g4vtSJG35WmF1rsg==",
    keywords=[KeyWord_Start]
    )
    audio_stream = sd.RawInputStream(samplerate=porcupine.sample_rate, blocksize=porcupine.frame_length, dtype='int16', channels=1)
    audio_stream.start()


    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length)[0]
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Palabra clave detectada...")
                start_transcription()
                captura_y_descripcion_llava(etapa="final")
                playsound(Validacion)
                # Procesar entrada y obtener respuesta 
                procesar_interaccion("transcription.txt", "captura_inicio.txt", "captura_final.txt")
                leer_respuesta_y_hablar("respuesta.txt")
                # Confirmar si se desea ejecutar la acción 
                if consulta_requiere_ayuda(leer_transcripcion()):
                    #leer_respuesta_y_hablar("respuesta.txt")
                    playsound(Ayuda)
                    if esperar_confirmacion_usuario():
                        playsound(ejecutando_accion)
                        nueva_peticion_usuario = start_transcription()
                        guardar_nueva_peticion(nueva_peticion_usuario)
                        resultado = ejecutar_accion_externa(nueva_peticion_usuario, driver_global)
                        if resultado:
                            playsound(confirma_accion)
                            playsound(Beep_Sound_Path) 
                    else:
                        playsound(atento_a_solicitud)
                        playsound(Beep_Sound_Path)


                print("Esperando de nuevo palabra clave...")
    except KeyboardInterrupt:
        print("Finalizando...")
        
    finally:
        audio_stream.stop()
        porcupine.delete()

if __name__ == "__main__":
    main()

