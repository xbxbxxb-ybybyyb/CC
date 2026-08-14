import torch
from torch import nn

from exp.exp_basic import ExpBasic
from data.data_loader import SupervisedTimeseriesDataset
from torch.utils.data import DataLoader


class ExpForecasting(ExpBasic):
    def __init__(self, args):
        super().__init__(args)

    def _build_model(self):
        model = self.model_dir[self.args.model](
            self.args.input_dim,
            self.args.hidden_dim,
            self.args.output_dim,
            self.args.num_layers
        ).float()
        return model

    def _get_data(self, flag):
        dataset = SupervisedTimeseriesDataset()
        if flag == 'train':
            subset = dataset.train_set
            batch_size = self.args.batch_size
            num_workers = self.args.num_workers
            shuffle = True

        elif flag == 'valid':
            subset = dataset.val_set
            batch_size = self.args.batch_size
            num_workers = self.args.num_workers
            shuffle = False

        elif flag == 'test':
            subset = dataset.test_set
            batch_size = self.args.batch_size
            num_workers = self.args.num_workers
            shuffle = False
        else:
            raise NotImplementedError

        return DataLoader(subset, batch_size=batch_size, num_workers=num_workers, shuffle=shuffle)

    def _select_optimizer(self):
        return torch.optim.Adam(self.model.parameters(), lr=self.args.lr)

    def _select_criterion(self, metric):
        if metric == 'mse':
            return nn.MSELoss().to(self.device)
        elif metric == 'mae':
            return nn.L1Loss().to(self.device)
        else:
            return nn.HuberLoss().to(self.device)

    def train(self):
        epoch_loss_mse = 0
        epoch_loss_mae = 0

        self.model.train()
        iterator = self._get_data('train')
        for batch_idx, (data, target) in enumerate(iterator):
            self._select_optimizer().zero_grad()
            data, target = data.to(self.device), target.to(self.device)
            output = self.model(data)
            mse_loss = self._select_criterion('mse')(output, target)
            mae_loss = self._select_criterion('mae')(output, target)
            combined_loss = mse_loss + mae_loss
            combined_loss.backward()
            self._select_optimizer().step()

            epoch_loss_mse += mse_loss.item()
            epoch_loss_mae += mae_loss.item()

        average_loss_mse = epoch_loss_mse / len(iterator)  # 计算平均损失
        average_loss_mae = epoch_loss_mae / len(iterator)

        return average_loss_mse, average_loss_mae

    def validate(self):
        epoch_loss_mse = 0
        epoch_loss_mae = 0

        self.model.eval()
        iterator = self._get_data('valid')
        with torch.no_grad():
            for batch_idx, (data, target) in enumerate(iterator):
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                mse_loss = self._select_criterion('mse')(output, target)
                mae_loss = self._select_criterion('mae')(output, target)

                epoch_loss_mse += mse_loss.item()
                epoch_loss_mae += mae_loss.item()

        average_loss_mse = epoch_loss_mse / len(iterator)
        average_loss_mae = epoch_loss_mae / len(iterator)

        return average_loss_mse, average_loss_mae

    def test(self):
        return self.validate()

    def predict(self):
        all_targets = []
        all_predictions = []

        self.model.eval()
        with torch.no_grad():
            for batch_idx, (data, target) in enumerate(self._get_data('test')):
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)

                all_targets.extend(target.numpy())
                all_predictions.extend(output.numpy())
        return all_targets, all_predictions

