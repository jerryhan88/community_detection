#!/usr/bin/env bash
for i in 0{1..9} {10..12}; do
    qsub _cluster_run.sh $i
done
