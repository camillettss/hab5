import os, sys
import random, time
import base64
random.seed(time.time())
from core.Characters import *
from core.Errors import CommandError
from core.Colors import bcolors as css
from core.Shop import Shop
import json
import atexit
import socket
import threading
import urllib.request
import pickle
import select
import asyncore

try:
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    offline=False
except:
    offline=True

_sys=sys.platform.lower()

class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch().decode()


getch = _Getch()

columns=4
rows=5
STARTUPSPWANS=2

langs=['it','en']
lang='it'

usrdata=json.loads(base64.b64decode(open('data/userdata.dat').read()).decode())
try:
    srcdata=json.loads(base64.b64decode(open('data/dumped.dat').read()).decode())
except:
    srcdata=''
if not srcdata=='':#not usrdata['firstlaunch'] in ['1',1]:
    for key in srcdata.keys():
        exec(key+'='+repr(srcdata[key]))
    #del srcdata

points={
    "win":10,
    "kill":1,
}

def list_splice(target, start, delete_count=None, *items):
    if delete_count == None:
        delete_count = len(target) - start

    # store removed range in a separate list and replace with *items
    total = start + delete_count
    removed = target[start:total]
    target[start:total] = items

    return removed


def updateWorld():
    return

class Engine():
    def __init__(self, spawns=1, show_title=True):
        super().__init__()
        atexit.register(self.cleanup)
        self.robots=[Robot(columns, rows, self) for _ in range(spawns)] # spawn on startup
        self.robots.append(Level2Robot(columns, rows, self)) # add a level 2 robot
        self.selected=None #self.robots[0]
        self.commands=json.loads(open('core/cmds.json').read())['commands']
        self.gamepoints=0
        self.beforeclean=srcdata
        self.inshop=False
        self.inbshell=False
        self.shop_support=Shop(self)
        self.freecolors=[c for x,c in css.__dict__.items() if not x.startswith('__') or x=='background']
        self.notes=[]
        # - network sets
        self.outgoing=[]
        # - graphic sets
        self.showids=False
        self.showpos=False
        self.showonlytrues=False
        self.showonlyfalse=False
        # remove bots with same pos or ids
        i=0; rmvd=0
        for bot in self.robots:
            for j in range(len(self.robots)-1):
                if bot.pos==self.robots[j].pos or bot.id==self.robots[j].pos:
                    del self.robots[j]; rmvd+=1
        for _ in range(rmvd):
            self.robots.append(Robot(columns, rows, self))
        if show_title:
            self.main_menu()
    
    def cleanup(self):
        global srcdata
        print('Exiting')
        f=open('data/dumped.dat','w')
        f.write(base64.b64encode(json.dumps(self.beforeclean).encode()).decode())
        f.close()
    
    def online_start(self):
        '''start a local server'''
        self.robots=[]
        MainServer(8080)
        asyncore.loop()
        print('out')

    def online_join(self):
        # make a Player object
        me=Player(columns,rows,self)
        me.connect('127.0.0.1:8080')
        me.loop()
        return
    
    def pickColor(self):
        return list_splice(self.freecolors, 0, 1)
    
    def online_run(self, p1, p2):
        while True:
            pass

    def run(self):
        while True:
            while self.inshop:
                try:
                    self.shop(globals()['srcdata']['score'])
                except IndexError:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Missing a parameter')
                except Exception as e:
                    print(css.FAIL+'[ERR]'+css.ENDC,str(e))
            while self.inbshell:
                try:
                    self.selected.BShell(input(css.OKCYAN+'[CMD]'+css.ENDC+css.OKGREEN+'[BSH]'+css.ENDC+' >> '))
                except IndexError:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Missing a parameter.')
                except Exception as e:
                    print(css.FAIL+'[ERR]'+css.ENDC,str(e))
            #sys.stdout.flush()
            #os.system('cls')
            if not len(self.robots): self.win()
            if not self.selected:
                self.mktable()
                # execute an engine command
                try:
                    self.parser(input(css.OKGREEN+'[CMD]'+css.ENDC+css.OKCYAN+'[MAIN]'+css.ENDC+'>> '))
                except IndexError:
                    pass
                except NotImplementedError:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Bot level is too low to perform this task.')
                except Exception as e:
                    print(e)
            else:
                try:
                    self.selected.parser(input(css.OKGREEN+'[CMD]'+css.ENDC+css.OKCYAN+'[BOT]'+css.ENDC+' -state:{}- >> '.format(self.selected.state)))
                except Exception as e:
                    print(e)

    def parser(self, x):
        global srcdata
        cmd=x.split()[0].lower()
        params=x.split()[1:]
        if '-h' in params or '--help' in params:
            self.docs(cmd); return
        if not cmd in self.commands and not cmd in self.shop_support.tools: raise CommandError(cmd)
        if not cmd in self.commands and cmd in self.shop_support.tools['0' if not self.selected else '1']: print(css.OKCYAN+'[SHOP]'+css.ENDC+css.FAIL+'[ERR]'+css.ENDC+' Per usare questo comando devi prima comprarlo.'); return
        if cmd=='select':
            try:
                if '-m' in params:
                    m=params[params.index('-m')+1]
                elif '--method' in params:
                    m=params[params.index('--method')+1]
                else:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Missing -m parameter.'); return
                if m=='id':
                    for bot in self.robots:
                        if bot.id==str(params[params.index(m)+1]):
                            self.selected=bot; return
                    print(css.FAIL+'[ERR]'+css.ENDC+' Invalid ID.')
                elif m=='pos':
                    for bot in self.robots:
                        botpos=str(bot.pos[0])+','+str(bot.pos[1])
                        if botpos==str(params[-1]):
                            self.selected=bot; return
                    print(css.FAIL+'[ERR]'+css.ENDC+' Invalid pos.')
                else:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Invalid value for -m.'); return
            except IndexError as e:
                print(css.FAIL+'[ERR]'+css.ENDC+' Missing some parameters, type "select -h" for help!')
            except Exception as e:
                print(css.FAIL+'[ERR]'+css.ENDC,e)
        elif cmd=='help':
            print(css.HEADER+'[H]'+css.ENDC+' List of commands:'); [print('-',_cmd) for _cmd in self.commands]
            print(css.HEADER+'[H]'+css.ENDC+' Type "cmd -h" for info about cmd.')
        elif cmd=='reset':
            if not len(params):
                print(css.FAIL+'[ERR]'+css.ENDC+' Invalid syntax, check "reset -h"'); return
            if '-w' in params:
                w=params[params.index('-w')+1]
            else:
                w=params[0]
            if w=='*':
                srcdata={'usrname':input('[>] New user name: '), 'score':0}
                self.commands=[
                    "select",
                    "show",
                    "notes",
                    "help",
                    "bye",
                    "reset",
                    "shop"
                ]
            elif w=='usrname':
                srcdata.update({'usrname':input('[>] New user name: ')})
            elif w=='score':
                srcdata.update({'score':0})
            else:
                print(css.FAIL+'[ERR]'+css.ENDC+' Invalid key:',w)
            self.dump()
            print(css.OKCYAN+'[OK]'+css.ENDC+' Done.')
        elif cmd=='bye':
            print('[?] Are you sure?')
            c=getch()
            if c in ['y','s']:
                # accredita
                globals()['srcdata']['score']+=self.gamepoints
                self.main_menu()
            elif c=='n':
                return
            else:
                print(css.FAIL+'[ERR]'+css.ENDC+' Unrecognized key, back to game.')
        elif cmd=='show':
            if params[0]=='notes':
                for note in self.notes:
                    print(css.WARNING+'[NOTE]'+css.ENDC,note)
                return
            try:
                if params[0] in ['id', 'ids']:
                    self.showids=True
                    if self.showpos==True: self.showpos=False
                elif params[0]=='pos':
                    self.showpos=True
                    if self.showids==True: self.showids=False
                elif params[0]=='null':
                    self.showids=False; self.showpos=False
                else:
                    raise CommandError()
            except IndexError:
                print(css.FAIL+'[ERR]'+css.ENDC+' Missing a parameter. check "show -h".')
            except CommandError:
                print(css.FAIL+'[ERR]'+css.ENDC+' Invalid value:',params[0])
        elif cmd=='notes':
            if params[0]=='show':
                for note in self.notes:
                    print(css.WARNING+'[NOTE]'+css.ENDC,note)
            elif params[0] in ['add', 'new', 'append']:
                if not '-text' in params:
                    self.notes.append(' '.join(params[1:]))
                else:
                    self.notes.append(' '.join(params[(params.index('-text')+1):]))
            elif params[0]=='flush':
                if params[1]=='*':
                    self.notes=[]
                else:
                    for n in params[1:]:
                        self.notes.remove(n)
            
            return
        elif cmd=='shop':
            # parse before entering
            if not len(params):
                self.inshop=True; return
            else:
                if '-sw' in params:
                    self.shop_support.swindow()
                if '-buy' in params:
                    #print(params)
                    self.shop_support.shop(params[params.index('-buy')+1], prize=json.loads(open('core/Shop/storage/tools.json').read())[params[params.index('-buy')+1]]['prize'])
                if not '-e' in params:
                    self.inshop=True
        elif cmd=='mapstates':
            print(css.WARNING+'[WARN]'+css.ENDC+' This tool is currently having some problems, i will fix this as soon as possible!')
            if '-ot' in params:
                self.showonlytrues=True
                self.showonlyfalse=False
            elif '-of' in params:
                self.showonlytrues=False
                self.showonlyfalse=True
            else:
                print(css.FAIL+'[ERR]'+css.ENDC+' Invalid parameter, check "mapstates -h".')
                return
    
    def subtract_points(self, value):
        global srcdata
        globals()['srcdata']['score']-=int(value)
        self.dump()
        # mantieni il tool acquistato
        #actual_tools=json.loads(open('core/cmds.json'))

    def dump(self):
        f=open('data/dumped.dat','w') # user data
        f.write(base64.b64encode(json.dumps(srcdata).encode()).decode())
        f.close()
        #f=open('core/cmds.json','w') # new commands and sheets
    
    # -- screens
    def win(self):
        if _sys=="linux":
            os.system("clear")
        else:
            os.system('cls')
        titles=[
            '__   _____  _   _  __        _____ _   _ \n\\ \\ / / _ \\| | | | \\ \\      / /_ _| \\ | |\n \\ V / | | | | | |  \\ \\ /\\ / / | ||  \\| |\n  | || |_| | |_| |   \\ V  V /  | || |\\  |\n  |_| \\___/ \\___/     \\_/\\_/  |___|_| \\_|\n                                         \n',
            '                                                \n# #      #      # #         # #     ###     ### \n# #     # #     # #         # #      #      # # \n #      # #     # #         ###      #      # # \n #      # #     # #         ###      #      # # \n #       #      ###         # #     ###     # # \n'
            ]
        srcdata['score']+=points['win']
        srcdata['score']+=self.gamepoints
        f=open('data/dumped.dat','w')
        f.write(base64.b64encode(json.dumps(srcdata).encode()).decode())
        f.close()
        print(css.OKGREEN+random.choice(titles)+css.ENDC)
        input('\n\npress any key to continue..')
        if _sys=="linux":
            os.system("clear")
        else:
            os.system('cls')
        while True:
            print('Do you want to start a new game? (y\\n)')
            r=getch()
            if r=='y':
                main()
            elif r=='n':
                print('Exiting...')
                time.sleep(1); exit(code=0)
            else:
                print('[ERR] Invalid Key',r,'.')
                continue

    def main_menu(self, err=None):
        if _sys=="linux":
            os.system("clear")
        else:
            os.system('cls')
        print('\n\t[-] Hello '+globals()['srcdata']['usrname']+' [-]')
        print('\t'+(' '*4)+css.HEADER+'[SCORE]'+css.ENDC,srcdata['score'],css.HEADER+'[SCORE]\n'+css.ENDC)
        print(css.OKGREEN+'\t'+(' '*5)+'START NEW GAME [1]'+css.ENDC)
        if not offline:
            print(css.OKGREEN+'\t'+(' '*6)+'ONLINE GAME [2]'+css.ENDC)
        print(css.OKGREEN+'\t'+(' '*5)+'EDIT ENEMIES: {n} [3]'.format(n=STARTUPSPWANS),css.ENDC)
        print(css.FAIL+'\t\t  EXIT [0]'+css.ENDC)
        if err:
            print('\n[ERR] invalid key:',err)
        print('\n1 Enter the option key:'); ck=getch()
        if ck in ['s',1,'1','y']:
            if _sys=="linux":
                os.system("clear")
            else:
                os.system('cls')
            self.run()
            return
        elif ck in ['e',0,'0']:
            # dump and exit
            f=open('data/dumped.dat','w')
            f.write(base64.b64encode(json.dumps(globals()['srcdata']).encode()).decode())
            f.close()
            exit()
        elif ck in ['o',2,'2']:
            if offline: self.main_menu(ck)
            self.main_menu('None\nExcuse me im still developing this function, coming soon!')
            # join or start
            if _sys=="linux":
                os.system("clear")
            else:
                os.system('cls')
            print('\n\tPress [1] for START a server, [2] to JOIN. ')
            chsd=getch()
            if chsd in ['1',1]:
                # start
                self.online_start()
            elif chsd in ['2',2]:
                # join
                self.online_join()
            else:
                print(chsd)
        elif ck in [3,'3']:
            print()
            try:
                stdbots_new=int(input('number of standard bots: '))-STARTUPSPWANS
                lvl2bots_new=int(input('number of level 2 bots: '))-1
                if stdbots_new>0:
                    for _ in range(stdbots_new):
                        self.robots.append(Robot(columns,rows,self))
                if lvl2bots_new>0:
                    for _ in range(lvl2bots_new):
                        self.robots.append(Level2Robot(columns,rows,self))
            except:
                self.main_menu('Number\nInvalid value, must be an integer.')
            else:
                self.run()
        else:
            self.main_menu(ck)

    def shop(self, money, *args):
        if not len(args): # mostra la vetrina e entra nel parser
            #self.shop_support.swindow()
            self.shop_support.parser(money)
        else:
            self.shop_support.parser(*args)

    def mktable(self):
        for column in range(columns):
            print('')
            for row in range(rows):
                #print('pos: ',{'x':column, 'y':row})
                pos=[row,column]; done=False
                for obj in self.robots:
                    if self.showonlyfalse:
                        if not obj.state==css.FAIL+'locked'+css.ENDC:
                            print('_',end=' '); done=True
                    if self.showonlytrues:
                        if not obj.state==css.OKGREEN+'unlocked'+css.ENDC:
                            print('_',end=' '); done=True
                    if obj.pos==pos:
                        if self.showonlyfalse:
                            if not obj.state==css.FAIL+'locked'+css.ENDC:
                                print('_',end=' '); done=True
                        if self.showonlytrues:
                            if not obj.state==css.OKGREEN+'unlocked'+css.ENDC:
                                print('_',end=' '); done=True
                        if self.showids:
                            if not done:
                                print(obj.image,obj.id,end=' '); done=True
                        elif self.showpos:
                            if not done:
                                print(obj.image,obj.pos,end=' '); done=True
                        else:
                            print(obj.image,end=' '); done=True
                if not done:
                    print('_',end=' ')
        print('\n')
        return 0

    def docs(self, man):
        data=json.loads(open('core/cmds.json').read())
        for key in data['cheatsheet'][man]:
            print(key,'->',data['cheatsheet'][man][key])

