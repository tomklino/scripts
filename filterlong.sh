#!/bin/bash

max=${1:-80}

awk "{if (length(\$0) < $max){print \$0}}"
