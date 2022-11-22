from os import path
import json

settings_file = 'settings.json'


def init():
    global debug_chat_id
    global token
    if path.exists(settings_file):
        with open(settings_file, 'r') as file:
            data = file.read()
            settings = json.loads(data)
            token = settings['token']
            debug_chat_id = settings['debug_chat_id']
    else:
        with open(settings_file, 'x') as file:
            print('First launch, enter bot token:')
            token = input()
            settings = {}
            settings['token'] = token
            print('Enter debug chat id (or user tag with @):')
            debug_chat_id = input()
            settings['debug_chat_id'] = debug_chat_id
            data = json.dumps(settings)
            file.write(data)
