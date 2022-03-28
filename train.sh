# export CUDA_VISIBLE_DEVICES=0

run='python -m IPython --no-banner --no-confirm-exit'

$run train.py -- \
--network Resnet34 \
--dataset Cytomorphology-4x \
--lr 0.01 \
--batch_size 64 \
--num_epochs 20 \
--save_best \

# $run train.py -- \
# --network Resnet34 \
# --dataset SVHN \
# --lr 0.01 \
# --num_epochs 5 \
# --save_best \

# for dataset in PBCBarcelona Cytomorphology-4x Cytomorphology-4x-PBC 
#     do

#     $run train.py -- \
#     --network Resnet34 \
#     --dataset $dataset \
#     --lr 0.01 \
#     --batch_size 64 \
#     --num_epochs 10 \
#     --save_best \

# done
