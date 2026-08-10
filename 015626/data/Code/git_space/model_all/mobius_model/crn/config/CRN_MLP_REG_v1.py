model_config = {
    'config_name': 'CRN_MLP_REG_v1',
    'export_name': 'crn_mlp_reg',

    'structure': 'MLP',
    'objective': 'MSE',

    'num_minutes': 237,
    'coefficient': None,

    'window_size': 10,
    'num_factors': None,
    'hidden_size': 128,
    'dropout_prob': 0.05,

    'initial_lr': 7.5e-4,
    'minimum_lr': 2.5e-5,
    'shrink_rounds': 3,
    'shrink_factor': 0.5,
    'minimum_boost': 0.0,
    'weights_decay': 0.0,

    'batch_size': 10000,
    'num_epochs': 200,
    'early_stop': 25,
}
