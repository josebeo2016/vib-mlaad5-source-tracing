# VIB-based Real Pre-emphasis Audio Deepfake Source Tracing

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