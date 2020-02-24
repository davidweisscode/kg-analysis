#!/bin/bash

if [[ -n "$@" ]]; then
    for arg in "$@" # Iterate over arguments
    do
        python3 build_graph.py "$arg" && python3 project_graph.py "$arg" && python3 compute_knc.py "$arg" && python3 analyze_knc.py "$arg"
    done
else
    echo "[Info] Please specify run config files as arguments"
fi
