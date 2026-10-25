"""Backup do banco de dados (item de OOP/automação do edital)."""
import glob
import os
import sqlite3
from datetime import datetime

import db


class Backup:
    def __init__(self, origem=db.DB_PATH, destino=None, manter=7):
        self.origem = origem
        self.destino = destino or os.path.join(db.BASE, "backups")
        self.manter = manter

    def executar(self):
        os.makedirs(self.destino, exist_ok=True)
        nome = datetime.now().strftime("robo_%Y%m%d_%H%M%S.db")
        caminho = os.path.join(self.destino, nome)
        # API de backup do SQLite: copia com segurança mesmo com o jogo em uso
        with sqlite3.connect(self.origem) as src, sqlite3.connect(caminho) as dst:
            src.backup(dst)
        self._limpar_antigos()
        return caminho

    def _limpar_antigos(self):
        arquivos = sorted(glob.glob(os.path.join(self.destino, "robo_*.db")))
        for antigo in arquivos[:-self.manter]:
            os.remove(antigo)


if __name__ == "__main__":
    print("Backup criado em:", Backup().executar())
