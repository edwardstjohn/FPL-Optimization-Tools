import time
from concurrent.futures import ProcessPoolExecutor
import sys
import os
import pandas as pd
from pathlib import Path
from solve_regular import solve_regular
import glob
import argparse
from pushbullet.pushbullet import PushBullet


def run_sensitivity(options=None):

    if options is None or 'count' not in options:

        # print("Remember to delete results folder and enable noise! Also note: you may reach your results faster to run multiple tabs of this script")
        # print("")
        runs = options.get('runs')
        processes = options.get('processes')
    else:
        runs = options.get('count', 1)
        processes = options.get('processes', 1)

    start = time.time()

    # for i in range(runs):
    #     print('Run no: ' + str(i))
    #     os.system('python solve_regular.py --randomized true')

    all_jobs = [{'run_no': str(i+1), 'randomized': True} for i in range(runs)]

    with ProcessPoolExecutor(max_workers=processes) as executor:
        results = list(executor.map(solve_regular, all_jobs))

    end = time.time()

    print()
    print(f"Total time taken is {(end - start) / 60:.2f} minutes")


def read_sensitivity(options=None):

    if options is None or options.get('gw') is None:
        gw = options.get('gw')
        situation = options.get('situation')
    else:
        gw = options['gw']
        situation = options.get('situation', 'n')

    print()

    directory = '../data/results/'
    # no_plans = len(os.listdir(directory))

    if situation == "N" or situation == "n": 

        buys = []
        sells = []
        no_plans = 0

        for filename in Path(directory).glob("*.csv"):
            plan = pd.read_csv(filename)
            if plan[(plan['week']==gw) & (plan['transfer_in']==1)]['name'].to_list() == []:
                buys += ['No transfer']
                sells += ['No transfer']
            else:
                buy_list = plan[(plan['week']==gw) & (plan['transfer_in']==1)]['name'].to_list()
                buy = ', '.join(buy_list)
                buys.append(buy)

                sell_list = plan[(plan['week']==gw) & (plan['transfer_out']==1)]['name'].to_list()
                sell = ', '.join(sell_list)
                sells.append(sell)
            no_plans += 1

        buy_sum = pd.DataFrame(buys, columns=['player']).value_counts().reset_index(name='PSB')
        sell_sum = pd.DataFrame(sells, columns=['player']).value_counts().reset_index(name='PSB')

        buy_sum['PSB'] = ["{:.0%}".format(buy_sum['PSB'][x]/no_plans) for x in range(buy_sum.shape[0])]
        sell_sum['PSB'] = ["{:.0%}".format(sell_sum['PSB'][x]/no_plans) for x in range(sell_sum.shape[0])]

        #print('Buy:')
        #print('\n'.join(buy_sum.to_string(index = False).split('\n')[1:]))
        #print()
        #print('Sell:')
        #print('\n'.join(sell_sum.to_string(index = False).split('\n')[1:]))
        #print()

        result_str = 'Buy:\n'
        result_str += '\n'.join(buy_sum.to_string(index = False).split('\n')[1:])
        result_str += '\n\nSell:\n'
        result_str += '\n'.join(sell_sum.to_string(index = False).split('\n')[1:])
        result_str += '\n'
        print(result_str)
        return result_str

    elif situation == "Y" or situation == "y":

        goalkeepers = []
        defenders = []
        midfielders = []
        forwards = []

        no_plans = 0

        for filename in Path(directory).glob("*.csv"):
            plan = pd.read_csv(filename)
            goalkeepers += plan[(plan['week']==gw) & (plan['squad']==1) & (plan['pos']=='GKP') & (plan['transfer_out']!=1)]['name'].to_list()
            defenders += plan[(plan['week']==gw) & (plan['squad']==1) & (plan['pos']=='DEF') & (plan['transfer_out']!=1)]['name'].to_list()
            midfielders += plan[(plan['week']==gw) & (plan['squad']==1) & (plan['pos']=='MID') & (plan['transfer_out']!=1)]['name'].to_list()
            forwards += plan[(plan['week']==gw) & (plan['squad']==1) & (plan['pos']=='FWD') & (plan['transfer_out']!=1)]['name'].to_list()
            no_plans += 1

        keepers = pd.DataFrame(goalkeepers, columns=['player']).value_counts().reset_index(name='PSB')
        defs = pd.DataFrame(defenders, columns=['player']).value_counts().reset_index(name='PSB')
        mids = pd.DataFrame(midfielders, columns=['player']).value_counts().reset_index(name='PSB')
        fwds = pd.DataFrame(forwards, columns=['player']).value_counts().reset_index(name='PSB')

        keepers['PSB'] = ["{:.0%}".format(keepers['PSB'][x]/no_plans) for x in range(keepers.shape[0])]
        defs['PSB'] = ["{:.0%}".format(defs['PSB'][x]/no_plans) for x in range(defs.shape[0])]
        mids['PSB'] = ["{:.0%}".format(mids['PSB'][x]/no_plans) for x in range(mids.shape[0])]
        fwds['PSB'] = ["{:.0%}".format(fwds['PSB'][x]/no_plans) for x in range(fwds.shape[0])]

        print('Goalkeepers:')
        print('\n'.join(keepers.to_string(index = False).split('\n')[1:]))
        print()
        print('Defenders:')
        print('\n'.join(defs.to_string(index = False).split('\n')[1:]))
        print()
        print('Midfielders:')
        print('\n'.join(mids.to_string(index = False).split('\n')[1:]))
        print()
        print('Forwards:')
        print('\n'.join(fwds.to_string(index = False).split('\n')[1:]))

        result_str = 'Goalkeepers:\n'
        result_str += '\n'.join(keepers.to_string(index = False).split('\n')[1:])
        result_str += '\n\nDefenders:\n'
        result_str += '\n'.join(defs.to_string(index = False).split('\n')[1:])
        result_str += '\n\nMidfielders:\n'
        result_str += '\n'.join(mids.to_string(index = False).split('\n')[1:])
        result_str += '\n\nForwards:\n'
        result_str += '\n'.join(fwds.to_string(index = False).split('\n')[1:])
        result_str += '\n'

        return result_str

    else:
        print("Invalid input, please enter 'y' for a wildcard or 'n' for a regular transfer plan.")


def pushbullet(solution):
	apiKey = "o.dW3qDJPeeeHBhxAc6vERqzD0vKZw1OnK"
	p = PushBullet(apiKey)
	
	devices = p.getDevices() # Get a list of devices

	p.pushNote(devices[0]["iden"], 'Simulations completed', solution)


def main():
    # Collecting inputs
    runs = int(input("How many simulations would you like to run? "))
    processes = int(input("How many processes you want to run in parallel? "))
    gw = int(input("What GW are you assessing? "))
    situation = input("Is this a wildcard or preseason (GW1) solve? (y/n) ")
    
    # Options dictionary to pass the inputs to the functions
    options = {
        'runs': runs,
        'processes': processes,
        'gw': gw,
        'situation': situation
    }
    
    # Running the functions from simulations.py and sensitivity.py
    run_sensitivity(options)
    result_str = read_sensitivity(options)

    # Pushing result to device notifications
    pushbullet(result_str)

# Running the main function
if __name__ == "__main__":
    main()
