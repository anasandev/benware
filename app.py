"""Servidor Flask do robô educativo."""
import logging
import os
import secrets
from functools import wraps

from flask import Flask, Response, jsonify, render_template, request

import db

BASE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
logging.basicConfig(
    filename=os.path.join(BASE, "logs", "robo.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

PAIS_USUARIO = os.environ.get("PAIS_USUARIO", "pais")
PAIS_SENHA = os.environ.get("PAIS_SENHA", "trocar123")  # TROQUE em produção

app = Flask(__name__)
db.iniciar()


def so_pais(f):
    """Protege a área dos pais com senha (HTTP Basic)."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        a = request.authorization
        ok = (a and secrets.compare_digest(a.username or "", PAIS_USUARIO)
              and secrets.compare_digest(a.password or "", PAIS_SENHA))
        if not ok:
            logging.warning("Acesso negado à area dos pais ip=%s", request.remote_addr)
            return Response("Acesso restrito", 401,
                            {"WWW-Authenticate": 'Basic realm="Area dos pais"'})
        return f(*args, **kwargs)
    return wrapper


def calcular_estrelas(acertos, total):
    taxa = acertos / total if total else 0
    return 3 if taxa >= 0.9 else 2 if taxa >= 0.6 else 1


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/saude")
def saude():
    """Usado pelo script MonitorServico para saber se o jogo está no ar."""
    return jsonify(status="ok")


@app.get("/api/missao/<int:missao_id>")
def api_missao(missao_id):
    licao = db.carregar_licao(missao_id)
    if licao is None:
        return jsonify(erro="Missão não encontrada"), 404
    return jsonify(licao)


@app.post("/api/tentativa")
def api_tentativa():
    dados = request.get_json(silent=True) or {}
    nome = str(dados.get("nome", "")).strip()[:30]
    licao = db.carregar_licao(dados.get("missao_id", 0))
    respostas = dados.get("respostas")
    if not nome or licao is None or not isinstance(respostas, list):
        return jsonify(erro="Dados inválidos"), 400

    gabarito = {p["id"]: p["correta"] for p in licao["perguntas"]}
    corrigidas = []
    for r in respostas:
        pid = r.get("pergunta_id")
        if pid not in gabarito:
            return jsonify(erro="Pergunta inválida"), 400
        tempo = r.get("tempo_ms")
        corrigidas.append((pid, int(r.get("escolha") == gabarito[pid]),
                           tempo if isinstance(tempo, int) else None))

    acertos = sum(c[1] for c in corrigidas)
    pontos = acertos * 10
    estrelas = calcular_estrelas(acertos, len(gabarito))

    with db.conectar() as conn:
        conn.execute("INSERT OR IGNORE INTO criancas (nome) VALUES (?)", (nome,))
        crianca_id = conn.execute("SELECT id FROM criancas WHERE nome = ?", (nome,)).fetchone()["id"]
        cur = conn.execute(
            "INSERT INTO tentativas (crianca_id, missao_id, pontos, estrelas) VALUES (?,?,?,?)",
            (crianca_id, licao["id"], pontos, estrelas))
        conn.executemany(
            "INSERT INTO respostas (tentativa_id, pergunta_id, correta, tempo_ms) VALUES (?,?,?,?)",
            [(cur.lastrowid, *c) for c in corrigidas])
    logging.info("Tentativa salva crianca=%s missao=%s pontos=%s", nome, licao["id"], pontos)
    return jsonify(pontos=pontos, estrelas=estrelas, acertos=acertos, total=len(gabarito))


@app.get("/pais")
@so_pais
def pais():
    with db.conectar() as conn:
        linhas = conn.execute("""
            SELECT c.nome, m.titulo, t.pontos, t.estrelas, t.data_hora
            FROM tentativas t
            JOIN criancas c ON c.id = t.crianca_id
            JOIN missoes m ON m.id = t.missao_id
            ORDER BY t.data_hora DESC LIMIT 100""").fetchall()
    return render_template("pais.html", linhas=linhas)
