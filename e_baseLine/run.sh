#!/usr/bin/env bash

for i in {0..10}; do
    python -c "from e1_relationshipCount import run; run($i)" &
done
