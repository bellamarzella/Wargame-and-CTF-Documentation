#!/bin/bash
password="hVQMk3lJNsmQ7VF3ubyrNNBom7BOgVXv" #Level 24s password, replace if necessary
for i in {0..10000}; do
    padded_code=$(printf "%04d" $i) #Pad i with necessary number of 0s
    echo "$password $padded_code"
done | nc localhost 30002 | grep -v "Wrong!" #Return any string that doesn't include "Wrong!"