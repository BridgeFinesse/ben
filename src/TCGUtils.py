import shelve
import json
import csv
from scoring import score
import random
import game
import requests
from datetime import datetime

#for Bot Bid API
from urllib import parse
from nn.models import Models
from bots import BotBid
from bidding import bidding
from util import hand_to_str

DB_NAME = 'gamedb'
#public_ip = requests.get("http://wtfismyip.com/text").text
#if (public_ip == '2601:246:cb00:fd0:c896:89f5:17c1:843b') or (public_ip == '24.1.254.247'):  ##J3
	#public_ip ='localhost'
public_ip = requests.get("https://api.ipify.org").text
if (public_ip in ['189.176.87.30','24.1.254.247']): ##sue,jay macbooks
	public_ip = "127.0.0.1"

def deal_data(deal_id):
    db = shelve.open(DB_NAME)
    deal = db[deal_id]
    
    db.close()
    
    #print(json.dumps(deal))
    return json.dumps(deal)


def BBOURL(deal_id):

	data = deal_data(deal_id)
	data = json.loads(data)

	hands = data['hands']
	hands = hands.split(" ")[0:4]

	bbohands = []
	for hand in hands:
		string = 'S' + str(hand)
		ii = [i for i in range(len(string)) if string.startswith('.', i)]
		string = string[:ii[0]] + 'H' + string[ii[0]+1:]
		string = string[:ii[1]] + 'D' + string[ii[1]+1:]
		string = string[:ii[2]] + 'C' + string[ii[2]+1:]
	
		bbohands.append(string)

	dealer = data['dealer']
	#Transform to BBO position
	#dealer = ('1234')[dealer]
	dealer = ('3412')[dealer]


	bids = []
	for i in data['bids']:
		bids.append(i['bid'])      

	plays = []
	for i in data['play']:
		plays.append(i['card'])      


	#Sample: https://www.bridgebase.com/tools/handviewer.html?lin=pn%7CSusan%20Siegel%2CJerry%20Cohen,Barry%20Pariser%2CTed%20Fine%7Cst||md|3SAQJ8HKQ87DA7CKQ2,ST964H962D932CT73,S752HDKQJ54CAJ984,|rh||ah|Board%2017|sv|o|mb|1D|mb|2H|mb|6N|mb|p|mb|p|mb|p|pc|ST|pc|S2|pc|SK|pc|SA|pc|HQ|pc|H2|pc|S5|pc|HA|pc|S3|pc|SJ|pc|S4|pc|S7|pc|CK|pc|C3|pc|C4|pc|C5|pc|CQ|pc|C7|pc|C8|pc|C6|pc|C2|pc|CT|pc|CA|pc|H3|pc|CJ|pc|H4|pc|H7|pc|H6|pc|C9|pc|H5|pc|H8|pc|H9|pc|D4|pc|D6|pc|DA|pc|D2|pc|HK|pc|D3|pc|D5|pc|HT|mc|12|

	#BBO Vulnerability codes: o =none,b = both ,n= n/s ,e = e/w
	url = 'https://www.bridgebase.com/tools/handviewer.html?lin=pn%7CYou%20Are%20Here%2CWest%20Robot,North%20Robot%2CEast%20Robot%7Cst||md|{}'.format(dealer)
	url += '{},{},{},|'.format(bbohands[2],bbohands[3],bbohands[0])
	
	if data['vuln_ns'] == False and  data['vuln_ew'] == False:
  		vul = 'o'
	elif data['vuln_ns'] == True and  data['vuln_ew'] == True:
  		vul ='b'
	elif data['vuln_ns'] == True and  data['vuln_ew'] == False:
		vul ='n'
	elif data['vuln_ns'] == False and  data['vuln_ew'] == True:
		vul ='e'
	
	url += 'rh||ah|Board%201|sv|{}|'.format(vul)
	
	for bid in bids:
		url +='mb|{}|'.format(bid)
	for play in plays:
		url +='pc|{}|'.format(play)

	

	return url
	
#print(BBOURL('6b87d95a9dd844e7ba3a6b21e628ed2d'))

