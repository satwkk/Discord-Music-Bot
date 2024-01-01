import sqlite3
from sqlite3 import Connection
import pathlib

DB_NAME = 'saved_songs.db'
handle: Connection = sqlite3.connect('saved_songs.db')