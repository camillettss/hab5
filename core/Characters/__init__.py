import random, time
import json
random.seed(time.time())
from core.Errors import *
from core.Colors import bcolors as css
import base64
from functools import reduce
import socket
import pickle

totalids=[n for n in range(1, 100)]

tips=[
    "one number is correct and well placed",
    "nothing is correct",
    'two numbers are correct but wrong placed',
    'one number is correct but wrong placed',
    'one number is correct but wrong placed'
]

sequences=[[], [], [], [], []]

numbers=[i for i in range(0,10)]

def list_splice(target, start, delete_count=None, *items):
    if delete_count == None:
        delete_count = len(target) - start

    # store removed range in a separate list and replace with *items
    total = start + delete_count
    removed = target[start:total]
    target[start:total] = items

    return removed

def shuffle(matrix):
    for i in range(0, len(matrix)-1):
        j=int(random.random()*(i+1))
        x=matrix[i]
        matrix[i]=matrix[j]
        matrix[j]=x
    return matrix

def spliceRandNumber(array=None):
    if not array:
        array=numbers
    return (list_splice(array,int(random.random()*len(array)), 1))[0]

def newCode():
    global sequences
    code=[None,None,None]
    sequences=[[], [], [], [], []]
    codeNumbers=[spliceRandNumber() for _ in range(3)]

    sequences[0] = [codeNumbers[0], spliceRandNumber(), spliceRandNumber()]
    sequences[1] = [sequences[0][1], spliceRandNumber(), spliceRandNumber()]
    sequences[2] = [codeNumbers[1], codeNumbers[2], sequences[1][1]]
    sequences[3] = [codeNumbers[0], sequences[1][2], spliceRandNumber()]
    fifthSequenceNId = int(random.random()*2)+1
    sequences[4] = [codeNumbers[fifthSequenceNId], spliceRandNumber(), spliceRandNumber()]

    for s in sequences:
        s=shuffle(s)

    places = [sequences[0].index(codeNumbers[0]),None,None]
    
    code[places[0]] = codeNumbers[0]
    
    for i in range(0,3):
        if not code[i]:
            if not codeNumbers[1] in code: # code.index(codeNumbers[1]) < 0:
                code[i] = codeNumbers[1]
                places[1]=i
            else:
                code[i] = codeNumbers[2]
                places[2]=i

    fixThirdSequence(codeNumbers, places)
    fixFourthSequence(codeNumbers, places)
    fixFifthSequence(fifthSequenceNId, codeNumbers, places)

    i=0
    for s in sequences:
        print(s, tips[i])
        i+=1
    
    return code

#fix last sequences
def fixThirdSequence(codeNumbers, places):
    global sequences
    index1=sequences[2].index(codeNumbers[1])
    index2=sequences[2].index(codeNumbers[2])
    if not index1==places[1] and not index2==places[2]: return
    sequences[2][index1] = codeNumbers[2]
    sequences[2][index2] = codeNumbers[1]

def fixFourthSequence(codeNumbers,places):
    global sequences
    index=sequences[3].index(codeNumbers[0])
    for i in range(0,3):
        if not sequences[3][i]==codeNumbers[0] and sequences[3][i] in sequences[3]:
            sequences[3][i]=random.choice(sequences[1])
    if not index==places[0]: return
    if index>1:
        change=sequences[3][index-1]
        sequences[3][index - 1] = codeNumbers[0]
        sequences[3][index] = change
    else:
        change = sequences[3][index + 1]
        sequences[3][index + 1] = codeNumbers[0]
        sequences[3][index] = change

def fixFifthSequence(nId, codeNumbers, places):
    index=sequences[4].index(codeNumbers[nId])
    seqTwoIndex = sequences[2].index(codeNumbers[nId])
    if (index==places[nId] or type(index)==type(places[nId])) or (seqTwoIndex==index or type(seqTwoIndex)==type(index)):
        newIndex= reduce(lambda acc, cur: acc+([cur if not cur==seqTwoIndex and not cur==places[nId] else 0][0]), [0,1,2], 0)
        change= sequences[4][newIndex]
        sequences[4][newIndex] = codeNumbers[nId]
        sequences[4][index]= change

