#!/bin/bash
# Name of the conda environment
ENVNAME=vib

eval "$(conda shell.bash hook)"
conda activate ${ENVNAME}
retVal=$?
if [ $retVal -ne 0 ]; then
    echo "Install conda environment ${ENVNAME}"
    
    # conda env
    conda create -n ${ENVNAME} python=3.9 pip --yes
    conda activate ${ENVNAME}
    echo "===========Install pytorch==========="
    pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu118

    # install scipy
    pip install scipy==1.11.4

    # install pandas
    pip install pandas==1.3.5

    # install protobuf
    pip install protobuf==3.20.3

    # install tensorboard
    pip install tensorboard==2.6.0
    pip install tensorboardX==2.6

    # install librosa
    pip install librosa==0.10.0

    # install pydub
    pip install pydub==0.25.1

    # install pyyaml
    pip install pyyaml

    # install tqdm
    pip install tqdm

    # install asteroid-filterbanks
    pip install asteroid-filterbanks

    # install einops
    pip install einops

    # install speechbrain
    pip install speechbrain

    # install torchinfo
    pip install torchinfo

    # install accelerate
    pip install accelerate

    # install datasets
    pip install datasets
    
    # install transformer
    pip install transformers

    # install matplotlib
    pip install matplotlib==3.7.3
    
else
    echo "Conda environment ${ENVNAME} has been installed"
fi