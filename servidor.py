"""Inicia o jogo com Waitress (mais estável no Windows que o servidor de desenvolvimento)."""
import os

from waitress import serve

from app import app

if __name__ == "__main__":
    porta = int(os.environ.get("ROBO_PORTA", "8080"))
    print(f"Robô educativo rodando na porta {porta}")
    serve(app, host="0.0.0.0", port=porta)
