#!/bin/bash
exec awk '{ print $4; }' $*
