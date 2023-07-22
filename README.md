# Curso API com Flask API

# flask_smorest

Esta lib é capaz de nos dar recursos muito uteis para se trabalhar no
desenvolvimento de APIRest. A flask_smorest pode unir o desenvolvimento da API
já com uma documentação integrada ao Swagger. Dentre os beneficios de se usa-la estão:

- Blueprint ( para modularização do código )
- Marshmallow ( para criação de schemas e validação dos dados )
- Swagger ( para documentação do código da API de forma automatizada )
- abort ( para mensagens de retorno com status_code e um retorno em JSON da mensagem.)

## Modularizando com flask-smorest

O primeiro passo para modularização é separar o codigo de rotas em arquivos. Neste curso
estamos fazendo a criação de itens e lojas então separar cada um em um modulo torna mais organizado.

Depois disto o que se resta fazer é importar a lib Blueprint do flask-smorest (não do Flask) e usar o
MethodView de flask.views para estender uma classe que vai conter os metodos de interatividade da API

```
from flask.views import MethodView
from flask_smorest import Blueprint

from db import stores

blp = Blueprint('store', __name__, description='Operations in stores')

@blp.route('/store)
class Store(MethodView):

    def get(self):
        return stores

    def post(self, store_data):
        ...
        return store_data

```

Após fazer esta modularização é importante ir até o arquivo principal (app.py) e então fazer a importação da _Api_
que faz parte do módulo do flask*smorest. Ela vai enfeitar o nosso app ( de Flask(**name**) ) nos retornando um objeto
com um metodo \_register_blueprint* para inserirmos os nossos Blueprints. Para já ter uma documentação com o Swagger
você deve passar parametros de configuração para o app por meio de _app.config_.

```
...
from flask_smorest import Api

from resources.item import blp as ItemBlueprint
from resources.stores import blp as StoreBlueprint

app = Flask(__name__)

# Se acontecer algum erro em uma integração propagar até o App principal
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['API_TITLE'] = 'Stores Rest API' #Titulo da api
app.config['API_VERSION'] = "v1" # Versao da API
app.config['OPENAPI_VERSION'] = "3.0.3" # Versão do openapi
app.config['OPENAPI_URL_PREFIX'] = "/" # Em qual url de inicio a documentação vai se manifestar
app.config['OPENAPI_SWAGGER_UI_PATH'] = "/swagger-ui" # http://localhost:5005/swagger-ui
app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'

api = Api(app)

api.register_blueprint(ItemBlueprint)
api.register_blueprint(StoreBlueprint)

```

A forma sensacional como esta documentação é disposta na tela e a simplicidade de integração assusta. Com isto a
sua APIRest já tem documentação swagger descrevendo todos os módulos, isto é uma maravilha.

### Validando dados com marshmallow

O marshmallow é uma lib usada para criar schemas e validar dados para que eles tenham a mesma estrutura que se espera receber/devolver na API.
Para usa-lo é interessante criar um arquivo que vai concentrar todos os schemas, o nome deste arquivo pode ser schemas.py. Com o
arquivo criado agora você basicamente precisa importar _fields_ e _Schema_.

```
from marshmallow import fields, Schema

class ItemSchema(Schema):
    id = fields.Str(dump_only=True)
```

Um detalhe importante é fields, ele é capaz de passar vários tipos de validadores de campos os mais comuns são:

- fields.Str (para strings)
- fields.Float (para números de ponto flutuante)
- fields.Int (para inteiros)
- fields.List (para listas de dados)
- fields.Enum (para enumeração de opções)

As opções são muitas, o ideal é ver a doc. Alguns dos argumentos que podem ser passados na instanciação de um
validador de campo são.

- dump_only (diz que este campo só será validado e retornado na resposta ao cliente)
- required ( quando marcado como True exige que este campo esteja contido tanto na entrada quanto na saida.)

Depois de criado os schemas pode-se fazer uso deles inserindo nas chamadas por meio do decorador _arguments_ do Blueprint.

```
# Exemplo 1
@blp.arguments(ItemUpdateSchema)
def put(self, item_id):
    ...

```

Só com isto já se tem um validador de campos restringindo o que será enviado pelos clientes e validando todos os dados ali passados.

Outra forma interessante é usar o decorador response para dizer quais os dados que serão retornados na resposta ao cliente.

```
# Exemplo 2
@blp.arguments(ItemUpdateSchema)
@blp.response(200, ItemSchema)
def put(self, item_data, item_id):
    ...
```

Veja que neste exemplo 2 temos a _@blp.response(200, ItemSchema)_ dizendo que o retorno será 200 e o que será retornado será o ItemSchema.
Isto vai ajudar também a API do Swagger a gerar a documentação correta sobre o que é enviado e o que é retornado.
