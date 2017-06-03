#!/usr/bin/env bash

for i in 0{1..9} {10..12}; do
    python -c "from a2_dwellTimeNpriorPresence import process_month; process_month('09$i')" &
done


#python -c "from a3_driverTrip import run; run()" &

