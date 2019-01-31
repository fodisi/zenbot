import json

import strategy_tester

if __name__ == "__main__":
    # Simulation configs must have the following format:
    # [{"strategy": "", "instrument": [""], "period": 0, "params": {"":""}}]
    # Loads simulation configs.
    with open('./scripts/strategy_tester/config.json') as f:
        sim_configs = json.load(f)

    # Executes one simulation for each simulation
    for sim in sim_configs:
        for instrument in sim['instrument']:
            strategy_tester.execute(
                sim['strategy'],
                instrument,
                sim['period'],
                sim['params']
            )
