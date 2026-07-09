#!/bin/bash
#Note that tmp/tmp.O0sv4yJ9D8 is a directory created by mktemp -d, you'll need to replace this with your own temporary directory


touch /tmp/tmp.O0sv4yJ9D8/ran.log #Creates a log file when the script runs, just to verify it has
cat /etc/bandit_pass/bandit24 > /tmp/tmp.O0sv4yJ9D8/password.txt 2>/tmp/tmp.O0sv4yJ9D8/error.txt #Dumps the password into password.txt, and any errors into error.txt
