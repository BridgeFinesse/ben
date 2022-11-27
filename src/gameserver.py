import sys
import uuid
import shelve
import asyncio
import websockets

import game
import human

import random
import TCGUtils

from nn.models import Models


MODELS = Models.load('../models')

print('models loaded')


def worker(driver):
    print('worker', driver)
    asyncio.new_event_loop().run_until_complete(driver.run())


async def handler(websocket, path):
	print(f'got websockett connection {websocket} ')
	client_ip = (websocket.remote_address)[0]   ##J3
	print(f'got path {path}')
  
    #rdeal = game.random_deal()
	if 'blah' in path:
		rdeal = TCGUtils.getdeal(path,client_ip)
	else:
		rdeal = path.replace("/", "")
		rdeal = rdeal.replace("%20", " ")
		rdeal = rdeal.replace("%7C", "|")
		rdeal = rdeal.split("|")[0:2] 
		
    
	driver = game.Driver(MODELS, human.WebsocketFactory(websocket))
	driver.set_deal(*rdeal)
	driver.human = [False, False, True, False]


	try:
		await driver.run()

		with shelve.open('gamedb') as db:
			deal_bots = driver.to_dict()
			deal_bots['client_ip']= client_ip  ##J3
			db[uuid.uuid4().hex] = deal_bots
			print('saved')
    
	except Exception as ex:
		print('Error:', ex)
		raise ex


start_server = websockets.serve(handler, "0.0.0.0", 4443)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