class Kernel():
    def __init__(self):
        self.islocked=True
        self.is_active=True
        self.ports={'80':1, '443':1}
        self.hashes={}
        [self.hashes.update({port:base64.b64encode(''.join([chr(random.randint(97,122)) for _ in range(5)]).encode()).decode()}) for port in self.ports.keys()]

class Robot():
    def __init__(self, cols:int, rows:int, Engine, image='R'):
        self.hp=100
        self.dict_pos={'x':random.randint(0,rows-1),'y':random.randint(0,cols-1)}
        self.pos=list(self.dict_pos.values())
        self.image=image
        self.commands=json.loads(open('core/Characters/cmds.json').read())['commands']
        self.id=str(spliceRandNumber(totalids))
        self.level=1
        self.state=css.FAIL+'locked'+css.ENDC
        # ---
        self.kernel=Kernel()
        self.Engine=Engine
    
    def move(self, pos:dict): raise NotImplementedError

    def parser(self, cmd):
        _cmd=cmd.split()[0].lower()
        params=cmd.split()[1:]
        if '-h' in params:
            self.docs(_cmd)
            return
        #params=[arg.casefold() for arg in params]
        # se _cmd necessita di più parametri ritorna subito un errore
        if (_cmd in ['hack']) and len(params)<=0:
            print(css.FAIL+'[ERR]'+css.ENDC+' Some parameters are missing.'); return
        if not _cmd in self.commands and cmd in self.Engine.shop_support.tools['1']: print(css.OKCYAN+'[SHOP]'+css.ENDC+css.FAIL+'[ERR]'+css.ENDC+' Per usare questo comando devi prima comprarlo.'); return
        if not _cmd in self.commands:
            raise CommandError(cmd)
        else:
            if _cmd=='hack':
                #print(self.kernel.__dict__, params, sep='--')
                if self.kernel.ports[params[0]]==1:
                    raise HackError()
                else:
                    print(css.OKCYAN+'[..]'+css.ENDC+' Hacking on port:',params[0])
                    self.kernel.islocked=False
                    self.state=css.OKGREEN+'unlocked'+css.ENDC
                    time.sleep(0.5)
                    print(css.OKCYAN+'[*]'+css.ENDC+css.OKGREEN+' Successfully hacked.'+css.ENDC)
            elif _cmd=='help':
                print(css.HEADER+'[H]'+css.ENDC+' List of commands:'); [print('-',cmd) for cmd in self.commands]
                print(css.HEADER+'[H]'+css.ENDC+' Type "cmd -h" for info about cmd.')
            elif _cmd=='scan':
                print(css.OKCYAN+'[..]'+css.ENDC+' Scanning...')
                print('[*] Found ports:')
                for port in self.kernel.ports.keys():
                    if self.kernel.ports[port] in ['1',1]:
                        print('-',css.HEADER+port,css.ENDC+' status:'+css.FAIL,self.kernel.ports[port],css.ENDC)
                    else:
                        print('-',port,' status:'+css.OKGREEN,self.kernel.ports[port], css.ENDC)
            elif _cmd in ['destroy', 'shutdown']:
                if self.kernel.islocked: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Unlock kernel first.'); return
                print(css.FAIL+'[..]'+css.ENDC+' Self-Destruction Enabled..')
                self.kernel.is_active=False
                self.Engine.robots.remove(self)
                time.sleep(0.4)
                self.Engine.gamepoints+=1
                print(css.HEADER+'[*]'+css.ENDC+' Bot killed.')
            elif _cmd=='bshell':
                if self.kernel.islocked: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Unlock kernel first.'); return
                if self.kernel.is_active: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Disable kernel first.'); return
                print(css.OKGREEN+'[CMD]'+css.ENDC+' Entering BrainShell...')
                if self.level<=1:
                    print(css.FAIL+'[ERR][#51]'+' BShell unreacheable, this robot hasnt a BShell interface.')
                else:
                    if len(params):
                        self.BShell(' '.join(params))
                    else:
                        self.Engine.inbshell=True
            elif _cmd=='info':
                [print(k,'->',self.kernel.__dict__[k]) for k in self.kernel.__dict__ if not k.startswith('__')]
            elif _cmd=='crack':
                if '-port' in params:
                    p=params[params.index('-port')+1]
                else:
                    p=params[0]
                if self.kernel.islocked: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Unlock kernel first.'); return
                if not self.kernel.is_active: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Kernel already disabled.'); return
                # resolve pattern
                print(css.HEADER+'[PATTERN]'+css.ENDC+' Resolve:')
                code=newCode()
                print(css.OKCYAN+'[INFO]'+css.ENDC+' Code: XXX')
                rep=input(css.OKBLUE+'[SOLUTION]'+css.ENDC+' >> ')
                if rep==''.join([str(i) for i in code]):
                    self.kernel.is_active=False
                    print(css.OKGREEN+'[OK]'+css.ENDC+css.OKCYAN+' Kernel Successfully disabled!'+css.ENDC)
                else:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Verification Failed.')
            elif _cmd=='hash':
                if not len(params): params.append('-port')
                if params[0]=='-port':
                    # show mode, mostra la cifratura della porta
                    try:
                        print(css.OKCYAN+'[HASH]'+css.ENDC,params[1],self.kernel.hashes[str(params[1])])
                    except Exception:
                        [print(css.OKCYAN+'[HASH]'+css.ENDC,key,self.kernel.hashes[key]) for key in self.kernel.hashes.keys()]
                elif params[0]=='-res':
                    # map commands like: {param:val}
                    mappedparams={}
                    ncmd=cmd.lower().split()[1:]
                    for p in ncmd:
                        if not p.startswith('-'): continue
                        try:
                            mappedparams.update({p:ncmd[ncmd.index(p)+1]})
                        except: break
                    if mappedparams['-res']==base64.b64decode(self.kernel.hashes[mappedparams['-port']]).decode():
                        self.kernel.ports[mappedparams['-port']]=0
                        print(css.HEADER+'[*]'+css.ENDC+' Port {p} Successfully bypassed.'.format(p=mappedparams['-port']))
                    else:
                        print(css.FAIL+'[!!] Failed.'+css.ENDC)
                else:
                    print(css.WARNING+'[WARN]'+' Unrecognized param {p}, using "-port" instead.'.format(p=params[0]))
                    try:
                        print(css.OKGREEN+'[HASH]'+css.ENDC,params[1],self.kernel.hashes[str(params[1])])
                    except Exception:
                        [print(css.OKGREEN+'[HASH]'+css.ENDC,key,self.kernel.hashes[key]) for key in self.kernel.hashes.keys()]
            elif _cmd in ['translater', 'encoder', 'decoder']:
                if _cmd=='encoder':
                    s=params[params.index('-text')+1]
                    print(css.HEADER+'[*]'+css.ENDC+' Encoded text: '+css.OKBLUE, base64.b64encode(s).decode(),css.ENDC)
                elif _cmd=='decoder':
                    s=params[params.index('-text')+1]
                    print(css.HEADER+'[*]'+css.ENDC+' Decoded text: '+css.OKBLUE, base64.b64decode(s).decode(),css.ENDC)
                elif _cmd=='translater':
                    if not '-mode' in params:
                        if 'encode' in params or 'decode' in params:
                            if 'encode' in params:
                                s=params[params.index('-text')+1]
                                print(css.HEADER+'[*]'+css.ENDC+' Encoded text: ', base64.b64encode(s).decode())
                            else:
                                s=params[params.index('-text')+1]
                                print(css.HEADER+'[*]'+css.ENDC+' Decoded text: ', base64.b64decode(s).decode())
            elif _cmd == 'exit':
                self.Engine.selected=None
    
    def docs(self, man):
        data=json.loads(open('core/Characters/cmds.json').read())
        for key in data['cheatsheet'][man]:
            print(key,'->',data['cheatsheet'][man][key])

