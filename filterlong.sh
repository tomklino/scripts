#!/bin/bash

max=${1:-80}

awk "{if (length(\$1) < $max){print \$1}}"
