[![MIT License](https://img.shields.io/github/license/LombardiDaniel/Sebotiao.svg?style=flat-square)](LICENSE.md)

<br />
<p align="center">
  <a href="https://discord.com/api/oauth2/authorize?client_id=795344842305175593&permissions=8&scope=bot">
    <img src="LOGO.png" alt="LOGO" width="200" height="200">
  </a>

  <h3 align="center">Sebotião</h3>

  <p align="center">
    O AutoMod do discord que parece aquele tiozão do zap.
    <br />
    <a target="_blank" href="https://discord.com/api/oauth2/authorize?client_id=795344842305175593&permissions=8&scope=bot"><strong>Coloque-o em seu servidor »</strong></a>
  </p>
</p>

## Tabela de Conteúdos

-   [Sobre o Projeto](#sobre-o-projeto)
    -   [Feito com](#feito-com)
-   [Desenvolvendo](#desenvolvendo)
    -   [Pré requisitos](#pré-requisitos)
    -   [Organização do Projeto](#organização-do-projeto)
-   [Roadmap](#roadmap)
-   [License](#license)

### Sobre o Projeto

Sebotiao é um AutoMod para seu servidor do [Discord](https://discord.com) que lembra o tiozão do zap. Ele possui funcionalidades básicas (por em quanto) e é bem simples de configurar. Para adicioná-lo ao seu servidor, basta clicar [aqui](https://discord.com/api/oauth2/authorize?client_id=795344842305175593&permissions=8&scope=bot).

Mas se você está aqui, imagino que tenha vindo para adicionar funcionalidades à ele. Nesse caso, continue lendo o documento.

#### Feito com

Feito com [discord.py](https://discordpy.readthedocs.io/en/latest/), [sqlalchemy](https://www.sqlalchemy.org). Servido à você por [Docker](https://www.docker.com).

### Desenvolvendo

Aqui você verá as ferramentas necessárias para o desenvolvimento do Sebotiao.

#### Pré-requisitos

Pessoalmente, recomendo que utilize docker. Nesse caso, utilize o [docker-compose.development.yml](https://github.com/LombardiDaniel/Sebotiao/blob/master/docker-compose.development.yml). Ele não criará uma database local [SQLite](https://www.sqlite.org/index.html), ao contrário de um container separado de [PostgreSQL](https://www.postgresql.org). Ela ficará salva no volume docker chamado `dev_bot_db`.

##### Utilizando Docker

-   [Docker](https://www.docker.com)
-   [Docker Compose](https://docs.docker.com/compose/)

##### Direto no Python

-   [Python 3.7](https://www.python.org)
-   [Virtual Env](https://pypi.org/project/virtualenv/)
-   Bibliotecas estão em [requirements.txt](https://github.com/LombardiDaniel/Sebotiao/blob/master/requirements.txt)

### Organização do Projeto

De forma geral, o arquivo `src/run.py` roda o bot, utilizando os arquivos da pasta `cog` (leia mais sobre cogs [aqui](https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html)). As interações com a database são feitas pelo arquivo `src/utils/dbManager.py`, que simplifica o acesso utilizando a biblioteca sqlalchemy. Os modelos para criação das tabelas ficam no arquivo `src/models.py`.

As variáveis de ambiente que o container bot precisa são:

| Nome da Variável | Significado                                                                                                                                                | Obrigatória |
| :--------------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------: |
|     BOT_TOKEN    | Token do bot (disponibilizado pelo discord)                                                                                                                |     Sim     |
|      DB_HOST     | IP (ou nome do container) da localidade da database                                                                                                        |     Sim     |
|       DEBUG      | Se `0`, a database será SQLite no próprio diretório (único container docker); se `1`, é necessário um segundo container, contendo uma database PostgreSQL. |     Não    |

As variáveis de ambiente que o container da database precisa são:

|  Nome da Variável | Significado                                                               | Obrigatória |
| :---------------: | ------------------------------------------------------------------------- | :---------: |
|    POSTGRES_DB    | Nome da database para ser criada                                          |     Sim     |
|   POSTGRES_USER   | Nome do usuário para ser criado (terá privilégios máximos em POSTGRES_DB) |     Sim     |
| POSTGRES_PASSWORD | Senha para o acesso do usuário POSTGRES_USER                              |     Sim     |
|   POSTGRES_PORT   | Porta em que a database será hosteada                                     |     Sim     |

As chaves de acesso para database e o token do bot do discord devem ser providenciados (gerados) por você.

Crie um bot [por aqui](https://discord.com/developers/applications/) e lembre-se de permitir acesso de administrador e habilitar [intents](https://discordpy.readthedocs.io/en/latest/intents.html).

### License

Este projeto está sob a Licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.
