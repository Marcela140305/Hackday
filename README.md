**Documentación del Proyecto VozAssistant - Hackday NDR-DevOPs-Core**

**Introducción:**

El presente documento detalla el desarrollo y la estructura del proyecto "VozAssistant", una herramienta creada durante el Hackday del equipo NDR-DevOPs-Core. El objetivo de este asistente de voz conversacional llamado ZOK. La documentación está organizada por módulos para facilitar la comprensión de cada componente y su rol dentro del sistema.

-----
**2. Módulo por Módulo**

**Módulo 1. modulo\_acciones**

Este módulo contiene la lógica principal para manejar las acciones.

**Propósito:**

Este módulo es el "corazón" del asistente, ya que se encarga de interpretar las instrucciones recibidas y ejecutar las acciones correspondientes. Es aquí donde se define la lógica para cada comando o tarea que el asistente puede realizar.

**Archivos Contenidos:**

- \_\_init\_\_.py: Este archivo indica que modulo\_acciones es un paquete de Python. A menudo se utiliza para inicializar el paquete, definir variables o importar módulos que se usarán comúnmente.
- Modulo\_5Acciones.py: Este archivo contiene la implementación principal de las acciones. Aquí se define la lógica para tareas como a*brir e interactuar con URLs de sitios dedicados y/o aplicaciones, realizar búsquedas, interactuar con APIs, proporcionar al usuario un acompañamiento completo sobre el sitio que este desee utilizar*.
- Modulo\_5AccionesAlternativa. Sobre este archivo existe una implementación alternativa para las acciones, una optimización o un enfoque diferente para el mismo conjunto de tareas. 
-----
**3. Continuación con la Estructura General del Proyecto**

**Estructura General del Proyecto**

El proyecto "ZOK" está organizado en los siguientes directorios y archivos principales:

- venv: Entorno virtual de Python. Contiene las bibliotecas y dependencias del proyecto.
- \_\_pycache\_\_: Directorio generado por Python para almacenar los archivos bytecode compilados (.pyc).
- chromedriver-win\_64: Controlador para el navegador Chrome, necesario para automatizar tareas web.
- models-es: Modelos para el procesamiento de lenguaje natural en español.
- modulo\_acciones: Contiene la lógica para la ejecución de comandos (el módulo anteriormente relacionado).
- modulo\_audio\_out: Lógica para la salida de audio (la voz del asistente).
- modulo\_procesamiento: Lógica para el procesamiento de la entrada (el audio del usuario).
- modulo\_visión: Módulo relacionado con tareas de visión artificial.
- ayudando.mp3: Archivo de audio para la respuesta "ayudando".
- pedir\_ayuda.mp3: Archivo de audio para la respuesta "puedes pedir ayuda".
- respuesta.mp3: Archivo de audio para la respuesta estándar.
- sound.mp3: Archivo de audio genérico.
- validacion.mp3: Archivo de audio para la respuesta "validando".
- captura\_final.png: Captura de pantalla final (ve en tiempo real lo que el usuario esta visualizando en pantalla ayudando al optimo acompañamiento de la IA de cara al usuario).
- captura\_final.txt: Archivo de texto relacionado con la captura (misma acción). 
- transcription.txt: Archivo de texto para almacenar la transcripción del audio del usuario.
- nuevaapeticion.txt: Archivo de texto para la nueva petición.
- respuesta.txt: Archivo de texto para la respuesta.
- Modulo\_1.py: Posiblemente el archivo principal o un módulo de inicialización del sistema.

**Módulos al detalle:**

**1. Módulo modulo\_acciones**

Este módulo se encarga de la automatización y la interacción con aplicaciones web específicas, en este caso, Mercado Libre. Utiliza la biblioteca Selenium para controlar el navegador web y simular acciones de un usuario.

- **Alcance del Módulo:**
  - Automatización de tareas en la web, en este caso, en el sitio de Mercado Libre.
  - Interpretar comandos de voz del usuario para traducirlos en clics, búsquedas y navegación.
  - Gestionar el ciclo de vida del navegador web (iniciar, cerrar, etc.).
