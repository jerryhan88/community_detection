#!/usr/bin/env bash

#for i in {0..10}; do
#    python -c "from b0_individualCounting import run; run($i)" &
#done

#for i in {0..10}; do
#    python -c "from b1_individualRelation import run; run($i)" &
#done

for i in {0..10}; do
    python -c "from b1_individualRelationF import run; run($i)" &
done