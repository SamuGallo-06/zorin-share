#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  pkexec python3 main.py "$@"
  exit
fi
else
  python3 main.py "$@"
fi