- **Llamado del Módulo:**
  - Este módulo es llamado desde el agente principal del proyecto (ejecutar\_accion\_externa) al detectar que la petición del usuario requiere una acción en el navegador web.
  - Las funciones internas (buscar\_producto, iniciar\_sesion, etc.) son llamadas por la función ejecutar\_accion\_externa.
- **Cadenas de Funcionamiento:**
  - La función ejecutar\_accion\_externa recibe una cadena de texto (la transcripción de la voz del usuario) y la evalúa para identificar palabras clave ("buscar", "iniciar sesión", etc.).
  - Basado en la palabra clave, llama a la función correspondiente (buscar\_producto, iniciar\_sesion, etc.), pasando como argumento el objeto driver del navegador y, en algunos casos, el término de búsqueda.
  - El resultado es una cadena de texto que indica si la acción fue exitosa o si hubo un error.
- **Desglose del Código:**
  - iniciar\_driver():
    - **Funcionalidad:** Configura y lanza una instancia del navegador Google Chrome.
    - **Detalles:**
      - Configura opciones como maximizar la ventana y desactivar notificaciones y extensiones para una experiencia de automatización limpia.
      - Define la ruta al ejecutable del chromedriver.
      - Carga la página de inicio de Mercado Libre como punto de partida.
      - Devuelve el objeto driver que se utiliza para todas las interacciones subsiguientes.
  - buscar\_producto(driver, termino):
    - **Funcionalidad:** Navega a la página de inicio de Mercado Libre, busca una barra de búsqueda y simula la escritura y el envío de un término de búsqueda.
    - **Detalles:** Utiliza driver.find\_element(By.NAME, "as\_word") para localizar la barra de búsqueda y send\_keys para ingresar el texto y presionar "Enter".
  - iniciar\_sesion(driver):
    - **Funcionalidad:** Navega a la página de inicio de Mercado Libre y hace clic en el enlace para iniciar sesión.
    - **Detalles:** Localiza el enlace por su texto visible (By.LINK\_TEXT, "Ingresa") y simula un clic.
  - crear\_cuenta(driver):
    - **Funcionalidad:** Navega a la página de inicio y hace clic en el enlace para crear una cuenta.
    - **Detalles:** Similar a la función de inicio de sesión, localiza el enlace por su texto (By.LINK\_TEXT, "Crea tu cuenta") y hace clic en él.
  - click\_enlace\_por\_texto(driver, texto\_visible):
    - **Funcionalidad:** Función genérica para hacer clic en cualquier enlace o botón que contenga un texto específico.
    - **Detalles:** Utiliza By.XPATH para buscar elementos <a> que contengan el texto\_visible. Esto la hace reutilizable para diversas acciones como ir al carrito, mis compras, etc.
  - ejecutar\_accion\_externa(texto\_usuario, driver):
    - **Funcionalidad:** Esta es la función principal del módulo. Recibe la transcripción del usuario y, a través de una serie de condicionales (if/elif), determina qué acción ejecutar.
    - **Detalles:** Analiza el texto del usuario en minúsculas y, si encuentra una palabra clave, llama a la función de acción correspondiente. Esto actúa como un router de comandos.
-----
**2. Módulo modulo\_audio**

Este módulo es responsable de la síntesis de voz (Text-to-Speech). Su función principal es tomar un texto y convertirlo en audio para que el asistente pueda "hablar" al usuario.

- **Alcance del Módulo:**
  - Generar una respuesta hablada a partir de un archivo de texto.
  - Utilizar el servicio de Azure Cognitive Services para la síntesis de voz.
  - Manejar la configuración de la voz (idioma, voz específica).
- **Llamado del Módulo:**
  - Se llama después de que el modulo\_procesamiento ha generado una respuesta en texto y la ha guardado en el archivo respuesta.txt.
  - La función leer\_respuesta\_y\_hablar se ejecuta para leer este archivo y reproducir el audio.
- **Cadenas de Funcionamiento:**
  - La función leer\_respuesta\_y\_hablar recibe la ruta del archivo respuesta.txt.
  - Lee el contenido del archivo.
  - Configura el servicio de Azure Speech SDK (speechsdk.SpeechConfig).
  - Crea un sintetizador de voz y le pasa el texto leído.
  - El servicio de Azure genera el audio, que es reproducido en el sistema del usuario.
