#!/bin/bash

THE_WORK_DIR="../../Archive/Works/"

# time duration
get_time() {
    echo $(date +%s%3N)
}
calc_duration() {
    start=$1
    end=$2
    name=$3
    duration=$(echo "scale=3; ($end - $start) / 1000" | bc)
    echo "[$3 Cost]: $duration seconds"
}

# Check for -m option
skip_compile=false
if [ "$1" == "-m" ]; then
    skip_compile=true
    shift
fi

if [ "$skip_compile" = false ]; then
    start_time=$(get_time)

    # Converting markdown to latex
    mdconv_start=$(get_time)
    rm TeXFiles/*
    cd MdFiles
    python3 md2tex.py
    cd ..
    mdconv_end=$(get_time)

    if [ "$1" == "cheat" ]; then
        if [ -d "CheatSheets" ]; then
            mdtoch_start=$(get_time)
            cd CheatSheets
            python3 md2ch.py
            cd ..
            xelatex -interaction=nonstopmode cheatsheet.tex > Logs/cheatsheet_compile.log 2>&1
            mdtoch_end=$(get_time)
        else
            echo "[Cheatsheets] No CheatSheets Dir found!"
        fi
    fi

    final_start=$(get_time)
    xelatex -interaction=nonstopmode master.tex > Logs/master_compile.log 2>&1
    zathura master.pdf & return
    xelatex -interaction=nonstopmode master.tex >> Logs/master_compile.log 2>&1
    final_end=$(get_time)

    # generating a markdown content
    python3 content_gen.py

    end_time=$(get_time)

    echo "============================================================"
    calc_duration $mdconv_start $mdconv_end "Markdown Convert to TeX"
    if [ "$1" == "cheat" ]; then
        calc_duration $mdtoch_start $mdtoch_end "CheatSheet Convert & Compiling"
    fi
    calc_duration $final_start $final_end "Main File Compiling"
    calc_duration $start_time $end_time "All"
    echo "Q.E.D."
    echo "============================================================"
fi

# Sync option, work with nutstore.
read -p "Move to TheWork? y/n: " move_choice
if [ "$move_choice" == "y" ]; then
    ls ${THE_WORK_DIR}
    read -p "Enter Name: " nameofpdf
    cp master.pdf "${THE_WORK_DIR}ZN-${nameofpdf}.pdf"
fi

if [ "$skip_compile" = false ]; then
    latexmk -c > Logs/latexmk_clean.log 2>&1
    echo "M O V E   F O R W A R D"
fi
