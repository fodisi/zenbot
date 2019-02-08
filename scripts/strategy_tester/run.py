import json

import strategy_tester

if __name__ == "__main__":
    # Simulation configs must have the following format:
    # [{"strategy": "", "instrument": [""], "period": 0, "params": {"":""}}]
    # Loads simulation configs.
    with open('./scripts/strategy_tester/config.json') as f:
        sim_configs = json.load(f)

    # Executes one simulation for each simulation
    for config in sim_configs:
        for instrument in config['instrument']:
            # print(config['params'])
            strategy_tester.execute(
                config['strategy'],
                instrument,
                config['params'],
                config['days'],
                config['start'],
                config['end']
            )
