def build_network(config):
    network = None
    structure = config['structure']

    if structure == 'CRN':
        from network.CRN import Network
        network = Network(window_size=config['window_size'], num_factors=config['num_factors'], hidden_size=config['hidden_size'], dropout_prob=config['dropout_prob'])

    if structure == 'RNN':
        from network.RNN import Network
        network = Network(window_size=config['window_size'], num_factors=config['num_factors'], hidden_size=config['hidden_size'], dropout_prob=config['dropout_prob'])

    if structure == 'MLP':
        from network.MLP import Network
        network = Network(window_size=config['window_size'], num_factors=config['num_factors'], hidden_size=config['hidden_size'], dropout_prob=config['dropout_prob'])

    if structure == 'EWM':
        from network.EWM import Network
        network = Network(window_size=config['window_size'], num_factors=config['num_factors'])

    if network is None:
        raise AssertionError('Failed to build network: {}'.format(structure))
    return network
