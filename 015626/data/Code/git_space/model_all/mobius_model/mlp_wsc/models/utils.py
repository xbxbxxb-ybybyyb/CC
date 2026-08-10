import torch
import numpy as np
import torch.nn as nn
from torch.utils.data import DataLoader


def cpu_to_gpu(cpu_batch):
    gpu_batch = {}
    for key in cpu_batch.keys():
        gpu_batch[key] = cpu_batch[key].cuda()
    return gpu_batch


def model_train(dataloader, model, loss_function, optimizer, use_gpu=True):
    assert issubclass(type(dataloader), DataLoader)
    assert issubclass(type(model), nn.Module)
    model.train()
    train_loss = 0.0
    train_sample_num = 0
    for batch in dataloader:
        if use_gpu:
            batch = cpu_to_gpu(batch)
        inputs = batch['x']
        targets = batch['y_true']
        batch_size = inputs.shape[0]
        outputs = model(inputs)
        train_sample_num += batch_size
        loss = loss_function(outputs, targets)
        train_loss += loss.item() * batch_size
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
    train_loss = train_loss / train_sample_num
    return train_loss


def model_valid(dataloader, model, loss_function, use_gpu=True):
    assert issubclass(type(dataloader), DataLoader)
    assert issubclass(type(model), nn.Module)
    model.eval()
    valid_loss = 0.0
    valid_sample_num = 0
    y_true_list = []
    y_pred_list = []
    for batch in dataloader:
        if use_gpu:
            batch = cpu_to_gpu(batch)
        inputs = batch['x']
        targets = batch['y_true']
        batch_size = inputs.shape[0]
        with torch.no_grad():
            outputs = model(inputs)
        loss = loss_function(outputs, targets)
        valid_loss += loss.item() * batch_size
        valid_sample_num += batch_size
        y_true_list.append(targets.detach().cpu().numpy())
        y_pred_list.append(outputs.detach().cpu().numpy())
    valid_loss = valid_loss / valid_sample_num
    y_true = np.concatenate(y_true_list, axis=0)
    y_pred = np.concatenate(y_pred_list, axis=0)
    return y_true, y_pred, valid_loss


def model_predict(dataloader, model, use_gpu=True):
    assert issubclass(type(dataloader), DataLoader)
    assert issubclass(type(model), nn.Module)
    model.eval()
    y_pred_list = []
    for batch in dataloader:
        if use_gpu:
            batch = cpu_to_gpu(batch)
        with torch.no_grad():
            outputs = model(batch['x'])
        y_pred_list.append(outputs.detach().cpu().numpy())
    y_pred = np.concatenate(y_pred_list, axis=0)
    return y_pred
