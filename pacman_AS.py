"""
pacman_AS.py - Test Run March 11, 2026
Team: pacmanAS
Based on Problem Set 4 concepts: A*, heuristics, planning
"""

from contest.capture_agents import CaptureAgent
import random

def create_team(first_index, second_index, is_red,
                first='AgenteOfensivo', second='AgenteDefensivo'):
    """
    Required factory function.
    Returns list with 2 agents: offensive and defensive.
    """
    return [eval(first)(first_index), eval(second)(second_index)]


class AgenteOfensivo(CaptureAgent):
    """
    OFFENSIVE AGENT: Captures enemy food
    States: ATTACK → RETURN → ESCAPE
    """
    
    def register_initial_state(self, game_state):
        """Initialization (max 15 seconds)"""
        CaptureAgent.register_initial_state(self, game_state)
        self.start = game_state.get_agent_position(self.index)
        
        # Calculate frontier (map midline)
        if self.red:
            self.frontera_x = game_state.data.layout.width // 2 - 1
        else:
            self.frontera_x = game_state.data.layout.width // 2
        
        print(f"[OFFENSIVE {self.index}] Ready at {self.start}")
    
    def choose_action(self, game_state):
        """Action decision (max 1 second)"""
        try:
            mi_estado = game_state.get_agent_state(self.index)
            mi_pos = mi_estado.get_position()
            comida_llevando = mi_estado.num_carrying
            
            # Get legal actions
            acciones = game_state.get_legal_actions(self.index)
            if 'Stop' in acciones:
                acciones.remove('Stop')
            
            if not acciones:
                return 'Stop'
            
            # Detect enemy ghosts
            enemigos = [game_state.get_agent_state(i) for i in self.get_opponents(game_state)]
            fantasmas = [e for e in enemigos if not e.is_pacman and e.get_position() is not None]
            
            # DECISION: What to do?
            if fantasmas:
                dist_min_fantasma = min(self.get_maze_distance(mi_pos, f.get_position()) for f in fantasmas)
                
                # ESCAPE if ghost very close
                if dist_min_fantasma <= 3:
                    return self.escapar(game_state, acciones, fantasmas)
            
            # RETURN if carrying 5+ food
            if comida_llevando >= 5:
                return self.regresar(game_state, acciones)
            
            # ATTACK by default
            return self.atacar(game_state, acciones)
        
        except Exception as e:
            print(f"ERROR offensive: {e}")
            return random.choice(acciones) if acciones else 'Stop'
    
    def atacar(self, game_state, acciones):
        """Find nearest food (simplified A*)"""
        mi_pos = game_state.get_agent_state(self.index).get_position()
        comida = self.get_food(game_state).as_list()
        
        if not comida:
            return random.choice(acciones)
        
        # Evaluate each action
        mejor_accion = None
        mejor_dist = float('inf')
        
        for accion in acciones:
            sucesor = self.get_successor(game_state, accion)
            pos_sig = sucesor.get_agent_state(self.index).get_position()
            
            # Heuristic: distance to nearest food
            dist = min(self.get_maze_distance(pos_sig, c) for c in comida)
            
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else random.choice(acciones)
    
    def regresar(self, game_state, acciones):
        """Return home to deposit food"""
        mi_pos = game_state.get_agent_state(self.index).get_position()
        walls = game_state.get_walls()
        altura = walls.height
        
        # Frontier points (home territory)
        frontera = [(self.frontera_x, y) for y in range(altura) if not walls[self.frontera_x][y]]
        
        if not frontera:
            return random.choice(acciones)
        
        # Go to nearest frontier point
        mejor_accion = None
        mejor_dist = float('inf')
        
        for accion in acciones:
            sucesor = self.get_successor(game_state, accion)
            pos_sig = sucesor.get_agent_state(self.index).get_position()
            
            dist = min(self.get_maze_distance(pos_sig, p) for p in frontera)
            
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else random.choice(acciones)
    
    def escapar(self, game_state, acciones, fantasmas):
        """Maximize distance from ghosts"""
        mejor_accion = None
        mejor_dist = -1
        
        for accion in acciones:
            sucesor = self.get_successor(game_state, accion)
            pos_sig = sucesor.get_agent_state(self.index).get_position()
            
            # Minimum distance to ghosts
            dist_min = min(self.get_maze_distance(pos_sig, f.get_position()) for f in fantasmas)
            
            if dist_min > mejor_dist:
                mejor_dist = dist_min
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else random.choice(acciones)
    
    def get_successor(self, game_state, action):
        """Helper: generate successor state"""
        return game_state.generate_successor(self.index, action)


