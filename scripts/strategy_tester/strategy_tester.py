#!/usr/bin/python3

import subprocess
from datetime import datetime
import re
import sys
import signal

# Changeable Variables
strat = 'trend_ma'
pair = 'gdax.BTC-USD'
days = 2
filename = ''
FILENAME_FORMAT = './scripts/strategy_tester/results/result_{0}_{1}_{2}days.txt'
# FILENAME_FORMAT = './results/result_{0}_{1}_{2}days.txt'


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
def sig_handler(signal, frame):
    print('[-] Exiting due to Ctrl-C')
    sys.exit(0)


# Call the Process
def call_process(strtorun):
    processtorun = 'zenbot sim {} --strategy={} --days={} {} --silent'.format(
        pair, strat, days, strtorun)
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
    line = str(percent) + '%, ' + winloss + ': ' + processtorun
    print(line)

    fh = open(filename, "a")
    fh.write(line + '\n')
    fh.close()


# Recurse the combinations of variables
def recurse_combos(strtorun, k_ind, v_ind):
    for item in vals[k_ind]:
        # Replace Key=Value if there is already one
        pat = re.compile('\-\-{}='.format(keys[k_ind]))
        if pat.search(strtorun):
            strtorun = re.sub(
                '(\-\-{}=[^\s]+)'.format(keys[k_ind]), '--{}={}'.format(keys[k_ind], item), strtorun)
        else:
            strtorun = strtorun + ' --{}={}'.format(keys[k_ind], item)

        if k_ind < (len(keys) - 1):
            recurse_combos(strtorun, k_ind + 1, 0)  # Next Item In Variables
        else:
            # Format Process to Run String
            processtorun = 'zenbot sim {} --strategy={}{} --days={} --silent'.format(
                pair, strat, strtorun, days)
            # Run Process Here
            call_process(strtorun)


# Sort the results at the end
def sort_results():
    print("\n[+] Printing Sorted Results\n")
    keylist = list(results.keys())
    keylist.sort()

    for key in keylist:
        line = '{}'.format(results[key])
        print(line)
    print("\n[-] Wrote Results to {0}".format(filename))


# Executes the simulation process
def execute(strategy, instrument, period, sim_params):
    global strat, pair, days, filename, variables, keys, vals
    strat = strategy
    pair = instrument
    days = period
    variables = sim_params
    keys = list(variables.keys())
    vals = list(variables.values())
    filename = FILENAME_FORMAT.format(strat, pair, days)

    signal.signal(signal.SIGINT, sig_handler)
    fh = open(filename, "w")
    fh.close()

    print('[+] Strategy Algorithm Tester: {}'.format(str(datetime.now())))
    print('[+] Strategy: {}     Instrument: {}     Days: {}'.format(strat, pair, days))
    recurse_combos('', 0, 0)
    sort_results()


# Starts program
if __name__ == "__main__":
    execute(strat, pair, days, variables)
