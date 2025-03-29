import os
import subprocess

def build():
    # Define o comando para criar o executável
    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name=signit",
        "main.py"
    ]
    subprocess.run(command, check=True)

if __name__ == "__main__":
    build()