class AgenteDefensivo(CaptureAgent):
    """
    DEFENSIVE AGENT: Protects territory
    States: PATROL → PURSUE
    """
    
    def register_initial_state(self, game_state):
        """Initialization"""
        CaptureAgent.register_initial_state(self, game_state)
        self.start = game_state.get_agent_position(self.index)
        
        # Calculate patrol points
        comida = self.get_food_you_are_defending(game_state).as_list()
        if comida:
            comida_sorted = sorted(comida, key=lambda c: c[1])
            self.patrulla = [
                comida_sorted[0],
                comida_sorted[len(comida_sorted) // 2],
                comida_sorted[-1]
            ]
        else:
            self.patrulla = [self.start]
        
        self.idx_patrulla = 0
        print(f"[DEFENSIVE {self.index}] Patrol: {len(self.patrulla)} points")
    
    def choose_action(self, game_state):
        """Defensive decision"""
        try:
            mi_pos = game_state.get_agent_state(self.index).get_position()
            
            # Detect invaders
            enemigos = [game_state.get_agent_state(i) for i in self.get_opponents(game_state)]
            invasores = [e for e in enemigos if e.is_pacman and e.get_position() is not None]
            
            acciones = game_state.get_legal_actions(self.index)
            if 'Stop' in acciones:
                acciones.remove('Stop')
            
            if not acciones:
                return 'Stop'
            
            # PURSUE if invader visible
            if invasores:
                return self.perseguir(game_state, acciones, invasores)
            
            # PATROL by default
            return self.patrullar(game_state, acciones)
        
        except Exception as e:
            print(f"ERROR defensive: {e}")
            return random.choice(acciones) if acciones else 'Stop'
    
    def perseguir(self, game_state, acciones, invasores):
        """Pursue nearest invader"""
        mi_pos = game_state.get_agent_state(self.index).get_position()
        
        # Nearest invader
        objetivo = min(invasores, key=lambda i: self.get_maze_distance(mi_pos, i.get_position()))
        
        # Action that gets closer
        mejor_accion = None
        mejor_dist = float('inf')
        
        for accion in acciones:
            sucesor = self.get_successor(game_state, accion)
            pos_sig = sucesor.get_agent_state(self.index).get_position()
            
            dist = self.get_maze_distance(pos_sig, objetivo.get_position())
            
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else random.choice(acciones)
    
    def patrullar(self, game_state, acciones):
        """Cycle through patrol points"""
        mi_pos = game_state.get_agent_state(self.index).get_position()
        objetivo = self.patrulla[self.idx_patrulla]
        
        # Change target if arrived
        if self.get_maze_distance(mi_pos, objetivo) <= 2:
            self.idx_patrulla = (self.idx_patrulla + 1) % len(self.patrulla)
            objetivo = self.patrulla[self.idx_patrulla]
        
        # Go to target
        mejor_accion = None
        mejor_dist = float('inf')
        
        for accion in acciones:
            sucesor = self.get_successor(game_state, accion)
            pos_sig = sucesor.get_agent_state(self.index).get_position()
            
            dist = self.get_maze_distance(pos_sig, objetivo)
            
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else random.choice(acciones)
    
    def get_successor(self, game_state, action):
        """Helper: generate successor state"""
        return game_state.generate_successor(self.index, action)
