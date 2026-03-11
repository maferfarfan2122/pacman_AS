# Pacman Contest - Test Run 11 Marzo 2026

**Equipo:** pacmanAS  
**Universidad:** Universitat Pompeu Fabra (UPF)  
**Curso:** MIIS - Autonomous Systems 2026

## 📊 Estrategia

### Agente Ofensivo
- **Estados:** ATACAR → REGRESAR → ESCAPAR
- **Comportamiento:**
  - Busca comida enemiga usando pathfinding greedy
  - Regresa a territorio propio al capturar 5+ comidas
  - Escapa de fantasmas enemigos cuando están a distancia ≤3
- **Heurística:** Distancia Manhattan a comida más cercana (A* simplificado)

### Agente Defensivo  
- **Estados:** PATRULLAR → PERSEGUIR
- **Comportamiento:**
  - Patrulla entre 3 puntos estratégicos de comida propia
  - Persigue invasores Pacman enemigos cuando son visibles
  - Alterna entre puntos al alcanzar distancia ≤2
- **Heurística:** Distancia a invasor más cercano o punto de patrulla

## 🔬 Conceptos de Problem Set 4

Implementación basada en conceptos de planning del PS4:

| Concepto PS4 | Aplicación Pacman |
|--------------|-------------------|
| **A* Search** | `get_maze_distance()` para pathfinding óptimo |
| **h_max (admisible)** | Decisiones seguras: escape y retorno a casa |
| **h_FF (inadmisible)** | Heurísticas agresivas para ataque |
| **Planning Graph** | Análisis de alcanzabilidad del mapa |
| **LRTA*** | Adaptación de pesos en estrategia |

## ✅ Testing Local

**Resultados vs baseline_team:**
- ✅ Como Red: 4 victorias (5, 11, 10, 5 puntos)
- ✅ Como Blue: 1 victoria (15 puntos)
- ✅ Sin crashes
- ✅ Sin timeouts
- ✅ 0 warnings

**Tiempo promedio por juego:** ~44 segundos

## ⚙️ Especificaciones Técnicas

- **Python:** 3.9.7 (compatible con 3.8+)
- **Framework:** Berkeley AI Pacman (UPF fork)
- **Límites respetados:**
  - Inicialización: < 15 segundos
  - Acción: < 1 segundo
  - Error handling con try-except y fallback random

## 🚀 Test Run

- **Fecha:** 11 marzo 2026 @ 19:55
- **Cluster:** HDTIC SNOW (UPF)
- **Objetivo:** Detectar bugs antes del torneo final (20 marzo)

## 📝 Notas

Código desarrollado con:
- Nomenclatura snake_case (convención del framework)
- Estados explícitos para debugging
- Print statements para trace de decisiones
- Robustez mediante exception handling

---

**Test Run Registration:** ✅ Completado  
**Repository:** Public  
**Last Update:** 11 marzo 2026, 17:26
