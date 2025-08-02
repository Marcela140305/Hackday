import os
import azure.cognitiveservices.speech as speechsdk

speech_key = "FVjcONVWEQIYOEyYZxvGTGQbu0xQhY2L63CWEq2BrD0hsWpyzyubJQQJ99BGACHYHv6XJ3w3AAAYACOGPihA"
region = "eastus2"

def leer_respuesta_y_hablar(path_respuesta="respuesta.txt", voz="es-CO-SalomeNeural"):
    if not os.path.exists(path_respuesta):
        print("No se encontró el archivo de respuesta.")
        return

    with open(path_respuesta, "r", encoding="utf-8") as f:
        texto = f.read().strip()

    if not texto:
        print("El archivo de respuesta está vacío.")
        return

    print(f"\nLEYENDO RESPUESTA:\n{texto}\n")

    # Configuración de síntesis
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
    speech_config.speech_synthesis_voice_name = voz

    # Crear el sintetizador
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    # Ejecutar síntesis
    result = synthesizer.speak_text_async(texto).get()

    # Validación de resultado
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Voz reproducida correctamente.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print(f"Síntesis cancelada: {cancellation.reason}")
        if cancellation.reason == speechsdk.CancellationReason.Error:
            print(f"Detalles del error: {cancellation.error_details}")