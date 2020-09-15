from cryptofeed.callback import BookCallback
from cryptofeed import FeedHandler

from cryptofeed.exchanges import Bitmex
from cryptofeed.defines import L2_BOOK, BID, ASK
import ccxt, time, os, curses, keyboard
from datetime import datetime 
from tkinter import Spinbox, Label,Tk
import threading,sys
import rui3

f=open('setting','w')
f.write('1'+'\n')
f.write('300'+'\n')
f.write('-200')
f.close()

rows=10
width=100
first_col_width=90
first_blank_col=""
for i in range(first_col_width):
    first_blank_col+=" "

if(os.path.exists('apikey_real')==False):
    print("Please make config file !")
    sys.exit()
f=open('apikey_real','r')
lines=f.readlines()
f.close
if(len(lines)!=3):
    print('Bad config!')
    sys.exit()
    
f=open('state','w')
f.write('None')
f.close()

btmx = ccxt.bitmex({
    'apiKey': lines[1][:-1],
    'secret':lines[2],
    'enableRateLimit': True,
    #addition for compturer clock not synchronised for real API
    'options': {
        'api-expires': 60,
    },
})

if lines[0].strip() == 'test':
    btmx.urls['api'] = btmx.urls['test']

f=open('contract','r')
contract=f.readlines()[0]
f.close()
        
params={"symbol":'XBTUSD',"leverage":'0'}
# btmx.private_post_position_leverage(params)
params={"symbol":contract,"leverage":'0'}
# btmx.private_post_position_leverage(params)
f=open('leverage','w')
f.write('0'+'\n')
f.write('0')
f.close()

def n(strr,n):
    if(len(strr)<n):
        for i in range(n-len(strr)):
            strr+=(' ')
    return strr

async def xbtusd_book(feed, pair, book, timestamp, receipt_timestamp):
    global width
    # Need flip the dict, but last element is first
    Max_book=len(book[BID])-1    
    fmt2="{:11.2f}"  
    stdscr = curses.initscr() #Make a screen in terminal window
    #Title
    stdscr.addstr(0,0,'                                    XBTUSD                                        ')
    stdscr.addstr(1,0,"  [ QTY_SUM ]|   [ QTY ]   |   [ BID ]   |   [ ASK ]   |   [ QTY ]   | [ QTY_SUM ]")
    stdscr.addstr(2,0,'-------------+-------------+-------------+-------------+-------------+-------------')
    # Add Bids, Asks to table
    bid_sum=0
    ask_sum=0
    for i in range(rows):
        bid_sum+=book[BID].items()[Max_book-i][1]
        ask_sum+=book[ASK].items()[i][1]
        stdscr.addstr(i+3,0,fmt2.format(bid_sum)+' | '+\
                      fmt2.format(book[BID].items()[Max_book-i][1])+' | '+\
                      fmt2.format(book[BID].items()[Max_book-i][0])+' | '+\
                      fmt2.format(book[ASK].items()[i][0])+' | '+\
                      fmt2.format(book[ASK].items()[i][1])+' | '+\
                      fmt2.format(ask_sum))
        
    usd_bid="{:6.2f}".format(book[BID].items()[Max_book][0])
    usd_ask="{:6.2f}".format(book[ASK].items()[0][0])    
    stdscr.addstr(rows*2+8,0,n("XBTUSD Bid:"+usd_bid+" XBTUSD Ask:"+usd_ask,width))
    
    stdscr.refresh()
    bid="{:6.2f}".format(book[BID].items()[Max_book][0])
    ask="{:6.2f}".format(book[ASK].items()[0][0])
    f=open('usd','w')
    f.write(bid+"\n")
    f.write(ask)
    f.close()
    
