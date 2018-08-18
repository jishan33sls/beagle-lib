#!/usr/bin/env python2.7

# Daniel Ayres

import sys
import argparse
import subprocess
import re
from math import log, exp

def gen_log_site_list(min, max, samples):
    log_range=(log(max) - log(min))
    samples_list = []
    for i in range(0, samples):
        samples_list.append(int(round(exp(log(min) + log_range/(samples-1)*i))))
    return samples_list

def main():
    parser = argparse.ArgumentParser(description='generate synthetictest benchmarks')
    parser.add_argument('synthetictest_path', help='path to synthetictest')
    args = parser.parse_args()

    taxa_list = [16, 400]
    rates = 4
    precision_list = ['double']

    states_list = [4]
    site_samples = 100
    # site_samples = 2
    sites_min = 100
    rsrc_list = ['cpu', 'cpu-threaded', 'pll', 'pll-repeats', 'gpu']
    reps = 100
    # reps = 10

    seed_list = range(1,101)
    # seed_list = range(1,2)

    extra_args = ['--randomtree', '--stdrand', '--fulltiming']

    throughput_re = re.compile('tree throughput total:   (.*) M partials/second')

    debug_file = open('debug.txt', 'w')

    header = 'iteration, precision, states, sites, taxa, seed, resource, throughput' 
    print header

    iteration = 0

    for taxa in taxa_list:
        sites_max = 1000000
        if (taxa == 400):
            sites_max = 100000
        sites_list = gen_log_site_list(sites_min, sites_max, site_samples)
        for rsrc in rsrc_list:
            for precision in precision_list:
                for states in states_list:
                    for sites in sites_list:
                        for seed in seed_list:
                            out_string = str(iteration)
                            out_string += ', ' + str(precision)
                            out_string += ', ' + str(states)
                            out_string += ', ' + str(sites)
                            out_string += ', ' + str(taxa)
                            out_string += ', ' + str(seed)
                            synthetictest_cmd = [args.synthetictest_path]
                            synthetictest_cmd.extend(['--states', str(states), '--sites', str(sites)])
                            synthetictest_cmd.extend(['--taxa', str(taxa), '--compacttips', str(taxa)])
                            synthetictest_cmd.extend(['--reps', str(reps), '--rates', str(rates)])
                            throughput_re_index = 0
                            if   rsrc == 'cpu':
                                synthetictest_cmd.extend(['--rsrc', '0', '--disablethreads'])
                            elif rsrc == 'cpu-threaded':
                                synthetictest_cmd.extend(['--rsrc', '0'])
                            elif rsrc == 'pll':
                                synthetictest_cmd.extend(['--rsrc', '0', '--plltest'])
                                throughput_re_index = 1
                            elif rsrc == 'pll-repeats':
                                synthetictest_cmd.extend(['--rsrc', '0', '--plltest', '--pllrepeats'])
                                throughput_re_index = 1
                            elif rsrc == 'gpu':
                                synthetictest_cmd.extend(['--rsrc', '1'])
                            synthetictest_cmd.extend(extra_args)
                            if precision == 'double':
                                synthetictest_cmd.extend(['--doubleprecision'])
                            try:
                                synthetictest_out = subprocess.check_output(synthetictest_cmd)
                                out_string += ', ' + rsrc
                                throughput = throughput_re.findall(synthetictest_out)
                                if throughput:
                                    out_string +=  ', ' + throughput[throughput_re_index]
                                else:
                                    out_string += ', ' + 'NA'
                            except subprocess.CalledProcessError:
                                out_string += 'ERROR'
                            print out_string
                            debug_file.write('===============================================================\n')
                            debug_file.write(out_string + '\n')
                            debug_file.write(' '.join(synthetictest_cmd) + '\n')
                            debug_file.write(synthetictest_out)
                            iteration += 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
