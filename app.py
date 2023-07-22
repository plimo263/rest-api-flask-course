import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from db import db
from blocklist import BLOCKLIST
import models

def create_app(db_url = None):
    app = Flask(__name__)

    # Se acontecer algum erro em uma integração propagar até o App principal
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['API_TITLE'] = 'Stores Rest API' #Titulo da api
    app.config['API_VERSION'] = "v1" # Versao da API
    app.config['OPENAPI_VERSION'] = "3.0.3"
    app.config['OPENAPI_URL_PREFIX'] = "/"
    app.config['OPENAPI_SWAGGER_UI_PATH'] = "/swagger-ui"
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = '4a50d097e3dab527811617f55a74da73c5f5868aaa3c039fdb71fb7c08ea11ad91d43916e96b0b810eb940cefd88ad93694870185a471422c7ec4bd8f4956b1443b6a63fde1f5d171f68cfb7a795ca2a6add7563ca53e2c386a6e71e7ec8de8bed2b123901ab0f499dc20869a30cce6918fd4b8bea3b8be690c53e70da2d2c16'

    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_loader_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The tonek has been revoked.", "error": "token_revoked"},
            ),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "Token is not fresh.",
                    "error": "fresh_token_required"
                }
            ),
            401,
        )

    @jwt.additional_claims_loader
    def claims_loader_callback(identity):
        if identity == 1:
            return {"is_admin": True}
        else:
            return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
            {"message": "The token has exipred", "error": "token_token_expired"}
            ),
            401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required"
             }
            ), 401
        )

    # with app.app_context():
    #     db.create_all()

    # Comandos a serem executados na linha de comando para migração
    # flask db init # Inicia as configuracoes para armazenar os dados da migracao
    # flask db migrate # Identifica os modelos para tabelas, cria o banco (em nosso caso sqlite) e a tabela de controle de versão do alembic.
    # flask db upgrade # Este finalmente vai criar as tabelas do schema de migração

    # Se caso você altere alguma coluna, inclua por exemplo basta mudar no model, depois executar os comandos
    # flask db migrate # Cria a nova migração indicando as mudanças
    # flask db upgrade # Atualiza o seu banco de dados usando a ultima versão de migração encontrada.
    
    # Se desejar voltar ao modelo antigo você pode executar o downgrade, isto vai garantir a reversão das alterações estruturais que voce tenha feito no banco.
    # Então terá que acertar no código para que isto seja reproduzido.
    # flask db downgrade
    

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)


    return app
