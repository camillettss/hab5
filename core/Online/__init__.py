import socket
import asyncore
import random
import pickle
import time
from core.Characters import Player

BUFFERSIZE=512

clients=[]

