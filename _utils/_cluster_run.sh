#! /bin/sh

# 2 common options. You can leave these alone:-
#$ -j y
#$ -cwd
#$ -m e
#$ -M ckhan.2015@phdis.smu.edu.sg
##$ -q "express.q"
##$ -q "short.q"
#$ -q "long.q"


source ~/.bashrc
cd /scratch/ckhan.2015/community_detection/_utils

python -c "from geoFunctions import get_sgPoints; get_sgPoints()"