async def xbtM20_book(feed, pair, book, timestamp, receipt_timestamp):
    f=open('contract','r')
    contract=f.readlines()[0]
    f.close()

    global width
    # Need flip the dict, but last element is first
    Max_book=len(book[BID])-1    
    fmt2="{:11.2f}"  
    stdscr = curses.initscr() #Make a screen in terminal window
    #Title
    stdscr.addstr(rows+3,0,n(' ',width))
    stdscr.addstr(rows+4,0,'                                    '+contract+'                                        ')
    stdscr.addstr(rows+5,0,"  [ QTY_SUM ]|   [ QTY ]   |   [ BID ]   |   [ ASK ]   |   [ QTY ]   | [ QTY_SUM ]")
    stdscr.addstr(rows+6,0,'------------+-------------+-------------+-------------+-------------+-------------')
    # Add Bids, Asks to table
    bid_sum=0
    ask_sum=0
    for i in range(rows):
        bid_sum+=book[BID].items()[Max_book-i][1]
        ask_sum+=book[ASK].items()[i][1]
        stdscr.addstr(i+rows+7,0,fmt2.format(bid_sum)+' | '+\
                      fmt2.format(book[BID].items()[Max_book-i][1])+' | '+\
                      fmt2.format(book[BID].items()[Max_book-i][0])+' | '+\
                      fmt2.format(book[ASK].items()[i][0])+' | '+\
                      fmt2.format(book[ASK].items()[i][1])+' | '+\
                      fmt2.format(ask_sum))
    
    f=open('usd','r')
    usd_bid=f.readline()[:-1]
    usd_ask=f.readline()
    f.close()
    
    M20_bid="{:6.2f}".format(book[BID].items()[Max_book][0])
    M20_ask="{:6.2f}".format(book[ASK].items()[0][0])

    f=open('M20','w')
    f.write(M20_bid+"\n")
    f.write(M20_ask)
    f.close()
    
    stdscr.addstr(rows*2+7,0,n(' ',width))
    stdscr.addstr(rows*2+9,0,n(contract+" Bid:"+M20_bid+" "+contract+" Ask:"+M20_ask,width))
    
    diff_open="{:6.2f}".format(float(M20_bid)-float(usd_ask))
    diff_close="{:6.2f}".format(float(M20_ask)-float(usd_bid))
    stdscr.addstr(rows*2+10,0,n("Open Difference ( XBTM20_bid - XBTUSD_ask ): "+diff_open,width))
    stdscr.addstr(rows*2+11,0,n("Close Difference ( XBTM20_ask - XBTUSD_bid ): "+diff_close,width))
    
    f=open('setting','r')
    qty=f.readline()[:-1]
    max_diff=f.readline()[:-1]
    min_diff=f.readline()
    f.close()
    stdscr.addstr(rows*2+12,0,n("Quantity:"+qty+" Max Difference:"+max_diff+" Min Difference:"+min_diff,width))
    
    f=open('state','r')
    state=f.readline()
    f.close()
    state="Current trading state: "+state+"     "
    
    cond=''
    if float(diff_open)>float(max_diff) and float(diff_close)<float(min_diff):
        stdscr.addstr(rows*2+13,0,n(state+"Open/Close condition satisfied! "+diff_open+">"+max_diff,width))
        cond='OpenClose'
    elif float(diff_open)>float(max_diff):
        stdscr.addstr(rows*2+13,0,n(state+"Open condition satisfied! "+diff_open+">"+max_diff,width))
        cond='Open'
    elif float(diff_close)<float(min_diff):
        stdscr.addstr(rows*2+13,0,n(state+"Close condition satisfied! "+diff_close+"<"+min_diff,width))
        cond='Close'
    else:
        stdscr.addstr(rows*2+13,0,n(state+"None condition satisfied!",width))
        cond='None'
    stdscr.addstr(rows*2+14,0,n(' ',width))
    stdscr.addstr(rows*2+15,0,n(' ',width))   
    stdscr.refresh()
    
    f=open('condition','w')
    f.write(cond)
    f.close()    
  
def log(data):
    with open('real_log.txt', 'a') as f:
        f.write(str(datetime.now()) + ' ' + str(data) + '\n')

def handle_timeout(e):
    sstr = 'timeout='
    pos = e.args[0].find(sstr)
    if pos > 0:
        timeout = int(e.args[0][pos + len(sstr):-1])
        time.sleep(timeout)
    else:
        time.sleep(2)
        
def bitmex_post_order(symbol,orderSide, ordType, orderQty, orderPrice):
    if ordType=="Market":
        params={"symbol":symbol,\
                "side":orderSide,\
                "orderQty":orderQty,\
                "ordType":"Market"}
    elif ordType=="Limit":
        params={"symbol":symbol,\
                "side":orderSide,\
                "orderQty":orderQty,\
                "ordType":"Limit",\
                "price":orderPrice}
    res = None
    while not res:
        try:
            res = btmx.private_post_order(params)
            log(res)
        except Exception as e:
            log(e)
            handle_timeout(e)
    return res  

