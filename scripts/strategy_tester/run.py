import json

import strategy_tester

if __name__ == "__main__":
    with open('./scripts/strategy_tester/config.json') as f:
        sim_configs = json.load(f)

    for sim in sim_configs:
        for instrument in sim['instrument']:
            strategy_tester.execute(
                sim['strategy'],
                instrument,
                sim['period'],
                sim['params']
            )