def intro():
    global srcdata
    dialogues=json.loads(open('core/dialogues.json').read())[lang]
    inputs_={}
    for k in dialogues[0]:
        if k.startswith('$input'):
            inputs_.update({k.split()[1]:input()})
            f=open('data/dumped.dat','w+')
            f.write(base64.b64encode(json.dumps(inputs_).encode()).decode())
            f.close()
            srcdata=json.loads(base64.b64decode(open('data/dumped.dat').read()).decode()) # reload
        elif k.startswith('$cls'):
            time.sleep(float(k.split()[1]))
            if _sys=="linux":
                os.system("clear")
            else:
                os.system('cls')
        elif k.startswith('$keydelay'):
            try:
                input(' '.join(k.split()[1:]))
            except:
                input()
        elif k.startswith('$timedelay'):
            time.sleep(float(k.split()[1]))
        else:
            print(k.format(**srcdata))
    # tutorial:
    # non disegnare con i loop
    print('\n')
    print('_ _ _ _ _   Questa è la mappa, gli underscore "_" indicano che il tile è vuoto.')
    print('_ _ _ _ _   i Robot sono indicati con R e la loro posizione è [x,y],')
    print('_ _ _ _ _   per selezionarne uno puoi usare diversi metodi del comando select,')
    print('_ _ _ _ _   con -m specifichi il metodo, usa id per selezionare tramite indrizzo e pos')
    print('_ _ _ _ _   per usare le coordinate. per vedere pos o id scrivi "show pos" o "show id"')
    input('\npress any key...')
    if _sys=="linux":
        os.system("clear")
    else:
        os.system('cls')
    print("l'obiettivo del gioco e' spegnere tutti i robot prima che (niente non ho ancora implementato questa parte).")
    print("Per disattivare un robot devi eseguire il comando shutdown (o destroy, sono la stessa cosa) nella sua shell, come?")
    print("per accedere alla shell bisogna sbloccare il kernel del robot e per farlo devi seguire questi passaggi:")
    print('[CMD] >> select -m MODE VALUE       # sostituisci mode con id o pos e value relativamente con id o coordinate')
    print('[CMD] hash -port                    # mostra tutte le porte e i loro hash')
    print('[CMD] decoder -text HASH            # ritorna la versione decodificata di HASH, usalo per decifrare gli hash di una porta')
    print('[CMD] hash -res DECODEDHASH -port P # usa DECODEDHASH per bypassare la porta P, deve essere la stessa porta da cui hai copiato gli hash')
    print('[CMD] hack PORTNUM                  # cracka il kernel passando per PORTNUM che corrisponde al numero di una port bypassata.')
    print('[CMD] shutdown                      # ora abbiamo accesso a dei comandi MShell come ad esempio shutdown, eseguilo per spegnere il bot.')
    input('\npress any key to continue...')
    if _sys=="linux":
        os.system("clear")
    else:
        os.system('cls')
    print('[*] Tutorial completato!')
    f=open('data/userdata.dat','w')
    f.write(base64.b64encode(json.dumps({'firstlaunch':0}).encode()).decode())
    f.close()
    return inputs_

