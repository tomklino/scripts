#!/bin/bash

until xhost +si:localuser:$USER; do sleep 1; done

