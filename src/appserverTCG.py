from gevent import monkey

monkey.patch_all()

from bottle import Bottle, run, static_file, redirect, template, request

import shelve
import json
import csv
from scoring import score
from TCGUtils import MatchPoint, deal_data, BBOURL, TCGDisplay

# For Bid API
from BotNextBid import robot_bid

# from urllib import parse
# from nn.models import Models
# from bots import BotBid
# from bidding import bidding
# from util import hand_to_str
# from TCGUtils import robot_bid

app = Bottle()

DB_NAME = 'gamedb'


@app.route('/Original')
def home():
    html = '<h1><a href="/app/bridge.html">Play Now</a></h1>\n'

    html += '<ul>\n'

    with shelve.open(DB_NAME) as db:
        deal_items = sorted(list(db.items()), key=lambda x: x[1]['timestamp'], reverse=True)

        for deal_id, deal in deal_items:
            html += '<li><span><a href="/app/viz.html?deal={}">{} {}</a></span>\n'.format(deal_id, deal['contract'],
                                                                                          len(list(filter(
                                                                                              lambda x: x % 2 == 1,
                                                                                              deal['trick_winners']))))
            html += '<span><a href="/api/delete/deal/{}">delete</a></span></li>'.format(deal_id)
    html += '</ul>'
    return html


@app.route('/app/<filename>')
def frontend(filename):
    url = filename

    if '?' in filename:
        filename = filename[:filename.index('?')]
    return static_file(filename, root='./frontend')


@app.route('/api/deals/<deal_id>')
def deal_data(deal_id):
    db = shelve.open(DB_NAME)
    deal = db[deal_id]
    db.close()
    return json.dumps(deal)


@app.route('/api/delete/deal/<deal_id>')
def delete_deal(deal_id):
    db = shelve.open(DB_NAME)
    db.pop(deal_id)
    db.close()
    redirect('/home')


@app.route('/redeal/<deal>')
def re_deal(deal):
    # Use template to load Deal into redeal.tpl(aka bridge.html) skip the .js and css calls
    if 'style' in deal:
        deal = deal[deal.index('style'):]
        return static_file(deal, root='./frontend')
    elif 'bridge.js' in deal:
        deal = deal[deal.index('bridge.js'):]
        return static_file(deal, root='./frontend')
    else:
        return template('./frontend/redeal/redeal', redeal=deal)


@app.route('/home')
def ExtDisplay():
    client_ip = request.environ.get('REMOTE_ADDR')
    html = TCGDisplay(client_ip)
    return html


@app.route('/admin')
def ExtDisplay():
    client_ip = request.environ.get('REMOTE_ADDR')
    html = TCGDisplay('admin')
    return html


# Robot Next Bid API
@app.route('/api/nextbid/<seq>')
def nextbid(seq):
    mybid = robot_bid(seq)

    #coming soon

    return mybid


run(app, host='0.0.0.0', port=8080, server='gevent')
