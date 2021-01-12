'''

Creates the formated messages to be sent on to the discord.

'''

import yaml

# from discord import Embed
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
                message += f"`{our_input}` é uma Classes de Comandos:\n"
                message += f"> {commands_dict[our_input]['msg']}\n\n"
                message += "Comandos:\n"

                # Para cada comando disponível dentro da categoria
                for key, value in commands_dict[our_input]['commands'].items():
                    message += f"> `{key}`: {value['msg']}\n"

                message += '\nEvie: `tiao ajuda COMANDO` para mais detalhes\n'

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

            message += '\nEvie: `tiao ajuda CATEGORIA` para mais detalhes\n'
        return message

    @staticmethod
    def cursed_words_msg(user_id):
        '''
        The reply when someone says a cursed word.
        '''
        return f'Aqui nois nao usa esses termo nao blz.Fas o favor <@{user_id}> obrigado .'

    # @staticmethod
    # def stream_notification(user_id, twitch_url):
    #     message = Embed(
    #         title='Ta na hora de ver uma live braba!',
    #         url=twitch_url,
    #         color=Colours.bright_green
    #     )
    #
    #     # message.add_field('')
    #
    #     message.set_footer('Venha para o pântano!')