BUFFERSIZE=512
class PlayerModel():
    def __init__(self, c:int, r:int, address, image='P'):
        dict_pos={'x':random.randint(0,r-1),'y':random.randint(0,c-1)}
        self.pos=list(dict_pos.values())
        self.x=dict_pos['x']; self.y=dict_pos['y']
        self.id=None
        # Connect to server
        ip=address.split(':')[0]
        port=int(address.split(':')[1])
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,port))
        self.s=s
    
    def loop(self):
        while True:
            # check in datas
            gameEvent = pickle.loads(self.s.recv(BUFFERSIZE))
            # print the map
            self.s.send(pickle.dumps(['mkTable', self.id]))
            pickle.loads(self.s.recv(BUFFERSIZE))()
            # make data
            raw=self.parser(input('[BOT][CMD] >> '))
            self.s.send(raw)
    
    def parser(self, x):
        try:
            cmd=x.split()[0].lower()
            params=x.split()[1:]
        except IndexError:
            print('[ERR] Index error.'); return None
        return cmd

## old class, use PlayerModel for new server
class Player(Robot):
    def __init__(self, cols:int, rows:int, Engine, image='P'):
        color=Engine.pickColor()[0]
        super().__init__(cols, rows, Engine, color+image+css.ENDC)
        self.x=int(self.pos[0])
        self.y=int(self.pos[1])
        self.world=Engine
        self.cpos=False
    
    def connect(self, address):
        ip=address.split(':')[0]
        port=int(address.split(':')[1])
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,port))
        self.s=s
    
    def _loop(self):
        while True:
            self.world.mktable()
            gameEvent = pickle.loads(self.s.recv(BUFFERSIZE)); data=[]
            if gameEvent[0] == 'npos':
                self.world.players[gameEvent[1]].pos=gameEvent[2]
            #if self.cpos:
                #data.append(['position update', self.id, self.x, self.y])
            data.append(self.parser(input('[CMD] >> ')))
            if data[0]==None:
                self.s.send(''.encode()); continue
            self.s.send(data)
            gameEvent = pickle.loads(self.s.recv(BUFFERSIZE))
            print(gameEvent)
            self.cpos=False
        # aggiorna la mappa ed esegui i comandi ricevuti se ce ne sono
    
    def loop(self):
        while True:
            self.world.mktable()
            gameEvent = pickle.loads(self.s.recv(BUFFERSIZE))
            if gameEvent[0]=='mapUpdate':
                for _id, _pos in gameEvent[1].items():
                    self.world.players[_id].pos=_pos

    def parser(self, x):
        try:
            cmd=x.split()[0].lower()
            params=x.split()[1:]
        except IndexError:
            print('[ERR] Index error.'); return None
        commands=['move']
        if not cmd in commands:
            print('[ERR] Unknown command.'); return None
        if cmd=='move':
            self.cpos=True
            newpos= self.move(params[0])
            if newpos:
                return ['npos', self.id, newpos]
            else:
                return ['npos', self.id, self.pos]
    
    def move(self, pos):
        newx=int(pos.split(',')[0]); x=self.pos[0]
        newy=int(pos.split(',')[1]); y=self.pos[1]
        skip=None
        if x in [0,5]:
            if newx>x:
                if x==4:
                    skip='x'
            else:
                if x==0:
                    skip='x'
        if y in [0,4]:
            if newy>y:
                if y==3:
                    skip='y'
            else:
                if y==0:
                    skip='y'
        if not skip:
            self.pos=[newx, newy]
        else:
            if skip=='y':
                self.pos=[newx, y]
            else:
                self.pos=[x, newy]      


