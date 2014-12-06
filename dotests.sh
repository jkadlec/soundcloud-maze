#!/bin/bash

trap "kill 0" SIGINT SIGTERM EXIT

python3 -m unittest tests/*.py && echo "unit tests passed" || echo "unit tests failed"

echo "functional tests:"

python3 main.py -c maze.conf &

export totalEvents=10000

./followermaze.sh &> /dev/null && echo "case '10000 msg' passed" || "case '10000 msg' failed"

export totalEvents=100000

./followermaze.sh &> /dev/null && echo "case '100000 msg' passed" || "case '100000 msg' failed"

export totalEvents=50000
export concurrencyLevel=768

./followermaze.sh &> /dev/null && echo "case '768 users' passed" || "case '5000 users' failed"

export maxEventSourceBatchSize=10000

./followermaze.sh &> /dev/null && echo "case '10000 batchsize' passed" || "case '10000 batchsize' failed"
