#! /bin/sh

# 2 common options. You can leave these alone:-
#$ -j y
#$ -cwd
#$ -m e
#$ -M ckhan.2015@phdis.smu.edu.sg
##$ -q "express.q"
##$ -q "short.q"
#$ -q "long.q"


processorID=$1

source ~/.bashrc
cd /scratch/ckhan.2015/community_detection/e_baseLine


python -c "from e3_baselineTripWP import run; run($processorID, 64)"