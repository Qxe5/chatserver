from curses import wrapper
import curses
import win
import socket
import threading
import memory
import sys
import time

NICK = "venomega"
USER = "Ernest Brown"


def connect():
    memory.object = socket.socket()
    memory.object.connect(
        ("ewjhkxhpajxzmvifpzy2zrbbk5yrnkmlomputw2gm2qipvz6pqbuviqd.onion", 2000))
    threading.Thread(target=the_reader).start()


def the_reader():
    while memory.status:
        buff = memory.object.recv(3300)
        alloc = b""
        for i in buff:
            if i == 10:
                memory.window.buffer_add("")
                alloc = b""
            if i == 32:
                alloc += b" "
            if (i >= 97 and i <= 122) or (i >= 65 and i <= 90):
                if i != 13:
                    alloc += i.to_bytes(1, 'little')
        recv = alloc.decode()
        memory.window.buffer_add(recv)


def monitor_loop():
    while True:
        memory.window.write_buffer()
        time.sleep(1)


def screen(stdscr):
    global NICK, USER
    memory.screen_width = curses.COLS - 2
    memory.window = win.window(0.90, 0.99, 0.01, 0.01)
    memory.window.build()
    connect()
    threading.Thread(target=monitor_loop).start()

    o = win.window(0.1, 0.99, 0.91, 0.01)
    o.build()
    buffer = ""
    while True:
        asd = o.win.getch()
        if asd == 10:  # enter
            memory.object.send(f"{buffer}\n".encode())
            buffer = ""
        if asd >= 97 and asd <= 122:  # lower keys
            buffer += asd.to_bytes(1, 'little').decode()
        if asd >= 65 and asd <= 90:  # upper keys
            buffer += asd.to_bytes(1, 'little').decode()
        o.write(0, 0, " " * memory.screen_width - 2)
        o.write(0, 0, buffer)


wrapper(screen)
# connect()
# input()
