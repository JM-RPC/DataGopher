#!/bin/zsh
source activate condaloess
SCRIPT_DIR=$(dirname $(readlink -f $0))
echo $SCRIPT_DIR
conda activate condaloess
python "$SCRIPT_DIR/srcnew/DataGopher.py"