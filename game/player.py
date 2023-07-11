from datetime import datetime

class Player:
    def __init__(self, pid, pos, board_sizes) -> None:
        self.pos = pos
        self.pid = pid
        self.tail = []
        self.length = 3
        self.alive = True
        self.last_pocket = datetime.now()
        self.board_sizes = board_sizes
    
    def update_pocket_time(self):
        self.last_pocket = datetime.now()
    
    def deez_nuts(self):
        if (datetime.now() - self.last_pocket).seconds > 5:
            return True
        return False
