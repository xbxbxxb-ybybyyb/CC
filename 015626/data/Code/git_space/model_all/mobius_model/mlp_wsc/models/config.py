import torch.nn as nn
from models.networks.dnn import DNN


model_mapping = {
    'dnn': DNN,
}


loss_mapping = {
    'regression': nn.MSELoss,
    'binary': nn.BCEWithLogitsLoss,
}
