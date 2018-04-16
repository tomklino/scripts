#!/bin/bash

max=${1:-160}

awk "{if (length(\$0) < $max){print \$0}}"