def main():
    if _sys=="linux":
        os.system("clear")
    else:
        os.system('cls')
    if usrdata['firstlaunch'] in ['1',1] or not 'dumped.dat' in os.listdir('data/'):
        datss=intro()
        datss.update({'score':0})
        #print(datss)
        f=open('data/dumped.dat','w+')
        f.write(base64.b64encode(json.dumps(datss).encode()).decode())
        f.close()
        globals()['srcdata']=datss
        #print(open('data/dumped.dat').read())
        print('[*] Starting Game...\n'); time.sleep(1)
    Game=Engine(spawns=STARTUPSPWANS)
    #Game.run()

# network

BUFFERSIZE = 512
clients={}
eng=Engine(show_title=False)
eng.players={}; eng.outgoing={}
eng.robots=[]

def updateWorld(msg):
    '''
    rcvd commands:
    ['posUpdate', id, newpos]
    ['mkTable', id]

    send commands:
    ['mapUpdate', {id1:pos1}]
    ['table', f]
    '''
    arr=pickle.loads(msg)
    if arr[0]=='posUpdate':
        eng.players[arr[1]].pos=arr[2]
    elif arr[0]=='mkTable':
        eng.outgoing[arr[1]].send(['table', eng.mktable])
    print(arr)

class MainServer(asyncore.dispatcher):
  def __init__(self, port):
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.bind(('127.0.0.1', port)) # external_ip here!
    self.listen(3)
    print('\n[..] Waiting for connection')

  def handle_accept(self):
    conn, addr = self.accept()
    print ('Connection address:' + addr[0] + " " + str(addr[1]))
    playerminion = PlayerModel(columns,rows, '127.0.0.1:8080')
    playerid=random.randint(100,1000)
    playerminion.id=playerid
    eng.players.update({playerid:playerminion})
    eng.outgoing[playerid]=conn
    conn.send(pickle.dumps(['new join', playerid]))
    SecondaryServer(conn)

class SecondaryServer(asyncore.dispatcher_with_send):
  def handle_read(self):
    recievedData = self.recv(BUFFERSIZE)
    if recievedData:
      updateWorld(recievedData)
    else: self.close()


main()