- **Desglose del Código:**
  - speech\_key y region: Variables de configuración para autenticarse con el servicio de Azure.
  - leer\_respuesta\_y\_hablar(path\_respuesta, voz):
    - **Funcionalidad:** La única función del módulo. Lee un archivo de texto, configura el sintetizador de voz de Azure y reproduce el texto como audio.
    - **Detalles:**
      - Verifica la existencia del archivo de respuesta.
      - Usa speechsdk.SpeechConfig para autenticarse con Azure y especificar el idioma y la voz (es-CO-SalomeNeural).
      - Crea una instancia de SpeechSynthesizer.
      - Llama a speak\_text\_async() para iniciar la síntesis. El .get() espera a que la operación termine.
      - Incluye lógica para manejar errores y notificar si la síntesis se cancela o falla.




-----
**3. Módulo modulo\_procesamiento**

Este módulo es el cerebro del asistente. Se encarga de construir el prompt con la información del usuario y del entorno (la pantalla) y de consultar un modelo de lenguaje (LLM) para obtener una respuesta.

- **Alcance del Módulo:**
  - Combinar la transcripción del usuario y la descripción de la pantalla en un único prompt.
  - Interactuar con un modelo de lenguaje local (Ollama) a través de una API.
  - Procesar la respuesta del LLM y guardarla en un archivo para el módulo de audio.
- **Llamado del Módulo:**
  - Este módulo es el paso central en la cadena de interacción. Se llama después de que se ha obtenido la transcripción de voz y la descripción de la pantalla.
  - La función procesar\_interaccion es la que inicia todo el proceso.
- **Cadenas de Funcionamiento:**
  - La función procesar\_interaccion llama a construir\_prompt para crear la entrada para el LLM.
  - construir\_prompt lee los archivos de texto generados por otros módulos (transcripcion.txt, captura\_final.txt).
  - El prompt se forma combinando la transcripción y la descripción de la pantalla.
  - La función consultar\_llm envía este prompt al modelo local de Ollama.
  - Una vez que se recibe la respuesta del LLM, se guarda en el archivo respuesta.txt, que será leído por el modulo\_audio.
- **Desglose del Código:**
  - leer\_archivo(path):
    - **Funcionalidad:** Función auxiliar para leer el contenido de un archivo de texto.
    - **Detalles:** Incluye una verificación para asegurarse de que el archivo existe antes de intentar leerlo.
  - construir\_prompt(transcripcion\_path, inicio\_path, final\_path):
    - **Funcionalidad:** Crea la instrucción completa para el modelo de lenguaje, combinando el contexto de la voz y la visión.
    - **Detalles:** Arma un prompt que le pide al LLM actuar como un asistente virtual y le proporciona la transcripción y la descripción de la pantalla como contexto.
  - consultar\_llm(prompt):
    - **Funcionalidad:** Se conecta a la API local de Ollama para enviar el prompt y obtener una respuesta del modelo de lenguaje.
    - **Detalles:** Usa la biblioteca requests para realizar una petición POST. El payload incluye el modelo a usar (mistral:latest), el prompt y la configuración para no usar streaming.
  - procesar\_interaccion(transcripcion\_path, inicio\_path, final\_path):
    - **Funcionalidad:** La función principal del módulo. Orquesta la construcción del prompt, la consulta al LLM y el almacenamiento de la respuesta.
    - **Detalles:** Llama a las funciones auxiliares en el orden correcto y maneja la escritura de la respuesta en el archivo respuesta.txt.
-----
**4. Módulo modulo\_vision**

Este módulo es el "ojo" del asistente. Su tarea es capturar la pantalla del computador, extraer el texto visible y preparar esa información para que el módulo de procesamiento la use como contexto.

- **Alcance del Módulo:**
  - Capturar una imagen de la pantalla principal del usuario.
  - Utilizar OCR (Reconocimiento Óptico de Caracteres) para extraer el texto de la imagen capturada.
  - Almacenar la captura de pantalla y el texto extraído en archivos para su posterior uso.
