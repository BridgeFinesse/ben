#for Bot Bid API
from urllib import parse
from nn.models import Models
from bots import BotBid
from bidding import bidding
from util import hand_to_str, parse_lin, display_lin
from bots import BotLead
from analysis import CardByCard

def robot_bid(seq) :
	
	#BBO API: http://34.195.157.55:8080/api/nextbid/pov="E" d="N" v="-" n="q842.j862.97.q93" s="aj.a93.akt632.k8" e="k.qt75.j854.a754" w="t97653.k4.q.jt62" h="p-p-1d-p-1h-p-2d-p-p-p
	seqd = dict(parse.parse_qsl(seq))

	models = Models.load('../models') 

	
	b = seqd['h']
	i = min(((b + '-C').index('-C')), ((b + '-D').index('-D')), ((b + '-H').index('-H')) ,((b + '-S').index('-S'))  )
	
	p = b[1+i:]
	print('play: ',p)
	b = b[:i]
	print('bids: ',b)
	
	vul = seqd['v']
	vuln_ns = False
	vuln_ew = False
	if vul == "b" or vul == 'n':
		vuln_ns = True
	elif vul == "b" or vul == 'e':
		vuln_ew = True

	
	#Skip and go to Card Play  if b ends with -p-p-p
	bidover = b[-6:] == '-p-p-p'
	print('Bid over? ' , bidover)
	
	if not bidover:
	
		
		b = b.replace("p", "pass")
		b = b.upper().split("-")
		auction = ['PAD_START']
		auction += b
	
		dealer = seqd['d']
		i = 'NESW'.index(dealer)
		pov = i + (len(b) % 4)
		#print('POV: ' , pov)
		#print('# of Bids:' , len(b))
		print('Auction: ' , auction)
		#hand = seqd[seqd['pov']]
		hand = (seqd['nesw'[pov]]).upper()
	
	
		
		#test parameters
		#vuln_ns = False
		#vuln_ew = True
		#hand = '73.KJ83.AT2.T962'
		#auction = ['PAD_START', '1D', '1S']
	
		var = [vuln_ns, vuln_ew], hand, models
		print(var)
		bot_bid = BotBid([vuln_ns, vuln_ew], hand, models)
		mybid = bot_bid.bid(auction).bid
		
		mybid = '<r type="bid" bid="{}"/>'.format(mybid)
		#mybid = bot_bid.bid(['PAD_START', '1D', '1S']).bid
		
		
	elif bidover:
		mybid = 'Bidding over... time for Lead'    
    
		print(0 < len(p))
		
		#Have to figure out who is on lead
		contract = (b.upper())[-8:-6]
		print('Contract: ' , contract)
		dealer = seqd['d']
		i = 'NESW'.index(dealer)
		print('Dealer: ', str(i))
		lastbidder = i + (len(b) % 4)
		print('Last Bidder' , str(lastbidder))
		
		declarer = 0
		b = b.replace("p", "pass")
		b = b.upper().split("-")
		auction = b
		
		for bids in b:
			
			if (bids[1:2] == (contract+' ')[1])  and ((i % 4) in (lastbidder,(2+lastbidder) % 4)):
				print(i , bids , bids[1:2] ,(contract+' ')[1])
				declarer = i
				break
			i += 1
		
		onlead = (declarer + 1) % 4
		print('On Lead: ' , onlead)
		hand = (seqd['nesw'[onlead]]).upper()
		print('On Lead Cards: ' , hand)
		
		# both vulnerable. you are sitting North as dealer and you hold
		#hand = 'J96.J43.A32.KJ42'
		# # the auction goes:
		#auction = ['PASS', '1C', '2D', '2H', '3D', '3H', 'PASS', '4H', 'PASS', 'PASS', 'PASS']
	#class BotLead:
    #def __init__(self, vuln, hand_str, models):
    
		
		#Time to Lead, No cards have been played
		if  len(p) == 0:    
    
			lead_bot = BotLead([vuln_ns, vuln_ew], hand, models)
			lead = lead_bot.lead(auction)
			mybid = '<r type="lead" card="{}"/>'.format(lead.card)
			#print('Lead s/b DA: ', lead.card)
			
		#Cards have been played, what next
		else:
			mybid = 'Middle of the Play of the Hand... coming soon'	
	
			dealer = 'S'
			vuln = [True, True]  # fist element is NS, second element is EW
 
			hands =	['AJ87632.J96.753.','K9.Q8542.T6.AJ74','QT4.A.KJ94.KQ986','5.KT73.AQ82.T532']
			auction = ['1N', 'PASS', '4H', 'PASS', '4S', 'PASS', 'PASS', 'PASS']
			#play = ['C2', 'D3', 'CA', 'C6', 'D6', 'DJ', 'DQ', 'D5', 'DA', 'D7', 'DT', 'D4', 'D8', 'H6', 'H2', 'D9', 'SQ', 'S5', 'S2', 'SK', 'H4', 'HA', 'H7', 'H9', 'S4', 'C3', 'SA', 'S9', 'S3', 'C4', 'ST', 'H3', 'CK', 'C5', 'HJ', 'C7', 'C8', 'CT', 'S6', 'CJ', 'S7', 'H8', 'C9', 'D2', 'S8', 'H5', 'CQ', 'HT', 'SJ', 'HQ', 'DK', 'HK']
			play = ['C2', 'D3', 'CA', 'C6', 'D6', 'DJ', 'DQ', 'SA']

			
			card_by_card = CardByCard(dealer, vuln, hands, auction, play, models)
			
			myplay = card_by_card.analyze_play()

	return '<r type="BestCard" card="{}"/>'.format(myplay)


	
#print('S/B 1D: ' ,robot_bid('pov=W&v=-&d=N&n=q842.j862.97.q93&s=aj.a93.akt632.k8&e=k.qt75.j854.a754&w=t97653.k4.q.jt62&h=p-p'))
#print('S/B 1H: ' ,robot_bid('pov=W&v=-&d=N&n=q842.j862.97.q93&s=aj.a93.akt632.k8&e=k.qt75.j854.a754&w=t97653.k4.q.jt62&h=p-p-1D-p'))
#print(robot_bid('pov=E&v=-&d=N&n=q842.j862.97.q93&s=aj.a93.akt632.k8&e=k.qt75.j854.a754&w=t97653.k4.q.jt62&h=p-p-1d-p-1h-p-2d-p-p-p'))
print(robot_bid('pov=E&v=-&d=N&n=q842.j862.97.q93&s=aj.a93.akt632.k8&e=k.qt75.j854.a754&w=t97653.k4.q.jt62&h=p-p-1d-p-1h-p-2d-p-p-p-CJ-CQ'))
