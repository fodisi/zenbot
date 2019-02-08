#!/usr/bin/python3

import subprocess
from datetime import datetime
import re
import sys
import signal

# Changeable Variables
strat = 'trend_ma'
pair = 'gdax.BTC-USD'
days = 0
start_date = ''
end_date = ''
filename = ''
FILENAME_FORMAT_DAYS = './scripts/strategy_tester/results/result_{0}_{1}_{2}days.txt'
FILENAME_FORMAT_PERIOD = './scripts/strategy_tester/results/result_{0}_{1}_{2}_{3}.txt'

# variables = {
#    'period': ['10m','15m','20m'], #=<value>  period length (default: 10m)
#    'min_periods': [52], #=<value>  min. number of history periods (default: 52)
#    'trend_ema': [10,20,30], #=<value>  number of periods for trend EMA (default: 20)
#    'neutral_rate': [0, 'auto'], #=<value>  avoid trades if abs(trend_ema) under this float (0 to disable, "auto" for a variable filter) (default: 0.06)
#    'oversold_rsi_periods': [15,20,25], #=<value>  number of periods for oversold RSI (default: 20)
#    'oversold_rsi': [25,30,35] #=<value>  buy when RSI reaches this value (default: 30)
# }

# Simulation variables (trend_ma default)
# variables = {
#     # =<value>  period length (default: 10m)
#     'period': ['10m', '15m', '20m'],
#     # =<value>  min. number of history periods (default: 52)
#     'min_periods': [52],
#     # =<value>  number of periods for trend EMA (default: 20)
#     'trend_ema': [10],
#     # =<value>  avoid trades if abs(trend_ema) under this float (0 to disable, "auto" fo$
#     'neutral_rate': [0],
#     # =<value>  number of periods for oversold RSI (default: 20)
#     'oversold_rsi_periods': [15],
#     # =<value>  buy when RSI reaches this value (default: 30)
#     'oversold_rsi': [25]
# }
variable = {}
# Stores Output
results = {}

# Needed for Recursiveness
keys = []
vals = []
# keys = list(variables.keys())
# vals = list(variables.values())


# Ctrl C - Handler
def interruption_handler(signal, frame):
    print('[-] Exiting due to Ctrl-C')
    sys.exit(0)


# Call the Process
def run_simulation(strtorun):
    if days:
        processtorun = 'zenbot sim {} --strategy={} --days={} {} --silent'.format(
            pair, strat, days, strtorun)
    else:
        processtorun = 'zenbot sim {} --strategy={} --start={} --end={} {} --silent'.format(
            pair, strat, start_date, end_date, strtorun)
    result = subprocess.check_output(processtorun.split())
    # Search for Percentage & Win/Loss
    m = re.search(b'end balance:.+\((.*)\%\)', result)
    percent = 0
    if m:
        percent = float(m.group(1))
    m = re.search(b'win\/loss: (.+)', result)
    if m:
        winloss = m.group(1).decode('utf-8')
    else:
        winloss = '0/0'
    # Store into table as Percentage Key
    results[percent] = '{}% - {}: {}'.format(percent, winloss, processtorun)
    # save results as csv: percent, winloss, processtorun
    line = str(percent) + '%,' + winloss + ',' + processtorun
    print(line)

    fh = open(filename, "a")
    fh.write(line + '\n')
    fh.close()


# Recurse the combinations of variables
def setup_simulation(strtorun, k_ind, v_ind):
    for item in vals[k_ind]:
        # Replace Key=Value if there is already one
        pat = re.compile('\-\-{}='.format(keys[k_ind]))
        if pat.search(strtorun):
            strtorun = re.sub(
                '(\-\-{}=[^\s]+)'.format(keys[k_ind]), '--{}={}'.format(keys[k_ind], item), strtorun)
        else:
            strtorun = strtorun + ' --{}={}'.format(keys[k_ind], item)

        if k_ind < (len(keys) - 1):
            setup_simulation(strtorun, k_ind + 1, 0)  # Next Item In Variables
        else:
            # # Format Process to Run String
            # processtorun = 'zenbot sim {} --strategy={}{} --days={} --silent'.format(
            #     pair, strat, strtorun, days)
            # Run Process Here
            run_simulation(strtorun)


# Sort the results at the end
def sort_results():
    print("\n>>> Printing Sorted Results\n")
    keylist = list(results.keys())
    keylist.sort()

    for key in keylist:
        line = '{}'.format(results[key])
        print(line)
    print("\n>>> Wrote Results to {0}".format(filename))


# Executes the simulation process for the last X days.
def execute(strategy, instrument, sim_params, sim_days, sim_start="", sim_end=""):
    # Sets global variables
    global strat, pair, days, start_date, end_date, filename, variables, keys, vals
    strat = strategy
    pair = instrument
    days = sim_days
    start_date = sim_start
    end_date = sim_end
    variables = sim_params
    keys = list(variables.keys())
    vals = list(variables.values())

    subtitle = ''
    # if days is bigger than 0, ignores start and end date.
    if days:
        filename = FILENAME_FORMAT_DAYS.format(strat, pair, days)
        subtitle = '>>> Strategy: {}     Instrument: {}     Days: {}'.format(
            strat, pair, days)
    else:
        filename = FILENAME_FORMAT_PERIOD.format(
            strat, pair, start_date, end_date)
        subtitle = '>>> Strategy: {}     Instrument: {}     Start: {}     End: {}'.format(
            strat, pair, start_date, end_date)

    print('>>> Strategy Tester: {}'.format(str(datetime.now())))
    print(subtitle)

    signal.signal(signal.SIGINT, interruption_handler)
    fh = open(filename, "w")
    fh.write('Percent,WinLoss,StrategyProcess\n')  # csv header line
    fh.close()

    setup_simulation('', 0, 0)
    sort_results()


# Starts program
if __name__ == "__main__":
    execute(strat, pair, days, variables)