def MatchPoint(date1,board1,score1):

	#extract columns from Index.pbn
	filename = open('./Dropbox/Index.pbn', 'r')
	file = csv.DictReader(filename)

	hands = []
	board = []
	date = []
	dist = []
	for col in file:
		hands.append(col['hands'])
		board.append(col['Board'])
		date.append(col['Date'])
		dist.append(col['Dist'])
	
	
	for i, (d, b) in enumerate (zip(date,board)):

		if d== date1 and b== board1  : break

	hdist = dist[i].split('||')

	
	mp = -99
	
	for dist in hdist:
		
		sdist = dist.split('|')
	
		if sdist[0] == str(score1):
			mp = sdist[3]

	return mp
	
#print(MatchPoint('2022-09-05' , '2' , '650'))



def TCGDisplay(client_ip):

	#extract columns from Index.pbn
	filename = open('./Dropbox/Index.pbn', 'r')
	file = csv.DictReader(filename)

	hands = []
	board = []
	date = []
	for col in file:
		hands.append(col['hands'])
		board.append(col['Board'])
		date.append(col['Date'])


	with shelve.open(DB_NAME) as db:
	
		deal_items = sorted(list(db.items()), key=lambda x: x[1]['timestamp'], reverse=True)



		html = '<html>\n'
		html += '<h1><a href="/app/bridge.html">Play Now</a></h1>\n'
		
		html +='<table>\n'
		html += ' <tr><th>TimeStamp - CT</th><th>Hand</th><th>Your Score</th><th><font title="The Common Game Field">MP %(TCG)</font></th><th>Expert Analysis&nbsp;</th><th>Robot Rebid</th><th>BBO Replay</th><th>Delete</th><th>Client_IP</th></tr>'


		for deal_id, deal in deal_items:
		
			if 'client_ip'in deal:
				if (deal['client_ip'] != client_ip) and (client_ip != 'admin') :
					continue
			
			
			html += '<tr>'
			tricks = len(list(filter(lambda x: x % 2 == 1, deal['trick_winners'])))
			dealcontract = deal['contract']
			dealer = ('NESW')[deal['dealer']]
			
			if deal['vuln_ns'] == False and  deal['vuln_ew'] == False:
				dealvul = 'None'
			elif deal['vuln_ns'] == True and  deal['vuln_ew'] == True:
  				dealvul ='Both'
			elif deal['vuln_ns'] == True and  deal['vuln_ew'] == False:
				dealvul ='N-S'
			elif deal['vuln_ns'] == False and  deal['vuln_ew'] == True:
				dealvul ='E-W'
			
			
			vul = False
			if (' ' + str(dealcontract))[-1] in 'EW' and deal['vuln_ew'] == True:
				vul= True				
			if (' ' + str(dealcontract))[-1] in 'NS' and deal['vuln_ns'] == True:
				vul= True
				
			
			if dealcontract != None:
				finalscore = score(dealcontract, vul , tricks)
				if dealcontract[-1] in 'EW':
					finalscore = -1 * finalscore
			else:
				finalscore = 0
				
			
			#Generate TimeStamp Field
			ts = datetime.fromtimestamp(int(deal['timestamp'])).strftime('%Y-%m-%d %H:%M')
			html += '<td>{}</td>'.format(ts)
			
			#Generate AI Robot Hand Analytics
			html += '<td>&nbsp;&nbsp;&nbsp;<a href="/app/viz.html?deal={}">{} {}</a></td>'.format(deal_id, deal['contract'], tricks)
			
			#Display Duplicate Score Field
			html += '<td>{}</td>'.format(finalscore)
			
			#Display TCG %MP
			
			try:
				i = hands.index(deal['hands'])
				#mp = MatchPoint("2022-07-04","1",-50)			
				mp = MatchPoint(date[i],board[i],finalscore)
				#print(date[i],board[i],finalscore,mp)
				html += '<td>{}</td>'.format(mp)
			except ValueError:
				html += '<td>&nbsp;</td>'
			
			
			#Generate TCG Analysis links			
			try:
				i = hands.index(deal['hands'])
				html += '<td>&nbsp;&nbsp;&nbsp;<a href="https://tcgcloud.bridgefinesse.com/PHPPOSTCGS.php?options=LookupClioBoard&date={}&board={}&gamemode=">TCG analysis</a></td>' . format(date[i],board[i])
			except ValueError:
				html += '<td>&nbsp;</td>'
			
			#Generate Robot Rebid link
			#http://34.195.157.55:8080/redeal/Q653.K985.964.T8 A.AJ2.AJ75.AQJ64 T98742.74.QT.K92 KJ.QT63.K832.753|N Both
			#html += '<td>&nbsp;&nbsp;&nbsp;<a href="http://34.195.157.55:8080/redeal/{}|{} {}">Rebid</a></td>'.format((deal['hands']),dealer,dealvul)
			
			
			html += '<td>&nbsp;&nbsp;&nbsp;<a href="http://{}:8080/redeal/{}|{} {}">Rebid</a></td>'.format(public_ip,(deal['hands']),dealer,dealvul)

			
			#Generate BBO Replay link & Add Tricks Taken		
			html += '<td>&nbsp;&nbsp;&nbsp;<a href ="{}|mc|{}">Replay</a></td>'.format(BBOURL(deal_id),tricks)
			
			
			#Generate Delete link			
			html += '<td>&nbsp;&nbsp;&nbsp;<a href="/api/delete/deal/{}">Delete</a></td>'.format(deal_id)

			#Display IP for Admin
			if 'client_ip'in deal:
				if  client_ip == 'admin' :
					html += '<td>&nbsp;&nbsp;&nbsp;<a href="https://www.whois.com/whois/{}">{}</a></td>'.format(deal['client_ip'], deal['client_ip'])

			html += '</tr>\n'

			
			#csv  += '{},{},{},{}\n'.format(deal_id, deal['contract'],deal['hands'], deal['timestamp'])

	html += '</table>\n'
	html += '</html>\n'


	return html

