'''
Creates the formated messages to be sent on to the discord.
'''

from datetime import datetime

import requests
import yaml

from discord import Embed

from extras import constants

class MessageFormater:
    '''
    Formats messages before sending (e.g. Embeds, links, tags etc).
    '''

    @staticmethod
    def ajuda(our_input=None):
        '''
        Custom made help command.

        Args:
            - our_input (str): key used to search the dictionary of available functions.
        Returns:
            None.
        '''

        # Path relativo ao arquivo `run.py`, localizado no diretório `src`
        with open('./extras/commands.yml', 'r') as file:
            commands_dict = yaml.load(file, Loader=yaml.FullLoader)

        # Se foi passado algum comando
        if our_input is not None:
            our_input = our_input.lower()

            # Tenta achar no nivel superior, se não encontrar, vai para o próx. camada
            try:
                message = ''
                message += f"`{our_input}` é uma Classe de Comandos:\n"
                message += f"> {commands_dict[our_input]['msg']}\n\n"
                message += "Comandos:\n"

                # Para cada comando disponível dentro da categoria
                for key, value in commands_dict[our_input]['commands'].items():
                    message += f"> `{key}`: {value['msg']}\n"

                message += '\nEnvie: `tiao ajuda COMANDO` para mais detalhes\n'

            # O argumento passado é um comando, não uma categoria
            except KeyError:
                message = ''
                # Procura o comando em todas as categorias
                for name, module in commands_dict.items():
                    for key, value in module['commands'].items():
                        # Se o comando for um dos declarados OU um alias dele
                        if our_input == key or our_input in value['aliases'].split(','):
                            message += f"Categoria: `{name}`\n\n"
                            message += "Comando:\n"
                            message += f"> `{key}`: {value['msg']}\n\n"
                            message += f">\t- Arguments: {value['args']}\n"

                            aliases = ''
                            for alias in value['aliases'].split(','):
                                aliases += f'`{alias}` '

                            message += f">\t- Aliases: {aliases}\n"
                            break

        else:
            message = 'Categorias disponíveis:\n'
            for name, module in commands_dict.items():
                message += f"> `{name}`: {module['msg']}\n"

            message += '\nEnvie `tiao ajuda CATEGORIA` para mais detalhes\n'

        message += "\n> Obs: Lembre de utilizar `tiao ` antes de qualquer comando.\n"

        return message

    @staticmethod
    def home_channel_message(title, description):
        '''
        '''

        embed_obj = Embed(title=title,
                          description=description,
                          color=constants.Colours.purple)

        embed_obj.add_field(name="Para ter acesso ao server",
                            value="Adicione uma reação à este post.")

        embed_obj.set_footer(text="Este server é moderado pelo Sebotião")

        return embed_obj

    @staticmethod
    def cursed_words_msg(user_id):
        '''
        The reply when someone says a cursed word.
        '''
        return f'Aqui nois nao usa esses termo nao blz.Fas o favor <@{user_id}> obrigado .'

    @staticmethod
    def development():
        '''
        Uses the request to check for info about the current git version.

        Args:
            None.
        Returns:
            - info (Embed obj.): Embed containing the info about current development
                state of Sebotiao.
        '''

        url = "https://api.github.com/repos/LombardiDaniel/Sebotiao"

        request = requests.get(url).json()

        embed_obj = Embed(
            title=request['name'],
            url=request['html_url'],
            description=request['description'],
            color=constants.Colours.bright_green)

        embed_obj.set_thumbnail(
            url="https://raw.githubusercontent.com/LombardiDaniel/Sebotiao/master/LOGO.png")

        lst_contributors = requests.get(url + '/contributors').json()
        embed_obj.add_field(
            name='Principais colaboradores:',
            value=", ".join([contributor['login'] for contributor in lst_contributors[0:4]]),
            inline=True)

        date_time_obj = datetime.strptime(request['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        delta = datetime.now() - date_time_obj

        msg = f"{delta.seconds//3600} horas atrás" if delta.days < 1 else f"{delta.days} dias atrás"

        embed_obj.add_field(
            name='Último Update:',
            value=msg,
            inline=True)

        releases = requests.get(url + '/releases').json()[0]
        embed_obj.set_footer(text=f"{releases['tag_name']}")

        return embed_obj
