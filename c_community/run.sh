#!/usr/bin/env bash

for i in {0..10}; do
    python -c "from c2_communityStatistics import run; run($i)" &
done
