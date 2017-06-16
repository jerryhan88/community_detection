#!/usr/bin/env bash
for i in {0..63}; do
    qsub _cluster_run.sh $i
done

#for i in {24..47}; do
#    qsub _cluster_run.sh $i
#done
#
#
#
#for i in {48..75}; do
#    qsub _cluster_run.sh $i
#done
#
#for i in {76..109}; do
#    qsub _cluster_run.sh $i
#done