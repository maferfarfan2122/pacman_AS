# Pacman Contest - Team pacmanAS

**Course:** Autonomous Systems 2026 | **Institution:** Universitat Pompeu Fabra  (MISS) 
**Team:** María Fernanda Farfán (u235590), Tiago de Oliveira Amaral (u269310)

## Project Description

This repository implements a two-agent team for the Pacman Capture-the-Flag tournament. The offensive agent uses a finite state machine with three states (ATTACK, RETURN, ESCAPE) for food collection and safe return, while the defensive agent patrols territory and pursues invaders. Both agents use greedy pathfinding with maze distance calculations and include exception handling to prevent timeouts

Local testing validates functionality with three test matches against baseline agents, achieving consistent victories. The implementation applies planning concepts from Problem Set 4, adapting A* search principles and heuristic evaluation for real-time decision-making under time constraints (1 second per action, 15 seconds initialization)
