import json
import csv
import math
import numpy as np
from collections import OrderedDict

class NBA_Evolutionary_Lineup_Selector:
    config = None
    player_dict = {}
    roster_construction = ['PG', 'SG', 'SF', 'PF', 'C', 'F', 'G', 'UTIL']
    lineup_pool = {}
    tournament_results = {}

    def __init__(self):
        self.load_config()
        self.load_projections(self.config['projection_path'])
        self.load_boom_bust(self.config['boombust_path'])
        self.load_lineup_pool(self.config['output_path']) # Load lineups generated by our optimizer


    # Load config from file
    def load_config(self):
        with open('config.json') as json_file: 
            self.config = json.load(json_file)
         
    # Load projections from file
    def load_projections(self, path):
        # Read projections into a dictionary
        with open(path) as file:
            reader = csv.DictReader(file)
            for row in reader:
                player_name = row['Name']
                self.player_dict[player_name] = {'Fpts': 0, 'Position': [], 'ID': 0, 'Salary': 0, 'StdDev': 0, 'Ownership': 0, 'In Lineup': False}
                self.player_dict[player_name]['Fpts'] = float(row['Fpts'])

                #some players have 2 positions - will be listed like 'PG/SF' or 'PF/C'
                self.player_dict[player_name]['Position'] = [pos for pos in row['Position'].split('/')]

                if 'PG' in self.player_dict[player_name]['Position'] or 'SG' in self.player_dict[player_name]['Position']:
                    self.player_dict[player_name]['Position'].append('G')

                if 'SF' in self.player_dict[player_name]['Position'] or 'PF' in self.player_dict[player_name]['Position']:
                    self.player_dict[player_name]['Position'].append('F')

                self.player_dict[player_name]['Position'].append('UTIL')


                self.player_dict[player_name]['Salary'] = int(row['Salary'].replace(',',''))
                # need to pre-emptively set ownership to 0 as some players will not have ownership
                # if a player does have ownership, it will be updated later on in load_ownership()
                self.player_dict[player_name]['Salary'] = int(row['Salary'].replace(',',''))

    # Load standard deviations
    def load_boom_bust(self, path):
        with open(path) as file:
            reader = csv.DictReader(file)
            for row in reader:
                player_name = row['Name']
                if player_name in self.player_dict:
                    self.player_dict[player_name]['StdDev'] = float(row['Std Dev'])

    def load_lineup_pool(self, path):
        with open(path) as file:
            reader = csv.DictReader(file)
            i = 0
            for row in reader:
                self.lineup_pool[i] = [row['PG'], row['SG'], row['SF'], row['PF'], row['C'], row['G'], row['F'], row['UTIL']]
                i = i + 1

    def run_evolution(self):
        remaining_pool = self.lineup_pool
        # While we still have more than the requisite 150 "surviving" lineups
        while len(remaining_pool) >= 150:
            # Dict of lineup fitness metrics - a lineup's ID will be tied to a fitness score
            # {1: 23, 2: 14.5, .... so on}
            lineup_fitness = {}
            # The winning lineups for this iteration
            winning_lineups = []
            # The top 1% lineups for this iteration
            top_1_percent = []
            # The top 10% for this iteration
            top_10_percent = []

            # Simulate a tournament 1000 times
            for i in range(1000):
                field_lineups = {}
                # random fpts expectation
                temp_fpts_dict = {p: round((np.random.normal(stats['Fpts'], stats['StdDev'])), 2) for p,stats in self.player_dict.items()}

                # find the realized fantasy points for this simulation
                for lineup_id,lineup in remaining_pool.items():
                    fpts_sim = sum(temp_fpts_dict[player] for player in lineup)
                    field_lineups[fpts_sim] = lineup_id

                # sort the dictionary descending
                sorted_lineups = OrderedDict(sorted(dict.items(), key=lambda v: v, reverse=True))
                
                # append the winning lineup
                winning_lineups.append(sorted_lineups[:1])

                # append the top 1% lineups
                one_p = math.floor(len(remaining_pool) / 100)
                top_1_percent.append(sorted_lineups[:one_p])

                # append the top 10% lineups
                ten_p = math.floor(len(remaining_pool) / 10)
                top_10_percent.append(sorted_lineups[:ten_p])
            

            print(winning_lineups)
            # Determine fitness score
            # Fitness score = 10*win_percent + 5*top_1_percent + 1*top_10_percent
            # for lineup_id in remaining_pool:
            #     winning_percent = winning_lineups.count(lineup_id)



                

        # From the pool of lineups, simulate a GPP
        # For each lineup in the pool, mark how often they win, finish top 1%, finish top 10%
        # Create some metric from the win%,1%,10%
        # Keep only the top 90% from each iteration
        # Repeat until you have a set of 150 lineups
        pass
        