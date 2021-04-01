[![MIT License](https://img.shields.io/github/license/LombardiDaniel/Sebotiao.svg?style=for-the-badge&logo=LibreOffice&logoColor=white)](LICENSE.md)
[![Build](https://img.shields.io/github/workflow/status/LombardiDaniel/Sebotiao/Builds%20bot%20update/master?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/LombardiDaniel/Sebotiao/actions)
[![tag](https://img.shields.io/github/v/release/LombardiDaniel/Sebotiao?style=for-the-badge)](https://github.com/LombardiDaniel/Sebotiao/releases)

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
        -   [Variáveis de Ambiente](#variáveis-de-ambiente)
        -   [Chaves de Acesso](#chaves-de-acesso)
        -   [Logs](#logs)
        -   [Comandos](#comandos)
-   [License](#license)

### Sobre o Projeto

Sebotiao é um AutoMod para seu servidor do [Discord](https://discord.com) que lembra o tiozão do zap. Ele possui funcionalidades básicas (por em quanto) e é bem simples de configurar. Para adicioná-lo ao seu servidor, basta clicar [aqui](https://discord.com/api/oauth2/authorize?client_id=795344842305175593&permissions=8&scope=bot).

Mas se você está aqui, imagino que tenha vindo para adicionar funcionalidades à ele. Nesse caso, continue lendo o documento.

#### Feito com

Feito com [discord.py](https://discordpy.readthedocs.io/en/latest/), [sqlalchemy](https://www.sqlalchemy.org). Servido à você por [Docker](https://www.docker.com).

### Desenvolvendo

Aqui você verá as ferramentas necessárias para o desenvolvimento do Sebotiao.

#### Pré-requisitos

Pessoalmente, recomendo que utilize docker. Nesse caso, utilize o [docker-compose.development.yml](https://github.com/LombardiDaniel/Sebotiao/blob/master/docker-compose.development.yml). Ele criará uma database [SQLite](https://www.sqlite.org/index.html) local, ao contrário de um container separado de [PostgreSQL](https://www.postgresql.org). Ela ficará salva no volume docker chamado `dev_bot_db`.

##### Utilizando Docker

-   [Docker](https://www.docker.com)
-   [Docker Compose](https://docs.docker.com/compose/)

##### Direto no Python

-   [Python 3.7](https://www.python.org)
-   [Virtual Env](https://pypi.org/project/virtualenv/)
-   Bibliotecas estão em [requirements.txt](https://github.com/LombardiDaniel/Sebotiao/blob/master/requirements.txt)

### Organização do Projeto

De forma geral, o arquivo `src/run.py` roda o bot, utilizando os arquivos da pasta `cog` (leia mais sobre cogs [aqui](https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html)). As interações com a database são feitas pelo arquivo `src/utils/dbManager.py`, que simplifica o acesso utilizando a biblioteca sqlalchemy. Os modelos para criação das tabelas ficam no arquivo `src/models.py`.

#### Variáveis de Ambiente

As variáveis de ambiente que o container bot precisa são:

| Nome da Variável | Significado                                                                                                                                                |     Obrigatória    |
| :--------------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------: |
|     BOT_TOKEN    | Token do bot (disponibilizado pelo discord)                                                                                                                |         Sim        |
|      DB_HOST     | IP (ou nome do container) da localidade da database                                                                                                        | Não (default=`db`) |
|       DEBUG      | Se `1`, a database será SQLite no próprio diretório (único container docker); se `0`, é necessário um segundo container, contendo uma database PostgreSQL. |  Não (default=`0`) |

As variáveis de ambiente que o container da database precisa são:

|  Nome da Variável | Significado                                                               | Obrigatória |
| :---------------: | ------------------------------------------------------------------------- | :---------: |
|    POSTGRES_DB    | Nome da database para ser criada                                          |     Sim     |
|   POSTGRES_USER   | Nome do usuário para ser criado (terá privilégios máximos em POSTGRES_DB) |     Sim     |
| POSTGRES_PASSWORD | Senha para o acesso do usuário POSTGRES_USER                              |     Sim     |
|   POSTGRES_PORT   | Porta em que a database será hosteada                                     |     Sim     |

#### Chaves de Acesso

As chaves de acesso para database e o token do bot do discord devem ser providenciados (gerados) por você.

Crie um bot [por aqui](https://discord.com/developers/applications/) e lembre-se de permitir acesso de administrador e habilitar [intents](https://discordpy.readthedocs.io/en/latest/intents.html).

#### Logs

Para logs, você deve utilizar a classe `DockerLogger`, declarada no arquivo [src/utils/docker.py](src/utils/docker.py). Ela salva arquivos `.log` nos `host volumes` do docker, ou seja, é criada uma pasta `logs/` no diretório do projeto para que sejam salvos lá. E também imprime todos os logs no stdout, para facilitar o acesso por meios como `docker logs` e [portainer.io](https://www.portainer.io).

Os arquivos `.log` são separados de acordo com o `prefix` especificados na inicialização do objeto. Este `prefix` também é usado para marcar no stdout. Formato dos logs:

```py
# Nos arquivos .log
f"{self.lvl_str}; {str(datetime.now())[:-3]}; {msg};\n"

# No stdout
f"{lvl.upper()}; {str(datetime.now())[:-3]}; {msg};"
```

Caso esteja debugando, pode-se chamar o método estático `stdout_log`, da mesma classe. Este aceita `*args` e `**kwargs`, para auxiliar.

#### Comandos

Eu optei por não usar o manuseador default de comandos do `discordpy`, então montei um parser que pode ser encontrado no arquivo [src/extras/messages.py](src/extras/messages.py). Mas de forma resumida, basta adicionar seu comando ao arquivo [src/extras/commands.yml](src/extras/commands.yml), mantendo a lógica do arquivo e tudo deve funcionar. (A lógica é:)

```yaml
nome_do_cog:
    msg: "Descrição do cog"
    commands:
        nome_do_comando:
            aliases: "aliases do comando"
            msg: "Descrição do comando"
            args: "Argumentos do comando" 
```


### License

Este projeto está sob a Licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.
