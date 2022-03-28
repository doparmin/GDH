
# for f_st in 1e-10 1e-9 1e-8 1e-7 1e-6 1e-4 1e-3 0
#     do
#     python invert.py \
#     --model models/Cytomorphology-4x_Resnet34.ckpt \
#     --lr 0.1 \
#     --f_stats $f_st \
#     --f_reg 1e-5 \
#     --batch_size 64 \
#     --num_epochs 5000 \

#     # --reset
# done

for a in 1...10
do
    for f_st in 1e-10 1e-9 1e-8 1e-7 1e-6 0
        do
        python invert.py \
        --model models/Cytomorphology-4x_Resnet34.ckpt \
        --lr 0.1 \
        --f_stats $f_st \
        --f_reg 0 \
        --batch_size 64 \
        --num_epochs 5000 \
        --unsupervised

        # --reset
    done
done