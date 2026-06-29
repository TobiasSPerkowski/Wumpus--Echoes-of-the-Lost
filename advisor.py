import sys
from pysat.solvers import Solver
from pysat.formula import IDPool


# === BASE DE CONHECIMENTO ===

class WumpusKB:
    def __init__(self):
        self.vpool = IDPool() # gerenciador de literais
        self.solver = Solver(name='glucose3')

    # cria literal para poco em (x,y)
    def pit(self, x,y):
        return self.vpool.id(f"P_{x}_{y}")

    # cria literal para poco em (x,y)
    def wumpus(self, x,y):
        return self.vpool.id(f"W_{x}_{y}")

    # adiciona clausula ao solver ("TELL")
    def add_clause(self, c):
        self.solver.add_clause(c)

    # cria e adiciona clausulas para a ausencia de pocos 
    # adj eh uma lista com as celulas adjacentes a atual
    def no_pits(self, adj):
        for x,y in adj:
            self.add_clause([-self.pit(x,y)])

    # cria e adiciona uma clausula para possiveis pocos
    def pits(self, adj):
        clause = [self.pit(x,y) for x,y in adj]
        if clause:
            self.add_clause(clause)

    # cria e adiciona clausulas para a ausencia de wumpus 
    def no_wumpuses(self, adj):
        for x,y in adj:
            self.add_clause([-self.wumpus(x,y)])

    # cria e adiciona uma clausula para possiveis wumpus
    def wumpuses(self, adj):
        clause = [self.wumpus(x,y) for x,y in adj]
        if clause:
            self.add_clause(clause)

    # usa solver para verificar se eh possivel ter poco ("ASK")
    def pit_possible(self, cell):
        p = self.pit(cell[0], cell[1])
        return self.solver.solve(assumptions=[p])

    # usa solver para verificar se eh possivel ter wumpus ("ASK")
    def wumpus_possible(self, cell):
        w = self.wumpus(cell[0], cell[1])
        return self.solver.solve(assumptions=[w])


# === CELULA ===
#apenas uma reprsentacao interna usada pelo conselheiro

class Cell:
    def __init__(self, v = False, s = False):
        self.visited = v
        self.safe = s
        self.breeze = False
        self.stench = False
        self.w_poss = False # wumpus possivel
        self.wall = False
    
    def __str__(self):
        v = "visited" if self.visited else "not visited"
        sa = "safe" if self.safe else "not safe"
        b = "breeze" if self.breeze else "no breeze"
        st = "stench" if self.stench else "no stench"
        w = "wall" if self.wall else "no wall"
        return v + ", " + sa + ", " + b + ", " + st + ", " + w


# === CONSELHEIRO ===

