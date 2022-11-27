<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">

  <title>Bridge</title>

  <link rel="stylesheet" href="style.css">
  <script type="text/javascript" src="bridge.js"></script>

</head>

<body> 

    <div id="container">
        <div id="north" class="grid-item">
            <!-- <div class="card" data-value="A">&spades;</div>
            <div class="card" data-value="T">&spades;</div>
            <div class="card" data-value="7">&spades;</div>
            <div class="card red" data-value="K">&hearts;</div>
            <div class="card red" data-value="Q">&hearts;</div>
            <div class="card red" data-value="J">&hearts;</div>
            <div class="card red" data-value="3">&hearts;</div>
            <div class="card red" data-value="2">&hearts;</div>
            <div class="card" data-value="9">&clubs;</div>
            <div class="card red" data-value="Q">&diams;</div>
            <div class="card red" data-value="T">&diams;</div>
            <div class="card red" data-value="9">&diams;</div>
            <div class="card red" data-value="4">&diams;</div> -->
            
            <div id="bidding-box">
                <div id="bidding-levels">
                    <div class="invalid">1</div>
                    <div>2</div>
                    <div>3</div>
                    <div class="selected">4</div>
                    <div>5</div>
                    <div>6</div>
                    <div>7</div>
                </div>
                <div id="bidding-suits" class="hidden">
                    <div>&clubs;</div>
                    <div class="red">&diams;</div>
                    <div class="red">&hearts;</div>
                    <div>&spades;</div>
                    <div>NT</div>
                </div>
                <div id="bidding-calls">
                    <div class="pass">PASS</div>
                    <div class="double">X</div>
                    <div class="redouble invalid">XX</div>
                </div>
            </div>
        </div>
        <div id="west" class="grid-item"></div>
        <div id="table" class="grid-item">
            <div id="table-container">
                <div class="table-grid-item label-north">
                    <span class="seat-label">N</span>
                </div>
                <div class="table-grid-item label-west">
                    <div class="seat-label">W</div>
                </div>
                <div class="table-grid-item trick-west">
                    <!-- <div class="card" data-value="A">&spades;</div> -->
                </div>
                <div class="table-grid-item trick-north">
                    <!-- <div class="card red" data-value="K">&hearts;</div> -->
                </div>
                <div class="table-grid-item trick-east">
                    <!-- <div class="card" data-value="9">&clubs;</div> -->
                </div>
                <div class="table-grid-item label-east">
                    <div class="seat-label">E</div>
                </div>
                <div class="table-grid-item trick-south">
                    <!-- <div class="card red" data-value="T">&diams;</div> -->
                </div>
                <div class="table-grid-item label-south">
                    <div class="seat-label">S</div>
                </div>
            </div>
        </div>
        <div id="east" class="grid-item"></div>
        <div id="south" class="grid-item">
            <!-- <div class="card" data-value="A">&spades;</div>
            <div class="card" data-value="T">&spades;</div>
            <div class="card" data-value="7">&spades;</div>
            <div class="card red" data-value="K">&hearts;</div>
            <div class="card red" data-value="Q">&hearts;</div>
            <div class="card red" data-value="J">&hearts;</div>
            <div class="card red" data-value="3">&hearts;</div>
            <div class="card red" data-value="2">&hearts;</div>
            <div class="card" data-value="9">&clubs;</div>
            <div class="card red" data-value="Q">&diams;</div>
            <div class="card red" data-value="T">&diams;</div>
            <div class="card red" data-value="9">&diams;</div>
            <div class="card red" data-value="4">&diams;</div> -->
        </div>
        
    </div>

    <div><a href="/home">Home</a></div>

    <div id="auctionstr"></div>


    <script type="text/javascript">
        console.log('starting')

        var ws = new WebSocket("ws://" + location.hostname + ":4443/{{redeal}}")
		
        var deal = undefined

        function getTrickCardSlots() {
            return [
                document.querySelector('.trick-north'),
                document.querySelector('.trick-east'),
                document.querySelector('.trick-south'),
                document.querySelector('.trick-west')
            ]
        }

        function setTurn(playerTurn) {
            let labels = ['.label-north', '.label-east', '.label-south', '.label-west']
            labels.forEach(l => document.querySelector(l + ' .seat-label').classList.remove("turn"))
            document.querySelector(labels[playerTurn] + ' .seat-label').classList.add("turn")
        }

        function cardClick(event) {
            console.log('card click')
            if (deal.expectCardInput) {
                let card = new Card(event.target.getAttribute('symbol'))

                if (deal.turn == 2) {
                    if (deal.hand.isPlayable(card, deal.currentTrick)) {
                        ws.send(card.symbol)
                        deal.expectCardInput = false
                    }
                } else if (deal.turn == 0) {
                    if (deal.public.isPlayable(card, deal.currentTrick)) {
                        ws.send(card.symbol)
                        deal.expectCardInput = false
                    }
                }
            }
        }

        function biddingLevelClick(event) {
            if (!deal.expectBidInput || event.target.classList.contains("invalid")) {
                return
            }
            document.querySelectorAll('#bidding-levels div').forEach(el => el.classList.remove("selected"))
            document.querySelectorAll('#bidding-suits div').forEach(el => el.classList.remove("invalid"))
            event.target.classList.add("selected")

            let level = parseInt(event.target.textContent)
            let auction = new Auction(deal.dealer, deal.vuln, deal.auction)
            let minBiddableSuit = auction.getMinBiddableSuitForLevel(level)

            console.log(auction.bids)
            console.log(minBiddableSuit)

            document.querySelector('#bidding-suits').classList.remove("hidden")

            let bidSuitClasses = ['.bid-clubs', '.bid-diamonds', '.bid-hearts', '.bid-spades', '.bid-nt']

            for (var i = 0; i < minBiddableSuit; i++) {
                document.querySelector(bidSuitClasses[i]).classList.add("invalid")
            }

            
        }

        function callClick(event) {
            if (!deal.expectBidInput || event.target.classList.contains("invalid")) {
                return
            }
            ws.send(event.target.textContent)
            deal.expectBidInput = false
        }

        function bidSuitClick(event) {
            if (!deal.expectBidInput || event.target.classList.contains("invalid")) {
                return
            }

            let level = document.querySelector('#bidding-levels .selected').textContent
            let bid = level + event.target.getAttribute("symbol")
            console.log(bid)

            ws.send(bid)

            deal.expectBidInput = false
        }

        document.querySelector('body').addEventListener('click', function() {
            console.log('click')
            if (deal.expectTrickConfirm) {
                getTrickCardSlots().forEach(el => el.textContent = "")
                ws.send('y')
                deal.expectTrickConfirm = false
            }
        })

        ws.onerror = function(event) {
            document.querySelector('#auctionstr').textContent = '[ERROR] ' + JSON.stringify(event)
        }

        ws.onclose = function(event) {
            document.querySelector('#auctionstr').textContent = '[CLOSED] ' + JSON.stringify(event)
        }

        ws.onmessage = function (event) {
            console.log('received message')
            console.log(event.data)

            let data = JSON.parse(event.data)

            if (data.message == "deal_start") {
                deal = new Deal(data.dealer, data.vuln, parseHand(data.hand))

                let dealerLabel = ['.label-north', '.label-east', '.label-south', '.label-west'][deal.dealer]

                document.querySelector(dealerLabel + ' .seat-label').classList.add("dealer")
                if (deal.vuln[0]) {
                    document.querySelector('.label-north .seat-label').classList.add("red")
                    document.querySelector('.label-south .seat-label').classList.add("red")
                }
                if (deal.vuln[1]) {
                    document.querySelector('.label-west .seat-label').classList.add("red")
                    document.querySelector('.label-east .seat-label').classList.add("red")
                }

                setTurn(deal.dealer)

                deal.hand.render(document.querySelector('#south'))
                deal.renderAuction(document.querySelector('#east'))
                deal.renderBiddingBox(document.querySelector('#north'))
            } else if (data.message == "bid_made") {
                deal.auction = data.auction
                deal.renderAuction(document.querySelector('#east'))
                deal.turn = (deal.turn + 1) % 4
            } else if (data.message == "get_bid_input") {
                deal.auction = data.auction
                deal.canDouble = data.can_double
                deal.canRedouble = data.can_redouble
                deal.expectBidInput = true
                deal.renderBiddingBox(document.querySelector('#north'))

                document.querySelectorAll('#bidding-calls div').forEach(el =>
                    el.addEventListener("click", callClick))
                document.querySelectorAll('#bidding-levels div').forEach(el =>
                    el.addEventListener("click", biddingLevelClick))
                document.querySelectorAll('#bidding-suits div').forEach(el =>
                    el.addEventListener("click", bidSuitClick))
            } else if (data.message == "auction_end") {
                deal.auction = data.auction
                deal.declarer = data.declarer
                deal.strain = data.strain
                deal.dummy = (deal.declarer + 2) % 4
                deal.turn = (data.declarer + 1) % 4
                setTurn(deal.turn)
                deal.currentTrick = new Trick(deal.turn, [])

                document.querySelector('#north').textContent = ''

                if (deal.declarer == 3) {
                    deal.renderAuction(document.querySelector('#west'))
                } else {
                    deal.renderAuction(document.querySelector('#east'))
                }

                document.querySelectorAll('.card')
                    .forEach(c => c.addEventListener('click', cardClick))
            } else if (data.message == "opening_lead") {
                let card = new Card(data.card)

                let publicHand = parseHand(data.dummy)
                deal.public = publicHand

                let dummyContainerId = ['#north', '#east', '#south', '#west'][deal.dummy]

                if (deal.dummy == 0) {
                    deal.public.render(document.querySelector(dummyContainerId))
                } else if (deal.dummy == 2) {
                    deal.public.render(document.querySelector('#north'))
                } else {
                    deal.public.renderEW(document.querySelector(dummyContainerId))
                }

                document.querySelectorAll('.card')
                    .forEach(c => c.addEventListener('click', cardClick))
            } else if (data.message == "card_played") {
                let card = new Card(data.card)
                
                deal.currentTrick.cards.push(card)
                if (data.player == 2) {
                    deal.hand = deal.hand.play(card)
                    deal.hand.render(document.querySelector('#south'))
                } else if (data.player == 0) {
                    if (deal.declarer == 0 || deal.declarer == 2) {
                        deal.public = deal.public.play(card)
                        deal.public.render(document.querySelector('#north'))
                    }
                } else if (data.player == deal.dummy) {
                    deal.public = deal.public.play(card)
                    if (deal.dummy == 1) {
                        deal.public.renderEW(document.querySelector('#east'))
                    } else if (deal.dummy == 3) {
                        deal.public.renderEW(document.querySelector('#west'))
                    }
                }
                document.querySelectorAll('.card')
                    .forEach(c => c.addEventListener('click', cardClick))
                deal.currentTrick.render(getTrickCardSlots())
                deal.turn = (data.player + 1) % 4
                setTurn(deal.turn)
            } else if (data.message == "get_card_input") {
                deal.expectCardInput = true
            } else if (data.message == "trick_confirm") {
                let trickWinner = deal.currentTrick.winner(deal.strain)
                console.log('trick won by ', trickWinner)

                deal.turn = trickWinner
                setTurn(deal.turn)
                deal.tricks.push(deal.currentTrick)
                deal.currentTrick = new Trick(trickWinner, [])

                deal.tricksCount[trickWinner % 2] += 1

                deal.renderTricks(document.querySelector('.tricks'))

                deal.expectTrickConfirm = true
            } else if (data.message == "deal_end") {
                let handsPBN = data.pbn.split(' ')
                let north = parseHand(handsPBN[0])
                let east = parseHand(handsPBN[1])
                let south = parseHand(handsPBN[2])
                let west = parseHand(handsPBN[3])

                north.render(document.querySelector('#north'))
                south.render(document.querySelector('#south'))
                east.renderEW(document.querySelector('#east'))
                west.renderEW(document.querySelector('#west'))

                deal.renderAuction(document.querySelector('#table'))
            }
        };

        /*let hand = parseHand('AT8..QJ9875432.K')
        hand.render(document.querySelector('#south'))
        hand.renderEW(document.querySelector('#west'))
        hand.renderEW(document.querySelector('#east'))*/
    </script>  

    
</body>
