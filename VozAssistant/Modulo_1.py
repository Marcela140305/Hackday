import sounddevice as sd
import pvporcupine
import struct
import vosk
import queue
import json
import os
from playsound import playsound

from modulo_vision.Modulo_2 import captura_y_descripcion_llava
from modulo_procesamiento.Modulo_3 import procesar_interaccion
#from modulo_procesamiento.Modulo_3GPT import procesar_interaccion
from modulo_audio_out.Modulo_4 import leer_respuesta_y_hablar

# Confiruación inicial 
KeyWord_Start = "ok google"
KeyWord_Stop = "gracias"
Vosk_Model_Path = r"C:\Users\user\Desktop\VozAssistant\models-es\vosk-model-small-es-0.42"
Beep_Sound_Path = "sound.mp3"


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
    else:
        print("No se capturó ningún texto.")



def main():
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
                procesar_interaccion("transcription.txt", "captura_inicio.txt", "captura_final.txt")
                leer_respuesta_y_hablar("respuesta.txt")
                print("Esperando de nuevo palabra clave...")
    except KeyboardInterrupt:
        print("Finalizando...")
        
    finally:
        audio_stream.stop()
        porcupine.delete()

if __name__ == "__main__":
    main()

