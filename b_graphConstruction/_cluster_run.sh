#! /bin/sh

# 2 common options. You can leave these alone:-
#$ -j y
#$ -cwd
#$ -m e
#$ -M ckhan.2015@phdis.smu.edu.sg
##$ -q "express.q"
#$ -q "short.q"
##$ -q "long.q"


processorID=$1

source ~/.bashrc
cd /scratch/ckhan.2015/community_detection/a_dataProcessing

python -c "from b1_individualRelationF import run; run($processorID)"
