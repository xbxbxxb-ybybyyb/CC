model_config = {
    'config_name': 'CRN_REG_v4',
    'export_name': 'crn_reg',

    'structure': 'CRN',
    'objective': 'MSE',

    'num_minutes': 237,
    'coefficient': 4,

    'window_size': 10,
    'num_factors': None,
    'hidden_size': 200,
    'dropout_prob': 0.1,

    'initial_lr': 8e-4,
    'minimum_lr': 1e-4,
    'shrink_rounds': 4,
    'shrink_factor': 0.5,
    'minimum_boost': 1e-3,
    'weights_decay': 1e-4,

    'epoch_size': 100000,
    'batch_size': 10000,
    'num_epochs': 100,
    'early_stop': 10,
}
