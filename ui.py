from tkinter import Spinbox, Label,Tk, Button, ttk
import ccxt,os,sys,threading
import bitmex_bot

if(os.path.exists('input/apikey_real')==False):
    print("Please make config file !")
    sys.exit()
f=open('input/apikey_real','r')
lines=f.readlines()
f.close
if(len(lines)!=3):
    print('Bad config!')
    sys.exit()
    
btmx = ccxt.bitmex({
    'apiKey': lines[1][:-1],
    'secret':lines[2],
    'enableRateLimit': False,
    'options': {
        'api-expires': 60,
    },
    #to resolve clock lack of synchronisation with server
})

if lines[0].strip() == 'test':
    btmx.urls['api'] = btmx.urls['test']

def g_hotkey_process():
    window = Tk()
    window.title("Real bot control")
    window.geometry('250x200')
    
    f=open('setting','r')
    Quantity=f.readline()[:-1]
    MaxDifference=f.readline()[:-1]
    MinDifference=f.readline()
    f.close()
    
    def SaveChange():
        f=open('input/setting','w')
        f.write(QtySpin.get()+'\n')
        f.write(MaxSpin.get()+'\n')
        f.write (MinSpin.get())
        f.close()
    def MaxChange():
        if(float(MaxSpin.get())<float(MinSpin.get())+1):
            MaxSpin.delete(0, "end")
            MaxSpin.insert(0, float(MinSpin.get())+1)
        SaveChange()
    def MinChange():
        if(float(MaxSpin.get())<float(MinSpin.get())+1):
            MinSpin.delete(0, "end")
            MinSpin.insert(0, float(MaxSpin.get())-1)
        SaveChange()
        
    QtyLabel = Label(window, text="Quantity")
    QtyLabel.grid(column=0, row=0)
    QtySpin = Spinbox(window, from_=1, to=500, width=7, command=SaveChange)
    QtySpin.delete(0, "end")
    QtySpin.insert(0, Quantity)
    QtySpin.grid(column=1,row=0)
        
    MaxLabel = Label(window, text="Max difference")
    MaxLabel.grid(column=0, row=1)
    MaxSpin = Spinbox(window,increment=0.5, from_=-200, to=500, width=7, command=MaxChange)
    MaxSpin.delete(0, "end")
    MaxSpin.insert(0, MaxDifference)
    MaxSpin.grid(column=1,row=1)
    
    MinLabel = Label(window, text="Min difference")
    MinLabel.grid(column=0, row=2)
    MinSpin = Spinbox(window,increment=0.5, from_=-200, to=500, width=7, command=MinChange)
    MinSpin.delete(0, "end")
    MinSpin.insert(0, MinDifference)
    MinSpin.grid(column=1,row=2)
    
    f=open('input/leverage','r')
    USDLeverage=f.readline()[:-1]
    M20Leverage=f.readline()
    f.close()
    
    label1=Label(window,text='XBTUSD Leverage')
    label1.grid(column=0,row=3)
    USDLeverageSpin = Spinbox(window,increment=1, from_=0, to=100, width=7)
    USDLeverageSpin.delete(0, "end")
    USDLeverageSpin.insert(0, USDLeverage)
    USDLeverageSpin.grid(column=1,row=3)  
    
    M20Label=Label(window,text='XBTM20 Leverage')
    M20Label.grid(column=0,row=4)
    M20LeverageSpin = Spinbox(window,increment=1, from_=0, to=100, width=7)
    M20LeverageSpin.delete(0, "end")
    M20LeverageSpin.insert(0, M20Leverage)
    M20LeverageSpin.grid(column=1,row=4)  
     
    def USDApplyLeverage():
        params={"symbol":'XBTUSD',"leverage":USDLeverageSpin.get()}
        btmx.private_post_position_leverage(params)
        f=open('input/leverage','r')
        lines=f.readlines()
        f.close()
        lvs=USDLeverageSpin.get()+'\n'+lines[1]
        f=open('input/leverage','w')
        f.write(lvs)
        f.close()
        
    def M20ApplyLeverage():
        f=open('input/contract','r')
        contract=f.readlines()[0]
        f.close()
        params={"symbol":contract,"leverage":M20LeverageSpin.get()}
        btmx.private_post_position_leverage(params)
        f=open('input/leverage','r')
        lines=f.readlines()
        f.close()
        lvs=lines[0]+M20LeverageSpin.get()
        f=open('input/leverage','w')
        f.write(lvs)
        f.close()
        
    USDLeverageButton=Button(window,text='Apply', command=USDApplyLeverage)
    USDLeverageButton.grid(column=2,row=3)
    M20LeverageButton=Button(window,text='Apply', command=M20ApplyLeverage)
    M20LeverageButton.grid(column=2,row=4)
       
    label3=Label(window,text='Second Contract')
    label3.grid(column=0,row=5)    
    ContractCombo= ttk.Combobox(window, width = 8, state='readonly')
    ContractCombo['values'] = ('XBTH20','XBTM20')
    ContractCombo.grid(column = 1, row = 5) 
    f=open('input/contract','r')
    contract=f.readlines()[0]
    f.close()
    if(contract=='XBTM20'):
        ContractCombo.current(0)
    else:
        ContractCombo.current(1)
    
    def ContractApply():
        M20Label['text']=ContractCombo.get()+' Leverage'
        f=open('input/contract','w')
        f.write(ContractCombo.get())
        f.close()
        
    ContractButton=Button(window,text='Apply', command=ContractApply)
    ContractButton.grid(column=2,row=5)
    
    ths=[]
    def openUsd():
        Quantity=QtySpin.get()
        bitmex_bot.bitmex_post_order('XBTUSD','Buy','Market',Quantity,'')
    def openM20():
        Quantity=QtySpin.get()
        bitmex_bot.bitmex_post_order(contract,'Sell','Market',Quantity,'')
    def OpenTrade():
        f=open('input/contract','r')
        contract=f.readlines()[0]
        f.close()
        th=threading.Thread(target=openUsd)
        ths.append(th)
        th1=threading.Thread(target=openM20)
        ths.append(th1)
        th.start()
        th1.start()
        
        f=open('input/state','w')
        f.write('Opened')
        f.close()

    def closeUsd():
        Quantity=QtySpin.get()
        bitmex_bot.bitmex_post_order('XBTUSD','Sell','Market',Quantity,'') 
    def closeM20():
        Quantity=QtySpin.get()
        bitmex_bot.bitmex_post_order(contract,'Buy','Market',Quantity,'') 
    def CloseTrade():
        f=open('input/contract','r')
        contract=f.readlines()[0]
        f.close()
        th=threading.Thread(target=closeM20)
        ths.append(th)
        th1=threading.Thread(target=closeUsd)
        ths.append(th1)
        th.start()
        th1.start()  
        f=open('input/state','w')
        f.write('Closed')
        f.close()
        
    OpenButton=Button(window,text="Open",command=OpenTrade)
    OpenButton.grid(column=0,row=6)
    CloseButton=Button(window,text="Close",command=CloseTrade)
    CloseButton.grid(column=1,row=6)
    
    window.mainloop()  

def main(): 
    g_hotkey_process()
    
if __name__ == '__main__':
    main()
