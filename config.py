import configparser
config = configparser.ConfigParser()
config.read('config.ini')

SERVER_IP=config['server']['SERVER_IP']
SERVER_PORT=config['server']['SERVER_PORT']
USERNAME=config['user']['USERNAME']
PASSWORD=config['user']['PASSWORD']