- **Llamado del Módulo:**
  - Este módulo es llamado al inicio y al final de una interacción para obtener el contexto visual.
  - Las funciones capturar\_pantalla y extraer\_texto son llamadas dentro de la función captura\_y\_descripcion\_llava.

- **Cadenas de Funcionamiento:**
  - La función captura\_y\_descripcion\_llava es el punto de entrada.
  - Llama a capturar\_pantalla para tomar una imagen de la pantalla y guardarla como un archivo .png.
  - Luego, llama a extraer\_texto, que utiliza la biblioteca pytesseract para analizar la imagen y convertir el texto de la imagen en una cadena de texto.
  - El texto extraído se guarda en un archivo .txt, que es uno de los inputs para el modulo\_procesamiento.
- **Desglose del Código:**
  - pytesseract.pytesseract.tesseract\_cmd: Configuración de la ruta al ejecutable de Tesseract OCR, una herramienta fundamental para el reconocimiento de texto.
  - capturar\_pantalla(nombre\_archivo):
    - **Funcionalidad:** Toma una captura de pantalla del monitor principal.
    - **Detalles:** Usa la biblioteca mss (Multi-platform Screen Shot) para obtener una imagen de la pantalla. La imagen se guarda en el disco duro.
  - extraer\_texto(img\_path):
    - **Funcionalidad:** Realiza el OCR en la imagen capturada para obtener el texto.
    - **Detalles:** Abre la imagen con la biblioteca Pillow (PIL) y utiliza pytesseract.image\_to\_string para extraer el texto.
  - captura\_y\_descripcion\_llava(etapa):
    - **Funcionalidad:** Función principal del módulo. Orquesta el proceso de captura y extracción de texto.
    - **Detalles:** Llama a las funciones de captura y extracción, y guarda los resultados en archivos con nombres que indican la etapa (inicio o final). Esto ayuda a organizar el contexto visual en el proceso de interacción.




**Conclusión del Proyecto VozAssistant**

El proyecto **VozAssistant**, desarrollado por el equipo NDR-DevOPs-Core para el Hackday, representa una solución integral y modular para la creación de un asistente virtual capaz de interactuar con el usuario y su entorno digital. Su arquitectura se destaca por la división de responsabilidades en cuatro módulos principales, lo que facilita la escalabilidad, el mantenimiento y la comprensión de su funcionamiento.

La integración de tecnologías de punta, como **Selenium** para la automatización web, el servicio de **Azure Cognitive Services** para la síntesis de voz, un **modelo de lenguaje local (Ollama)** para el procesamiento de consultas, y **PyTesseract** para la visión artificial, demuestra una sólida capacidad técnica para construir un sistema completo y funcional.

El flujo de trabajo es robusto y bien definido:

1. El módulo de **Visión** (modulo\_vision) actúa como el "ojo" del asistente, capturando la pantalla y extrayendo el texto relevante.
1. Esta información visual se une a la transcripción de la voz del usuario para crear un contexto enriquecido.
1. El módulo de **Procesamiento** (modulo\_procesamiento) toma este contexto y lo envía a un modelo de lenguaje local, que actúa como el "cerebro" para generar una respuesta coherente.
1. Si la respuesta es una instrucción que requiere una acción en la web, el módulo de **Acciones** (modulo\_acciones) entra en juego, utilizando el navegador para ejecutar la tarea solicitada.
1. Finalmente, la respuesta generada por el LLM se convierte en voz a través del módulo de **Audio** (modulo\_audio), permitiendo que el asistente se comunique de forma natural con el usuario.

En resumen, **VozAssistant** no es solo un conjunto de scripts, sino un sistema cohesivo que fusiona la voz, la visión y el lenguaje natural para ofrecer una experiencia de usuario interactiva y poderosa. El diseño modular del proyecto permite que cada componente evolucione de manera independiente, abriendo el camino para futuras mejoras, como la integración de nuevos modelos de lenguaje, la adición de más plataformas de automatización o la mejora del reconocimiento visual.

