"""
myTeam.py - Test Run 11 Marzo 2026
Equipo: pacmanAS
Basado en conceptos de Problem Set 4: A*, heuristics, planning
"""

from contest.capture_agents import CaptureAgent
import random

def create_team(first_index, second_index, is_red,
                first='AgenteOfensivo', second='AgenteDefensivo'):
    """
    Factory function requerida.
    Retorna lista con 2 agentes: ofensivo y defensivo.
    """
    return [eval(first)(first_index), eval(second)(second_index)]


class AgenteOfensivo(CaptureAgent):
    """
    AGENTE OFENSIVO: Captura comida enemiga
    Estados: ATACAR → REGRESAR → ESCAPAR
    """
    
    def register_initial_state(self, game_state):
        """Inicialización (max 15 segundos)"""
        CaptureAgent.register_initial_state(self, game_state)
        self.start = game_state.get_agent_position(self.index)
        
        # Calcular frontera (mitad del mapa)
        if self.red:
            self.frontera_x = game_state.data.layout.width // 2 - 1
        else:
            self.frontera_x = game_state.data.layout.width // 2
        
        print(f"[OFENSIVO {self.index}] Listo en {self.start}")
    
    def choose_action(self, game_state):
        """Decisión de acción (max 1 segundo)"""
        try:
            mi_estado = game_state.get_agent_state(self.index)
            mi_pos = mi_estado.get_position()
            comida_llevando = mi_estado.num_carrying
            
            # Obtener acciones legales
            acciones = game_state.get_legal_actions(self.index)
            if 'Stop' in acciones:
                acciones.remove('Stop')
            
            if not acciones:
                return 'Stop'
            
            # Detectar fantasmas enemigos
            enemigos = [game_state.get_agent_state(i) for i in self.get_opponents(game_state)]
            fantasmas = [e for e in enemigos if not e.is_pacman and e.get_position() is not None]
            
            # DECISIÓN: ¿Qué hacer?
            if fantasmas:
                dist_min_fantasma = min(self.get_maze_distance(mi_pos, f.get_position()) for f in fantasmas)
                
                # ESCAPAR si fantasma muy cerca
                if dist_min_fantasma <= 3:
                    return self.escapar(game_state, acciones, fantasmas)
            
            # REGRESAR si llevas 5+ comida
            if comida_llevando >= 5:
                return self.regresar(game_state, acciones)
            
            # ATACAR por defecto
            return self.atacar(game_state, acciones)
        
        except Exception as e:
            print(f"ERROR ofensivo: {e}")
            return random.choice(acciones) if acciones else 'Stop'
    
    def atacar(self, game_state, acciones):
        """Buscar comida más cercana (A* simplificado)"""
        mi_pos = game_state.get_agent_state(self.index).get_position()
        comida = self.get_food(game_state).as_list()
        
        if not comida:
            return random.choice(acciones)
        
        # Evaluar cada acción
        mejor_accion = None
        mejor_dist = float('inf')
        
        for accion in acciones:
            sucesor = self.get_successor(game_state, accion)
            pos_sig = sucesor.get_agent_state(self.index).get_position()
            
            # Heurística: distancia a comida más cercana
            dist = min(self.get_maze_distance(pos_sig, c) for c in comida)
            
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else random.choice(acciones)
    
    def regresar(self, game_state, acciones):
        """Regresar a casa para depositar comida"""
        mi_pos = game_state.get_agent_state(self.index).get_position()
        walls = game_state.get_walls()
        altura = walls.height
        
        # Puntos de frontera (territorio propio)
        frontera = [(self.frontera_x, y) for y in range(altura) if not walls[self.frontera_x][y]]
        
        if not frontera:
            return random.choice(acciones)
        
        # Ir al punto de frontera más cercano
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
        """Maximizar distancia a fantasmas"""
        mejor_accion = None
        mejor_dist = -1
        
        for accion in acciones:
            sucesor = self.get_successor(game_state, accion)
            pos_sig = sucesor.get_agent_state(self.index).get_position()
            
            # Distancia mínima a fantasmas
            dist_min = min(self.get_maze_distance(pos_sig, f.get_position()) for f in fantasmas)
            
            if dist_min > mejor_dist:
                mejor_dist = dist_min
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else random.choice(acciones)
    
    def get_successor(self, game_state, action):
        """Helper: generar sucesor"""
        return game_state.generate_successor(self.index, action)


class AgenteDefensivo(CaptureAgent):
    """
    AGENTE DEFENSIVO: Protege territorio
    Estados: PATRULLAR → PERSEGUIR
    """
    
    def register_initial_state(self, game_state):
        """Inicialización"""
        CaptureAgent.register_initial_state(self, game_state)
        self.start = game_state.get_agent_position(self.index)
        
        # Calcular puntos de patrulla
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
        print(f"[DEFENSIVO {self.index}] Patrulla: {len(self.patrulla)} puntos")
    
    def choose_action(self, game_state):
        """Decisión defensiva"""
        try:
            mi_pos = game_state.get_agent_state(self.index).get_position()
            
            # Detectar invasores
            enemigos = [game_state.get_agent_state(i) for i in self.get_opponents(game_state)]
            invasores = [e for e in enemigos if e.is_pacman and e.get_position() is not None]
            
            acciones = game_state.get_legal_actions(self.index)
            if 'Stop' in acciones:
                acciones.remove('Stop')
            
            if not acciones:
                return 'Stop'
            
            # PERSEGUIR si hay invasor visible
            if invasores:
                return self.perseguir(game_state, acciones, invasores)
            
            # PATRULLAR por defecto
            return self.patrullar(game_state, acciones)
        
        except Exception as e:
            print(f"ERROR defensivo: {e}")
            return random.choice(acciones) if acciones else 'Stop'
    
    def perseguir(self, game_state, acciones, invasores):
        """Perseguir invasor más cercano"""
        mi_pos = game_state.get_agent_state(self.index).get_position()
        
        # Invasor más cercano
        objetivo = min(invasores, key=lambda i: self.get_maze_distance(mi_pos, i.get_position()))
        
        # Acción que acerca más
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
        """Ciclar entre puntos de patrulla"""
        mi_pos = game_state.get_agent_state(self.index).get_position()
        objetivo = self.patrulla[self.idx_patrulla]
        
        # Cambiar objetivo si llegamos
        if self.get_maze_distance(mi_pos, objetivo) <= 2:
            self.idx_patrulla = (self.idx_patrulla + 1) % len(self.patrulla)
            objetivo = self.patrulla[self.idx_patrulla]
        
        # Ir al objetivo
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
        """Helper: generar sucesor"""
        return game_state.generate_successor(self.index, action)
