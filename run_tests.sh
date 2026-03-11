#!/bin/bash
# Test script for team pacmanAS
# Runs validation matches and saves logs

set -e

# Dynamic path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEST_DIR="$(cd "$SCRIPT_DIR/../pacman-agent/pacman-contest/src/contest" && pwd)"
LOG_DIR="$SCRIPT_DIR/test_logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Configuration
TEAM_FILE="pacman_AS.py"
BASELINE="baseline_team"
NUM_TESTS=3

mkdir -p "$LOG_DIR"

echo "╔════════════════════════════════════════╗"
echo "║  Pacman Contest - Team pacmanAS Test   ║"
echo "╚════════════════════════════════════════╝"
echo ""

cd "$CONTEST_DIR"

# Run tests
RESULTS=()
for i in $(seq 1 $NUM_TESTS); do
    echo "Test $i/$NUM_TESTS..."
    LOG_FILE="$LOG_DIR/test_${i}_${TIMESTAMP}.log"
    
    python capture.py -r "agents/pacmanAS/$TEAM_FILE" -b "$BASELINE" -q > "$LOG_FILE" 2>&1
    
    # Extract score from log
    if grep -q "The Red team wins" "$LOG_FILE"; then
        SCORE=$(grep "The Red team wins" "$LOG_FILE" | grep -oE "[0-9]+" | head -1)
        RESULTS+=("$SCORE")
        echo "  ✓ Win (+${SCORE})"
    elif grep -q "The Blue team wins" "$LOG_FILE"; then
        SCORE=$(grep "The Blue team wins" "$LOG_FILE" | grep -oE "[0-9]+" | head -1)
        RESULTS+=("-$SCORE")
        echo "  ✗ Loss (-${SCORE})"
    elif grep -q "Tie game" "$LOG_FILE"; then
        RESULTS+=("0")
        echo "  - Tie (0)"
    else
        RESULTS+=("")
        echo "  Error: Check logs"
    fi
done

# Generate summary
SUMMARY_FILE="$LOG_DIR/summary_${TIMESTAMP}.txt"

{
    echo "════════════════════════════════════════"
    echo "Test Summary - Team pacmanAS"
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "════════════════════════════════════════"
    echo ""
    
    TOTAL=0
    WINS=0
    LOSSES=0
    TIES=0
    
    for i in $(seq 0 $((NUM_TESTS - 1))); do
        SCORE="${RESULTS[$i]}"
        TEST_NUM=$((i + 1))
        
        if [ -n "$SCORE" ]; then
            if [ "$SCORE" -gt 0 ]; then
                echo "Test $TEST_NUM: Win (+${SCORE})"
                TOTAL=$((TOTAL + SCORE))
                WINS=$((WINS + 1))
            elif [ "$SCORE" -lt 0 ]; then
                echo "Test $TEST_NUM: Loss (${SCORE})"
                TOTAL=$((TOTAL + SCORE))
                LOSSES=$((LOSSES + 1))
            else
                echo "Test $TEST_NUM: Tie (0)"
                TIES=$((TIES + 1))
            fi
        else
            echo "Test $TEST_NUM: Error"
        fi
    done
    
    echo ""
    echo "────────────────────────────────────────"
    echo "Results: $WINS wins / $LOSSES losses / $TIES ties"
    if [ $NUM_TESTS -gt 0 ]; then
        AVG=$((TOTAL / NUM_TESTS))
        echo "Average Score: ${AVG}"
    fi
    echo "════════════════════════════════════════"
} > "$SUMMARY_FILE"

cat "$SUMMARY_FILE"
echo ""
echo "Logs saved: test_logs/"
