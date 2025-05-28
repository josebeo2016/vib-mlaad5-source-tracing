# VIB-based Real Pre-emphasis Audio Deepfake Source Tracing
(Accepted to ISCA Interspeech 2025)

The rise of audio deepfakes presents significant challenges, necessitating effective detection and attribution mechanisms for fabricated speech. This paper addresses the need to identify not only fake speech but also its origins. We develop the audio deepfake source tracing method as follows: First, we establish a protocol using the MLAAD v5 dataset to analyze the acoustic and vocoder processing involved in generating fake speech. Second, we introduce a novel real pre-emphasis method based on the VIB architecture for audio deepfake source tracing. Our evaluation demonstrates that our model outperforms baseline systems, achieving enhancements of 10%. Our approach significantly improves model generalization and reduces complexity while preserving the real pre-emphasis effect established by the baseline.

## Dataset preparation
- Please download the [MLAAD v5](https://deepfake-total.com/sourcetracing) dataset, unzip and place the `fake` directory of MLAAD v5 into `mlaad_v5`.
- For Common Voice dataset, you can freely use any language subsets (recommended to use at least 5 langauges). Then following the `mlaad_v5/0_preprocess.ipynb` to make your own data protocol.
## Setting environment
```
bash 0_envsetup.sh
```
## Training
```
CUDA_VISIBLE_DEVICES=0 python train_ST.py --config configs/ST_2stage_augall_wav2vec2_vib_gelu_sclnormal.yaml  --database_path ./mlaad_v5  --batch_size 1 --padding_type "repeat" --max_lr 1e-4 --min_lr 1e-6 --comment "ST_2stage_augall_wav2vec2_vib_sclnormal_0.1CE_mlaad_vocoder_stage1_verify" --num_epochs 80
```