class Advisor:
    def __init__(self):
        self.pos = (0, 0)
        self.dir = 0
        self.arrows = 0
        self.shots = []

        # celula inicial eh segura
        self.cells = dict()
        self.cells[self.pos] = Cell(v=True, s=True)

        self.kb = WumpusKB()
        no_pit = -self.kb.pit(0,0)
        no_wumpus = -self.kb.wumpus(0,0)
        self.kb.add_clause([no_pit])
        self.kb.add_clause([no_wumpus])

        # celulas adjacentes sao seguras
        adj = self.adj(self.pos)
        for c in adj:
            self.cells[c] = Cell(s=True)

        self.kb.no_pits(adj)
        self.kb.no_wumpuses(adj)

  
    def add_arrows(self, amount):
        self.arrows += amount


    def turn_left(self):
        self.dir = (self.dir - 1) % 4 
    

    def turn_right(self):
        self.dir = (self.dir + 1) % 4 


    # retorna coords da posicao a frente
    def forward_pos(self):
        x,y = self.pos
        if self.dir == 0: # Norte
            return (x, y+1)
        if self.dir == 1: # Leste
            return (x+1, y)
        if self.dir == 2: # Sul
            return (x, y-1)
        # Oeste
        return (x-1, y)
    
    # verifica se c eh segura
    def is_safe(self, c):
        cell = self.cells[c]
        if cell.safe:
            return True
        
        # se ainda nao souber, consulta base de conhecimento
        cell.w_poss = self.kb.wumpus_possible(c)
        if not cell.w_poss and not self.kb.pit_possible(c):
            cell.safe = True
            return True
        
        return False


    # retorna celulas adjacentes a pos
    def adj(self, pos):
        x,y = pos
        # retornando na melhor ordem (evita giros desnecessarios)
        if self.dir == 0: # Norte
            return [(x, y+1), (x-1, y), (x, y-1), (x+1, y)]
        if self.dir == 1: # Leste
            return [(x+1, y), (x, y+1), (x-1, y), (x, y-1)]
        if self.dir == 2: # Sul
            return [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]
        # Oeste
        return [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]


    # atualiza estado interno do conselheiro
    def update(self, sensors):
        stench, breeze, bump = sensors

        if bump == '1': # parede
            wall = self.forward_pos()
            self.cells[wall].wall = True
            self.cells[wall].visited = True
            # atualiza base de conhecimento
            no_pit = -self.kb.pit(wall[0], wall[1])
            no_wumpus = -self.kb.wumpus(wall[0], wall[1])
            self.kb.add_clause([no_pit])
            self.kb.add_clause([no_wumpus])
            return

        # atualizando variaveis e BC
        self.pos = self.forward_pos()
        curr_cell = self.cells[self.pos]
        curr_cell.visited = True
        for c in self.adj(self.pos):
            if c not in self.cells:
                self.cells[c] = Cell()

        adj = [c for c in self.adj(self.pos) if not self.cells[c].wall]

        if breeze == '1':
            self.cells[self.pos].breeze = True
            self.kb.pits(adj)
        else:
            self.kb.no_pits(adj)

        if stench == '1':
            self.cells[self.pos].stench = True
            self.kb.wumpuses(adj)
        else:
            self.kb.no_wumpuses(adj)
        
        # checando seguranca
        for c in adj:
            self.is_safe(c)


    # retorna a diferenca entre target e a posicao atual
    def get_offset(self, target):
        x,y = self.pos
        tx,ty = target
        return (tx - x, ty - y)
    

    # verifica se uma celula eh uma opcao para movimento
    def is_valid_move(self, cell):
        safe = self.is_safe(cell)
        visited = self.cells[cell].visited
        wall = self.cells[cell].wall
        return safe and not visited and not wall
    

    # verifica se uma celula eh uma opcao para disparo
    def is_valid_shot(self, cell):
        visited = self.cells[cell].visited
        wall = self.cells[cell].wall
        return not visited and not wall
    

    # escolhe uma celula para indicar
    def choose(self):
        # procura pela celula segura nao visitada mais proxima
        target = self.best_move()
        if target:
            return self.get_offset(target)
        
        #se n tiver nenhuma, procura uma para disparar
        if self.arrows > 0:
            target = self.best_shot()
            if target:
                return "s, " + str(self.get_offset(target))

        # sem solucao
        return "e"
    

    # retorna distancia e quantidade de rotacoes pra chegar em cell
    def move_cost(self, cell):
        dx,dy = self.get_offset(cell)
        dist = abs(dx) + abs(dy)

        if abs(dx) > abs(dy):
            dir = 1 if dx > 0 else 3 # E else W
        else:
            dir = 0 if dy > 0 else 2 # N else S
        
        turns = min((dir - self.dir) % 4, (self.dir - dir) % 4)

        return (dist, turns)
    

    # retorna o melhor movimento (se houver algum)
    def best_move(self):
        best = None
        best_cost = (float("inf"), float("inf")) 

        for c in self.cells:
            if self.is_valid_move(c):
                
                cost = self.move_cost(c)

                if cost < best_cost:
                    best = c
                    best_cost = cost
        
        return best


    # retorna quantidade de celulas adjacentes desconhecidas, com fedor,
    # com brisa e com parede
    def adj_stats(self, cell):
        unknown = 0
        stenches = 0
        breezes = 0
        walls = 0
    
        for a in self.adj(cell):
            if a not in self.cells or not self.cells[a].visited:
                unknown += 1
            else:
                if self.cells[a].stench:
                    stenches += 1
                if self.cells[a].breeze:
                    breezes += 1
                if self.cells[a].wall:
                    walls += 1

        return (unknown, stenches, breezes, walls)
    

    # retorna o melhor disparo (se houver algum)
    def best_shot(self):
        best = None
        best_u = 0
        best_b = 4
        best_w = 4
        best_cost = (float("inf"), float("inf")) 

        for c in self.cells:
            if self.is_valid_shot(c):
                # avalia infos das celulas adjacentes
                u, s, b, w = self.adj_stats(c)
                cost = self.move_cost(c)

                # filtrando
                if b >= s:
                    continue # mais chance de poco do que wumpus
                if u < best_u:
                    continue # menos desconhecidas
                if u == best_u:
                    if b > best_b or w > best_w:
                        continue # mais pocos ou wumpus
                    if cost >= best_cost:
                        continue # mais distante

                # se chegou aqui, eh o melhor disparo ate o momento
                best = c
                best_u = u
                best_b = b
                best_w = w
                best_cost = cost

        return best
    

    # retorna se a posicao a frente eh segura
    def is_forward_safe(self):
        fp = self.forward_pos()

        # checando se ficou segura depois de um disparo
        self.check_shots()

        if self.is_safe(fp):
            return True
        
        return False
    
    # percorre lista de disparos e atualiza base de conhecimento
    def check_shots(self):
        for shot in self.shots[:]: # usa copia pra nao pular elementos apos remocao
            pos, dir, scream = shot
            cells = []

            # pegando celulas na direcao do disparo
            if dir == 0: # Norte
                cells = [c for c in self.cells if c[0] == pos[0] and c[1] > pos[1]]
            elif dir == 1: # Leste
                cells = [c for c in self.cells if c[1] == pos[1] and c[0] > pos[0]]
            elif dir == 2: # Sul
                cells = [c for c in self.cells if c[0] == pos[0] and c[1] < pos[1]]
            else: # Oeste
                cells = [c for c in self.cells if c[1] == pos[1] and c[0] < pos[0]]

            # percorrendo celulas 
            if scream: # acertou wumpus
                for c in cells:
                    cell = self.cells[c]
                    if cell.w_poss: 
                        no_wumpus = -self.kb.wumpus(c[0],c[1])
                        self.kb.add_clause([no_wumpus])
                        self.shots.remove(shot)
                        break
            else: # acertou parede
                for c in cells:
                    cell = self.cells[c]
                    no_wumpus = -self.kb.wumpus(c[0],c[1])
                    self.kb.add_clause([no_wumpus])
                    if cell.wall:
                        self.shots.remove(shot)
                        break       


    # armazena infos de um disparo
    def arrow_shot(self, scream):
        shot = (self.pos, self.dir, scream)
        self.shots.append(shot)
        
        self.arrows -= 1
        

# === MAIN ===

advisor = Advisor()

while True:
    line = sys.stdin.readline()
    if not line:
        break

    input = line.strip().split()
    if not len(input) > 0:
        break

    if input[0] == "h": # jogador pediu ajuda
        move = advisor.choose()
        print(move, flush=True)
    elif input[0] == "c": # checar seguranca
        safe = advisor.is_forward_safe()
        print(safe, flush=True)
    elif input[0] == "l": # jogador virou pra esquerda
        advisor.turn_left()
    elif input[0] == "r": # jogador virou pra direita
        advisor.turn_right()
    elif input[0] == "a": # jogador recebeu flechas
        advisor.add_arrows(int(input[1]))
    elif input[0] == "s": # jogador disparou flecha
        advisor.arrow_shot(int(input[1]))
    elif len(input[0]) == 3: # jogador moveu (3 sensores: fedor, brisa e colisao)
        advisor.update(input[0])
    else:
        break
