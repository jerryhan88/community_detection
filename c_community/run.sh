#!/usr/bin/env bash

for i in {0..10}; do
    python -c "from c1_communityProdDuration import run; run($i)" &
done
