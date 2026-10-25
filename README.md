# Robô educativo (Bit)

## Rodar
    pip install -r requirements.txt
    python servidor.py          # http://localhost:8080
    python backup.py            # gera backup em backups/

## Variáveis de ambiente
- PAIS_USUARIO / PAIS_SENHA : acesso à rota /pais (troque a senha padrão!)
- ROBO_PORTA : porta do serviço (padrão 8080)
- ROBO_DB    : caminho do banco (padrão dados/robo.db)

## Estrutura
- app.py        rotas Flask e regras de pontuação
- db.py         tabelas SQLite e carga das missões
- licoes/       conteúdo das missões em JSON
- backup.py     classe Backup (automação)
- logs/robo.log log do jogo (para o analisador de logs)
