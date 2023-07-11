import json
import threading
import pygame as pg
from random import randint
from game.colors import Colors as clr
from game.player import Player
from game.network import Network


class Game:
    def __init__(self) -> None:
        self.pid = randint(1, 100000)
        self.board_width = 10
        self.board_height = 10
        self.cell_size = 40

        bw = self.board_width * self.cell_size
        bh = self.board_height * self.cell_size
        self.window_sizes = bw + 100, bh + 100
        self.board_sizes = (bw, bh)
        offset_x = self.window_sizes[0] / 2 - bw / 2
        offset_y = self.window_sizes[1] / 2 - bh / 2
        self.board_offset = offset_x, offset_y

        self.players = []
        self.own_player = Player(self.pid, [0, 0], (self.board_width, self.board_height))
        self.players.append(self.own_player)

        self.apple = [-100, -100]
        self.current_press = None
        self.last_direction = None

        with open('config.json', 'r') as f:
            config = json.loads(f.read())
        print(config)

        self.net = Network((config['host'], config['port']))

    def move(self, direction):
        if not self.own_player.alive:
            return
        old_pos = self.own_player.pos.copy()
        self.last_direction = direction
        def death():
            self.own_player.pos = old_pos
            self.own_player.alive = False
            data = {
                'type': 'death',
                'pid': self.pid
            }
            self.net.send(json.dumps(data).encode())
        match direction:
            case "a":
                self.own_player.pos[0] -= 1
                if self.own_player.pos[0] < 0:
                    death()
                    return
            case "w":
                self.own_player.pos[1] -= 1
                if self.own_player.pos[1] < 0:
                    death()
                    return
            case "d":
                self.own_player.pos[0] += 1
                if self.own_player.pos[0] >= self.board_width:
                    death()
                    return
            case "s":
                self.own_player.pos[1] += 1
                if self.own_player.pos[1] >= self.board_height:
                    death()
                    return
                
        own = self.own_player
        if own.pos in [t[:2] for t in own.tail]:
            death()
            return
        for p in self.players:
            if p == self.own_player:
                continue
            if own.pos in [p.pos, *[t[:2] for t in p.tail]]:
                death()
                return
        if self.own_player.pos == self.apple:
            self.apple = [-100, -100]
            self.own_player.length += 1
        self.own_player.tail.append([*old_pos, own.length])
        if len(own.tail) > own.length:
            own.tail.pop(0)
        
        data = {
            "type": 'player_pocket',
            "id": self.pid,
            "pos": own.pos,
            "tail": [t[:2] for t in own.tail]
        }
        self.net.send(json.dumps(data).encode())
    
    def handle_input(self):
        events = pg.event.get()
        for e in events:
            if e.type == pg.QUIT:
                pg.quit()
            
            if e.type == pg.KEYDOWN:
                if e.unicode in ["a", "s", "d", "w"]:
                    if self.last_direction == "a" and e.unicode == "d":
                        continue
                    if self.last_direction == "s" and e.unicode == "w":
                        continue
                    if self.last_direction == "w" and e.unicode == "s":
                        continue
                    if self.last_direction == "d" and e.unicode == "a":
                        continue
                    self.current_press = e.unicode
    
    def draw_screen(self):
        self.screen.fill((clr.bg))
        off = self.board_offset
        cs = self.cell_size
        for x in range(self.board_width):
            for y in range(self.board_height):
                pg.draw.rect(self.screen, clr.cell, (off[0] + x * cs, off[1] + y * cs, cs, cs), border_radius=10)
        
        a = self.apple
        pg.draw.rect(self.screen, clr.apple, [off[0] + cs * a[0], off[1] + cs * a[1], cs, cs], border_radius=10)
        
        for plr in self.players:
            plr: Player
            if not plr.alive:
                self.players.remove(plr)
            x, y = plr.pos
            pg.draw.rect(self.screen, clr.player_head, (off[0] + x * cs, off[1] + y * cs, cs, cs), border_radius=10)
            for i, t in enumerate(plr.tail):
                color = clr.player_body_1 if i % 2 else clr.player_body_2
                pg.draw.rect(self.screen, color, (off[0] + t[0] * cs, off[1] + t[1] * cs, cs, cs), border_radius=10)
    
    def game_update(self):
        for p in self.players:
            if p == self.own_player:
                continue
            if p.deez_nuts():
                self.players.remove(p)
        if self.current_press in ["a", "s", "d", "w"]:
            self.move(self.current_press)

    def net_pocks(self, data: bytes):
        # try:
        data = json.loads(data.decode())
        if data['type'] == "player_pocket":
            for p in self.players:
                if p.pid == data['id']:
                    player = p
                    break
            else:
                player = Player(data['id'], data['pos'], (self.board_width, self.board_height))
                self.players.append(player)
            player.pos = data['pos']
            player.tail = data['tail']
            player.update_pocket_time()
        elif data['type'] == "appol":
            self.apple = data["pos"]
        elif data['type'] == 'death':
            for p in self.players:
                p: Player
                if p.pid == data['pid']:
                    self.players.remove(p)
                    return
        # except Exception as err:
        #     print(err)
    
    def run(self):
        pg.init()
        pg.display.set_caption("Walmart Snake")
        self.screen = pg.display.set_mode(self.window_sizes)
        icon = pg.image.load("assets/game_logo.webp").convert_alpha()
        pg.display.set_icon(icon)
        clock = pg.time.Clock()
        net_thread = threading.Thread(target=self.net.listen_loop, args=[self.net_pocks])
        net_thread.start()
        frame = 0
        while True:
            self.handle_input()
            if frame % 30 == 0:
                self.game_update()
            frame += 1
            self.draw_screen()
            pg.display.flip()
            clock.tick(60)