#print(TCGDisplay())  

def getdeal(redeal,client_ip):
	print(redeal)
	
    #Pick a Common Game Hand & Ensure no replay of deals and if runout go to random
   
	#Extract hands played
	handsplayed =[] 
	client_ips = []  
	with shelve.open(DB_NAME) as db:
		deal_items = sorted(list(db.items()), key=lambda x: x[1]['timestamp'], reverse=True)

		for deal_id, deal in deal_items:
			if 'client_ip'in deal:
				if deal['client_ip'] == client_ip:
					handsplayed.append(deal['hands'])
			else:
				handsplayed.append(deal['hands'])
						
   
	#Extract Library hands from Index.pbn
	filename = open('./Dropbox/Index.pbn', 'r')
	file = csv.DictReader(filename)
	hands = []
	dealvul = []
	for col in file:
		hands.append(col['hands'])
		dealvul.append(col['DealVul'])
	
	a = set(hands)
	b = set(handsplayed)
	
	unplayedall = (a.difference(b))
	
	#if unplayedall is almost empty, revert to random hands
	if 2 > len(unplayedall):
		rdeal = game.random_deal()
		#print('Random Hand: ' , rdeal)
	else:	
		unplayed = random.choice(list(unplayedall))
		i = hands.index(unplayed)
		rdeal = (hands[i],dealvul[i])
		#print('TCG Hand:' , rdeal)
			
	#Original Code below allowed hands to replay
	# getdeal = random.choice(list(open('./Dropbox/Index.pbn'))[1:])
	# 	raw = getdeal.rstrip('\r\n')   
	# 	rdeal = raw.split(",")[0:2]    
    
	return rdeal
       
#print(getdeal())   

def robot_bid(seq) :
	
	#34.195.157.55:8080/api/nextbid/n=q842.j862.97.q93&s=aj.a93.akt632.k8&e=k.qt75.j854.a754&w=t97653.k4.q.jt62&bidding=p-p-1d-p-1h-p-2d-p-p-p-CJ-CQ
	mybid = 'Always bid 3NT'
	seqd = dict(parse.parse_qsl(seq))

	models = Models.load('../models') 

	hand = seqd['s']
	auction = ['PAD_START' , 'P', 'P', '1D']

	#test parameters
	vuln_ns = False
	vuln_ew = True
	hand = '73.KJ83.AT2.T962'
	auction = ['PAD_START', '1D', '1S']
	bot_bid = BotBid([vuln_ns, vuln_ew], hand, models)
	mybid = bot_bid.bid(['PAD_START', '1D', '1S']).bid
	
	return mybid
	
	