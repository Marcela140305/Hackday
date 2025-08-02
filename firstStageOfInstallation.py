import platform
import subprocess
import sys

def install_requirements():
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def install_ollama():
    os_type = platform.system()
    try:
        if os_type == "Linux" or os_type == "Darwin":
            subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
        elif os_type == "Windows":
            subprocess.run("winget install Ollama.Ollama", shell=True, check=True)
        else:
            print(f"SO no compatible: {os_type}")
    except subprocess.CalledProcessError as e:
        print("Error instalando Ollama:", e)

if __name__ == "__main__":
    install_requirements()
    install_ollama()
