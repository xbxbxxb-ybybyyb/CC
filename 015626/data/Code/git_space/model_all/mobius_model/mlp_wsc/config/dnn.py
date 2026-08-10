processing_params = {
    'x_need_zscore': False,
    'x_need_clip': False,
    'y_label_need_zscore': True,
    'y_label_need_clip': True,
    'x_clip_range': ('q_0.005', 'q_0.995'),
    'y_clip_range': ('q_0.005', 'q_0.995'),
    'cv_num': 5,
}

model_params = {
    'hidden_size_list': (128, 64),
    'dropout_prob': 0.05,
}

obj_params = {

}

training_params = {
    'initial_lr': 7.5e-4,
    'l2_regularization': 0,
    'batch_size': 10000,
    'num_iterations': 200,
    'early_stopping_rounds': 25,
}
