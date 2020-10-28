#!/bin/bash

ROOT_DIR=${1}
NUM_PROCESS=${2}
OPTI_DIR=${3}

python ReorientAndExtract.py -i ${ROOT_DIR}

parallel -j ${NUM_PROCESS} fslreorient2std ::::+ ${ROOT_DIR}/T1ReorientInput.txt ::::+ ${ROOT_DIR}/T1ExtractInput.txt
parallel -j ${NUM_PROCESS} fslreorient2std ::::+ ${ROOT_DIR}/BOLDReorientInput.txt ::::+ ${ROOT_DIR}/BOLDExtractInput.txt

parallel -j ${NUM_PROCESS} bash ${OPTI_DIR} -i :::: ${ROOT_DIR}/T1ExtractInput.txt

rm ${ROOT_DIR}/T1ExtractInput.txt

rm ${ROOT_DIR}/T1ReorientInput.txt

rm ${ROOT_DIR}/BOLDReorientInput.txt
rm ${ROOT_DIR}/BOLDExtractInput.txt
