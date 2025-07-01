md2tex=$(realpath ../md2tex.py)
md2ch=$(realpath ../md2ch.py)
run=$(realpath ../run.sh)
preamble=$(realpath ../preamble.tex)
preamble_slide=$(realpath ../preamble_slide.tex)
preamble_report=$(realpath ../preamble_report.tex)
content_gen=$(realpath ../content_gen.py)
Makefile=$(realpath ../Makefile)
# report=$(realpath ../report.tex)

# synbolic link to Makefile
[ ! -f Makefile ] && ln -s "$Makefile" ./Makefile

# symbolic link to run.sh
[ ! -f run.sh ] && ln -s "$run" ./run.sh

# symbolic link to preamble.tex
[ ! -f preamble.tex ] && ln -s "$preamble" ./preamble.tex
[ ! -f preamble_report.tex ] && ln -s "$preamble_report" ./preamble_report.tex

# directories
mkdir -p Logs
mkdir -p MdFiles
mkdir -p TeXFiles
mkdir -p CheatSheets
mkdir -p Assets/Codes
mkdir -p Assets/Images
mkdir -p Assets/Books

# do not overrides current file
cp --update=none ../master.tex .
cp --update=none ../.gitignore .
cp --update=none ../report.tex .

# content_gen.py
[ ! -f content_gen.py ] && ln -s "$content_gen" ./content_gen.py

# MdFiles directory config
cd MdFiles
# symbolic link to md2tex.py
[ ! -f md2tex.py ] && ln -s "$md2tex" ./md2tex.py

# CheatSheets directory config
cd ../CheatSheets
# symbolic link to md2ch.py
[ ! -f md2ch.py ] && ln -s "$md2ch" ./md2ch.py
cp --update=none ../../cheatsheet.tex .
