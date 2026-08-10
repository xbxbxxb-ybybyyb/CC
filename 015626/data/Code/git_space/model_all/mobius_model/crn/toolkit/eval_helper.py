import os
import pandas as pd
from config.base import root
from framework.utils import load_pickle, save_pickle


def merge_signal(identifier, update_date_list, return_time_list, random_seed_list):
    output_root = os.path.join(root, 'signal', identifier)
    os.makedirs(output_root, exist_ok=True)

    update_date_list.sort()
    for return_time in return_time_list:
        fragments = []
        for i, update_date in enumerate(update_date_list):
            prediction_all = {}
            for random_seed in random_seed_list:
                home = os.path.join(root, 'model', 'model_prod', identifier, update_date, 'time_{}'.format(return_time), 'seed_{}'.format(random_seed))
                for k in range(5):
                    prediction_path = os.path.join(home, 'prediction.{}.pkl'.format(k))
                    prediction = load_pickle(prediction_path)
                    prediction_all['{}_{}'.format(random_seed, k)] = prediction
            prediction_all = pd.DataFrame(prediction_all)
            prediction_avg = prediction_all.mean(axis=1)
            if i + 1 < len(update_date_list):
                str_date = (pd.Timestamp(update_date) + pd.Timedelta(days=1)).strftime('%Y%m%d')
                end_date = update_date_list[i + 1]
            else:
                str_date = (pd.Timestamp(update_date) + pd.Timedelta(days=1)).strftime('%Y%m%d')
                end_date = prediction_avg.index[-1].strftime('%Y%m%d')
            prediction_cut = prediction_avg[str_date:end_date]
            fragments.append(prediction_cut)
        signal = pd.concat(fragments, axis=0)
        suffix = str(return_time) + '.' + ''.join([str(random_seed) for random_seed in random_seed_list])
        signal_name = '{}.{}'.format(identifier, suffix)
        signal.name = signal_name

        output_path = os.path.join(output_root, '{}.pkl'.format(signal_name))
        print('save signal to {}'.format(output_path), flush=True)
        save_pickle(signal, output_path)
    return None
