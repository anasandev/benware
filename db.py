"""Banco SQLite: criação das tabelas e carga das missões a partir dos JSON."""
import glob
import json
import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("ROBO_DB", os.path.join(BASE, "dados", "robo.db"))
LICOES_DIR = os.path.join(BASE, "licoes")

SCHEMA = """
CREATE TABLE IF NOT EXISTS criancas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE COLLATE NOCASE,
    avatar TEXT DEFAULT 'bit',
    criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS missoes (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    ordem INTEGER NOT NULL,
    arquivo_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tentativas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crianca_id INTEGER NOT NULL REFERENCES criancas(id),
    missao_id INTEGER NOT NULL REFERENCES missoes(id),
    pontos INTEGER NOT NULL,
    estrelas INTEGER NOT NULL,
    data_hora TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS respostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tentativa_id INTEGER NOT NULL REFERENCES tentativas(id),
    pergunta_id TEXT NOT NULL,
    correta INTEGER NOT NULL,
    tempo_ms INTEGER
);
CREATE TABLE IF NOT EXISTS medalhas_conquistadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crianca_id INTEGER NOT NULL REFERENCES criancas(id),
    codigo_medalha TEXT NOT NULL,
    data_hora TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
"""


def conectar():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def carregar_licao(missao_id):
    caminho = os.path.join(LICOES_DIR, f"missao{int(missao_id)}.json")
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def iniciar():
    """Cria as tabelas e registra cada missao*.json encontrada."""
    with conectar() as conn:
        conn.executescript(SCHEMA)
        for arq in sorted(glob.glob(os.path.join(LICOES_DIR, "missao*.json"))):
            with open(arq, encoding="utf-8") as f:
                m = json.load(f)
            conn.execute(
                "INSERT OR REPLACE INTO missoes (id, titulo, ordem, arquivo_json) VALUES (?,?,?,?)",
                (m["id"], m["titulo"], m["ordem"], os.path.basename(arq)),
            )