def bitmex_close_pos(symbol):
    res = None
    params = {'symbol': symbol, 'execInst': 'Close'}
    while not res:
        try:
            res = btmx.private_post_order(params)
            log(res)
        except Exception as e:
            log(e)
            handle_timeout(e)    
def g_hotkey_process():
    window = Tk()
    window.title(":)")
    window.geometry('250x100')
    
    f=open('setting','r')
    Quantity=f.readline()[:-1]
    MaxDifference=f.readline()[:-1]
    MinDifference=f.readline()
    f.close()
    
    def SaveChange():
        f=open('setting','w')
        f.write(QtySpin.get()+'\n')
        f.write(MaxSpin.get()+'\n')
        f.write(MinSpin.get())
        f.close()
    
    QtyLabel = Label(window, text="Quantity")
    QtyLabel.grid(column=0, row=0)
    QtySpin = Spinbox(window, from_=1, to=2, width=7, command=SaveChange) # limited to 2 during testing
    QtySpin.delete(0, "end")
    QtySpin.insert(0, Quantity)
    QtySpin.grid(column=1,row=0)
        
    MaxLabel = Label(window, text="Max difference")
    MaxLabel.grid(column=0, row=1)
    MaxSpin = Spinbox(window, from_=-200, to=500, width=7, command=SaveChange)
    MaxSpin.delete(0, "end")
    MaxSpin.insert(0, MaxDifference)
    MaxSpin.grid(column=1,row=1)
    
    MinLabel = Label(window, text="Min difference")
    MinLabel.grid(column=0, row=2)
    MinSpin = Spinbox(window, from_=-200, to=500, width=7, command=SaveChange)
    MinSpin.delete(0, "end")
    MinSpin.insert(0, MinDifference)
    MinSpin.grid(column=1,row=2)
    
    window.mainloop()  

def trade():
    f=open('condition','r')
    cond=f.readline()
    f.close()
    
    stdscr1 = curses.initscr() 
    stdscr1.addstr(rows*2+14,0,n('',width))
    stdscr1.addstr(rows*2+15,0,n(cond+" "+str(datetime.now()),width))
    stdscr1.refresh() 
    
    f=open('setting','r')
    Quantity=f.readline()[:-1]
    f.close()
    
    f=open('state','r')
    state=f.readline()
    f.close()
    
    f=open('contract','r')
    contract=f.readlines()[0]
    f.close()

    tths=[]

    def openUsd():
        bitmex_post_order('XBTUSD','Buy','Market',Quantity,'')
    def openM20():
        bitmex_post_order(contract,'Sell','Market',Quantity,'')
    def closeUsd():
        bitmex_post_order('XBTUSD','Sell','Market',Quantity,'')
    def closeM20():
        bitmex_post_order(contract,'Buy','Market',Quantity,'')
        
    if((cond=='Open' or cond=='OpenClose') and state!='Opened'):
        th=threading.Thread(target=openUsd)
        tths.append(th)
        th1=threading.Thread(target=openM20)
        tths.append(th1)
        th.start()
        th1.start()
        f=open('state','w')
        f.write('Opened')
        f.close()
    elif((cond=='Close' or cond=='OpenClose') and state=='Opened'):
        th=threading.Thread(target=closeM20)
        tths.append(th)
        th1=threading.Thread(target=closeUsd)
        tths.append(th1)
        th.start()
        th1.start()  
        f=open('state','w')
        f.write('Closed')
        f.close()
        
    t=threading.Timer(0.1, trade)
    t.start()
    
import platform    
def main(): 
    f=open('contract','r')
    contract=f.readlines()[0]
    f.close()
    
    print("Hello XBTUSD, "+contract+" ! Orderbooks loading....") 
    
    if(platform.system()=='Windows'):
        keyboard.add_hotkey('g', rui3.g_hotkey_process)
        os.system('mode con: cols=100 lines='+str((rows+4)*2+10))
    
    ths=[]
    th=threading.Thread(target=trade)
    ths.append(th)
    th.start()
    
    f1 = FeedHandler()
    usd_handler=Bitmex(pairs=['XBTUSD'], channels=[L2_BOOK], callbacks={L2_BOOK: BookCallback(xbtusd_book)})
    f1.add_feed(usd_handler)
    
    M20_handler=Bitmex(pairs=[contract], channels=[L2_BOOK], callbacks={L2_BOOK: BookCallback(xbtM20_book)})
    f1.add_feed(M20_handler)
    f1.run()
    
if __name__ == '__main__':
    main()
    curses.endwin() #Close screen