class Level2Robot(Robot):
    def __init__(self, cols:int, rows:int, Engine, image='M'):
        super().__init__(cols, rows, Engine, image)
        self.level=2
        self.selected=None
        self.kernel.islocked=True
        self.kernel.is_active=True
        #self.id=list_splice(totalids, 0, 1)
    
    def parser(self, x):
        super().parser(x)
    
    def BShell(self, x=None):
        comms=json.loads(open('core/Characters/cmds.json').read())['bscommands']
        cmd=x.split()[0].lower()
        params=x.split()[1:]
        if '-h' in params: self.BSHdocs(cmd); return
        if not cmd in comms:
            if cmd=='bshell' or not cmd:
                # start a serial communication
                self.Engine.inbshell=True
                if params[0] in comms:
                    cmd=params[0]
                    params.remove(params[0])
                else: return
            else:
                print(css.FAIL+'[ERR]'+css.ENDC+' Unrecognized command:', cmd)
                return
        # exec live commands
        if cmd=='move':
            if '-pos' in params:
                self.move(params[params.index('-pos')+1])
            else:
                self.move(params[0])
        elif cmd in ['atk', 'attack']:
            if '-h' in params:
                self.BSHdocs(cmd)
            bot=None
            #if not '-pos' in params: and not '-id' in params:
            #    print(css.FAIL+'[ERR]'+css.ENDC+' Invalid syntax, check "atk -h" for help.'); return
            #if self.selected and not '-bot' in params:
                #bot=self.selected
            #if not '-bot' in params:
                # find the bot
                # default method = id
            if not '-pos' in params: # if doesnt override selecting mode
                for obj in self.Engine.robots:
                    try:
                        if str(obj.id)==str(params[params.index('-id')+1]):
                            bot=obj; break
                    except:
                        if str(obj.id)==str(params[0]):
                            bot=obj; break
                if not bot:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Invalid id.')
            else:
                # use position
                for obj in self.Engine.robots:
                    if str(obj.pos)==str(params[params.index('-pos')+1]):
                        bot=obj; break
                if not bot:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Invalid position.')
            if not self.inrange(bot): print(css.FAIL+'[ERR][#78]'+css.ENDC+' Bot unreachable, too far.'); return
            print('[*] Decoded hashes:')
            if not '-port' in params:
                [print('- port',port,'\b:',base64.b64decode(bot.kernel.hashes[port]).decode()) for port in bot.kernel.hashes.keys()]
            else:
                print('- port',port,'\b:',base64.b64decode(bot.kernel.hashes[params[params.index('-port')+1]]).decode())
        elif cmd=='retrieve':
            # qualsiasi pos va bene
            if not '-pos' in params: # if doesnt override selecting mode
                for obj in self.Engine.robots:
                    if str(obj.id)==str(params[params.index('-id')+1]):
                            bot=obj; break
                if not bot:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Invalid id.')
            else:
                # use position
                for obj in self.Engine.robots:
                    if str(obj.pos)==str(params[params.index('-pos')+1]):
                        bot=obj; break
            if not bot:
                print(css.FAIL+'[ERR]'+css.ENDC+' Invalid position.')
            print('[*] Retrieved data:')
            [print('[BOTDATA]',k,'->',bot.__dict__[k]) for k in bot.__dict__ if not k.startswith('__')]
            print()
            [print('[KERNEL]',k,'->',bot.kernel.__dict__[k]) for k in bot.kernel.__dict__ if not k.startswith('__')]
        elif cmd in ['dmg', 'fire']:
            if not '-pos' in params: # if doesnt override selecting mode
                for obj in self.Engine.robots:
                    if str(obj.id)==str(params[params.index('-id')+1]):
                            bot=obj; break
                if not bot:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Invalid id.')
            else:
                # use position
                for obj in self.Engine.robots:
                    if str(obj.pos)==str(params[params.index('-pos')+1]):
                        bot=obj; break
            if not bot:
                print(css.FAIL+'[ERR]'+css.ENDC+' Invalid position.')
            if bot.kernel.islocked: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Unlock kernel first.'); return
            print(css.FAIL+'[..]'+css.ENDC+' Self-Destruction Enabled..')
            bot.kernel.is_active=False
            self.Engine.robots.remove(bot)
            time.sleep(0.4)
            self.Engine.gamepoints+=1
            print(css.HEADER+'[*]'+css.ENDC+' Bot killed.')
        elif cmd in ['remotehack', 'rmh']:
            bot=None
            if not '-pos' in params: # if doesnt override selecting mode
                for obj in self.Engine.robots:
                    try:
                        if str(obj.id)==str(params[params.index('-id')+1]):
                            bot=obj; break
                    except:
                        if str(obj.id)==str(params[0]):
                            bot=obj; break
                if not bot:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Invalid id.')
            else:
                # use position
                for obj in self.Engine.robots:
                    if str(obj.pos)==str(params[params.index('-pos')+1]):
                        bot=obj; break
            if not bot:
                print(css.FAIL+'[ERR]'+css.ENDC+' Invalid position.'); return
            print(css.OKCYAN+'[..]'+css.ENDC+' Hacking bot',bot.id)
            bot.kernel.islocked=False
            bot.state=css.OKGREEN+'unlocked'+css.ENDC
            time.sleep(0.5)
            print(css.OKCYAN+'[*]'+css.ENDC+css.OKGREEN+' Successfully hacked.'+css.ENDC)
        elif cmd in ['bye', 'exit']:
            self.Engine.inbshell=False
        elif cmd=='help':
            print(css.HEADER+'[H]'+css.ENDC+' List of commands:'); [print('-',cmd) for cmd in comms]
            print(css.HEADER+'[H]'+css.ENDC+' Type "cmd -h" for info about cmd.')
        elif cmd=='map':
            if not len(params):
                md='std'
            else:
                if '-mode' in params:
                    md=params[params.index('-mode')+1]
                elif '-m' in params:
                    md=params[params.index('-m')+1]
                else:
                    md=params[0]
            if md in ['std', 'default', 'rapid', 'rmap']:
                # rapid map
                for bot in self.Engine.robots:
                    if bot.id==self.id: continue
                    print('- bot'+css.OKBLUE,bot.id,css.ENDC+'at'+css.OKBLUE,bot.pos,css.ENDC+'state:'+bot.state)
            elif md in ['org', 'orig', 'original', 'general', 'main']:
                # main map
                if '-set' in params:
                    var=params[params.index('-set')+1]; val=params[params.index('-set')+2]
                    print(var,val)
                    if var in ['showids','showpos']:
                        exec('self.Engine.'+var+'='+repr(bool(val)))
                self.Engine.mktable()
            else:
                print(css.FAIL+'[ERR]'+css.ENDC+' Unknown mode:', md)
                return
    
    def BSHdocs(self, man):
        data=json.loads(open('core/Characters/cmds.json').read())
        for key in data['BSSheet'][man]:
            print(key,'->',data['BSSheet'][man][key])
    
    def inrange(self, x):
        bx=x.pos[0]
        by=x.pos[1]
        print(self.pos, x.pos)
        if not int(bx) > int(self.pos[0])+1 and not int(bx) < int(self.pos[0])-1: # check x coords first
            if not int(by) > int(self.pos[1])+1 and not int(by) < int(self.pos[1])-1: # now ys
                return True
        return False

    def move(self, pos):
        newx=int(pos.split(',')[0]); x=self.pos[0]
        newy=int(pos.split(',')[1]); y=self.pos[1]
        skip=None
        if x in [0,5]:
            if newx>x:
                if x==4:
                    skip='x'
            else:
                if x==0:
                    skip='x'
        if y in [0,4]:
            if newy>y:
                if y==3:
                    skip='y'
            else:
                if y==0:
                    skip='y'
        if not skip:
            for bot in self.Engine.robots:
                if bot.pos==[newx, newy]:
                    if not bot.id==self.id:
                        print(css.FAIL+'[ERR]'+css.ENDC+' ID:',bot.id,'already in',newx,',',newy,'!')
                    return
            self.pos=[newx, newy]
        else:
            if skip=='y':
                for bot in self.Engine.robots:
                    if bot.pos==[newx, y]:
                        if not bot.id==self.id:
                            print(css.FAIL+'[ERR]'+css.ENDC+' ID:',bot.id,'already in',newx,',',newy,'!')
                        return
                self.pos=[newx, y]
            else:
                for bot in self.Engine.robots:
                    if bot.pos==[x, newy]:
                        if not bot.id==self.id:
                            print(css.FAIL+'[ERR]'+css.ENDC+' ID:',bot.id,'already in',newx,',',newy,'!')
                        return
                self.pos=[x, newy]
    
    def attack(self, bot):
        print(self,'attacking',bot)
        return
