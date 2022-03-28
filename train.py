import sys
from collections import defaultdict
import os
import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from utils import num_params, test_accuracy, pretty_plot
from datasets import get_dataset

from models import get_model

import argparse

number_workers = 16

os.makedirs('models', exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', default='CIFAR10')
parser.add_argument(
    '--network',
    # choices=['resnet18', 'resnet34'],
    default='Resnet18')
parser.add_argument('--ckpt', default='auto',
                    help='Model checkpoint for saving/loading.')
parser.add_argument('--device', default='cuda:0')
parser.add_argument('--num_epochs', type=int, default=5,
                    help='Number of training epochs.')
parser.add_argument('--lr', type=float, default=0.01, help='learning rate')
parser.add_argument('--batch_size', type=int, default=64, help='batch size')
parser.add_argument('--reset', action='store_true')
parser.add_argument('--save_best', action='store_true',
                    help='Save only the best models (measured in valid accuracy).')

if 'ipykernel' in sys.argv[0]:
    args = parser.parse_args([
        '--dataset', 'CIFAR10'
    ])
else:
    args = parser.parse_args()

device = args.device

if args.ckpt == 'auto':
    args.ckpt = f'models/{args.dataset}_{args.network}.ckpt'

plot_loc = args.ckpt.split('.')[0] + '.png'
log_loc = args.ckpt.split('.')[0] + '.txt'


def log(msg):
    print(msg)
    with open(log_loc, 'a') as f:
        f.write(msg + '\n')


torch.manual_seed(4)

dataset = get_dataset(args.dataset)
train_loader = DataLoader(
    dataset.train_set, batch_size=args.batch_size, shuffle=True, num_workers=number_workers)
valid_loader = DataLoader(
    dataset.valid_set, batch_size=args.batch_size, shuffle=False, num_workers=number_workers)
test_loader = DataLoader(
    dataset.test_set, batch_size=args.batch_size, shuffle=False, num_workers=number_workers)

in_channels = dataset.in_channels
num_classes = dataset.num_classes


##################################### Train Model #####################################

# print(dataset.classes)
# print(dataset.class_labels)

loss_fn = nn.CrossEntropyLoss()

if os.path.exists(args.ckpt) and not args.reset:
    state_dict = torch.load(args.ckpt, map_location=device)
    model = state_dict['model']
    optimizer = state_dict['optimizer']
    init_epoch = state_dict['epoch']
    logs = state_dict['logs']
    best_acc = state_dict['acc']
    log(f"Loading model {args.ckpt} ({init_epoch} epochs), valid acc {best_acc:.3f}")
else:
    init_epoch = 0
    best_acc = 0
    logs = defaultdict(list)

    model = get_model(args.network, in_channels, num_classes)
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    if os.path.exists(log_loc):
        os.remove(log_loc)

valid_acc = test_accuracy(model, valid_loader, name='valid', device=device)


log('\n' + '\n'.join(f'{k}={v}' for k, v in vars(args).items()) + '\n')

log('Training ' f'{model.__class__.__name__}, '
    f'params:\t{num_params(model) / 1000:.2f} K')

for epoch in range(init_epoch, args.num_epochs):
    model.train()
    step_start = epoch * len(train_loader)
    for step, (x, y) in enumerate(train_loader, start=step_start):
        x, y = x.to(device), y.to(device)

        logits = model(x)
        loss = loss_fn(logits, y)

        acc = (logits.argmax(dim=1) == y).float().mean().item()

        metrics = {'acc': acc, 'loss': loss.item()}
        for m, v in metrics.items():
            logs[m].append(v)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if step % len(train_loader) % 50 == 0:
            log(f'[{epoch}/{args.num_epochs}:{step % len(train_loader):3d}] '
                + ', '.join([f'{k} {v:.3f}' for k, v in metrics.items()]))

    model.eval()
    valid_acc_old = valid_acc
    valid_acc = test_accuracy(
        model, valid_loader, name='valid', device=device)
    interpolate_valid_acc = torch.linspace(
        valid_acc_old, valid_acc, steps=len(train_loader)).tolist()
    logs['val_acc'].extend(interpolate_valid_acc)

    if not args.save_best or valid_acc > best_acc:
        pretty_plot(logs, steps_per_epoch=len(train_loader),
                    smoothing=500, save_loc=plot_loc)
        best_acc = valid_acc

        log(f'Saving model to {args.ckpt}')
        torch.save({'model': model, 'optimizer': optimizer, 'epoch': epoch + 1,
                    'acc': best_acc, 'logs': logs, 'input_shape': dataset.input_shape, 'classes': dataset.classes}, args.ckpt)


# torch.save({'model': model, 'optimizer': optimizer, 'epoch': init_epoch,
#             'acc': best_acc, 'logs': logs, 'input_shape': dataset.input_shape, 'classes': dataset.classes}, args.ckpt)

# pretty_plot(logs, smoothing=50)
