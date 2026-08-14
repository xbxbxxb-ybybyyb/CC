# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import argparse

import matplotlib.pyplot as plt

from exp.exp_forecasting import ExpForecasting


def main():
    train_mse_losses = []
    valid_mse_losses = []
    train_mae_losses = []
    valid_mae_losses = []

    for epoch in range(args.epochs):
        train_loss_mse, train_loss_mae = exp.train()
        valid_loss_mse, valid_loss_mae = exp.validate()

        train_mse_losses.append(train_loss_mse)
        valid_mse_losses.append(valid_loss_mse)
        train_mae_losses.append(train_loss_mae)
        valid_mae_losses.append(valid_loss_mae)
        print(f'Epoch: {epoch + 1:02}, Train MSELoss: {train_loss_mse:.5f}, Train MAELoss: {train_loss_mae:.3f}, Val. MSELoss: {valid_loss_mse:.5f}, Val. MAELoss: {valid_loss_mae:.3f}')

    plt.figure(figsize=(10, 5))
    plt.plot(train_mse_losses, label='Training Loss')
    plt.plot(valid_mse_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('MSELoss')
    plt.title('Training and Validation Loss over Epochs')
    plt.legend()
    plt.grid(True)
    plt.show()


#  预测函数调入


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TimesNet')
    parser.add_argument('--model', type=str, default='LSTM', choices=['LSTM', 'GRU', 'CNN', 'Transformer'])
    parser.add_argument('--input_dim', type=int, default=4, help='input dimension')
    parser.add_argument('--hidden_dim', type=int, default=64, help='hidden dimension')
    parser.add_argument('--num_layers', type=int, default=1, help='number of layers')
    parser.add_argument('--output_dim', type=int, default=1, help='output dimension')
    parser.add_argument('--lr', type=float, default=0.0001, help='learning rate')
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--num_workers', type=int, default=0)
    parser.add_argument('--epochs', type=int, default=100)

    args = parser.parse_args()

    exp = ExpForecasting(args=args)

    main()
