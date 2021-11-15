#!/bin/bash
# Copyright (c) 2018-2019 Terry Greeniaus.
# All rights reserved.

# Helper script to iterate through all "edit" commits in
# an interactive rebase and build them testing for build
# and unittest successes.  It will stop on the first commit
# that fails or go until the rebase is complete.
while true; do
    make clean && make test && make -j || break
    git rebase --continue || break
done
