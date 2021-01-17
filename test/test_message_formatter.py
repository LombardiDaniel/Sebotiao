import unittest

from discord import Embed

from src.extras.messages import MessageFormater


class TestMessage(unittest.TestCase):
    '''
    Tests all methods from the 'MessageFormater' module.
    '''

    def test_cursed_words_msg(self):
        '''
        Test for 'cursed_words_msg()'.
        '''

        result = MessageFormater.cursed_words_msg(1020304050)

        msg = f'Aqui nois nao usa esses termo nao blz.Fas o favor <@1020304050> obrigado .'

        # Tests result type
        self.assertIsInstance(result, str)
        # Tests result msg
        self.assertEqual(result, msg)
        # Tests required arg
        self.assertRaises(TypeError, MessageFormater.cursed_words_msg)

    def test_development(self):
        '''
        Tests type for development
        '''

        result = MessageFormater.development()

        embed_obj = embed_obj = Embed(title='title')

        # Tests result type
        self.assertIsInstance(result, type(embed_obj))


if __name__ == '__main__':
    unittest.main()
