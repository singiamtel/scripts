#!/usr/bin/env bash
exec awk '{ print $4; }' "$*"
