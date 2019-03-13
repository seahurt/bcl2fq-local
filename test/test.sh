#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
BASE=$(dirname $DIR)
python $BASE/bcl2fq/bcl2fq.py -i $DIR -o $DIR --cmd-only
