#!/usr/bin/env python
"""
usage:  bcl2fq-local -i <seq_dir> -o <ou_dir>

optional arguments:
    --sample-sheet Path  Using custom sample sheet file
    --mismatch N         Mismatch for barcode, default: 1
    --process N          Process number for demultiplexing and processing
    --io-process N       Process number for reading and writing
    --binpath   Path     Bcl2fastq binary file path
    --cmd-only           Only print the cmd without running it
"""
import xmltodict
import subprocess
import argparse
import os
import sys
import time
import shutil
# import json


settings = {}


def parse_params(xml_file):
    with open(xml_file) as f:
        contents = f.read()
    try:
        params = xmltodict.parse(contents)
    except Exception as e:
        print(e)
    else:
        return params


def gen_conf():
    params_info_file = os.path.join(settings['seq_dir'], 'RunInfo.xml')
    params = parse_params(params_info_file)
    settings['mask'] = gen_mask(params['RunInfo']['Run']['Reads']['Read'])


def gen_mask(reads):
    mask = []
    for item in reads:
        if item['@IsIndexedRead'] == 'N':
            mask.append('y{}n'.format(int(item["@NumCycles"]) - 1))
        elif item['@IsIndexedRead'] == 'Y':
            mask.append('i{}n'.format(int(item["@NumCycles"]) - 1))
        else:
            continue
    return ','.join(mask)


def gen_commmand():
    template = '{bin} -r {read_process_num} -p {parse_process_num} -w {write_process_num} ' + \
        '--barcode-mismatches {mismatch} --no-lane-splitting -R {seq_dir} --output-dir {out_dir} ' + \
        '--use-bases-mask {mask} --sample-sheet {sample_sheet_path}'

    return template.format(read_process_num=settings['ioprocess'],
                           parse_process_num=settings['process'],
                           write_process_num=settings['ioprocess'],
                           mismatch=settings['mismatch'],
                           seq_dir=settings['seq_dir'],
                           out_dir=settings['out_dir'],
                           mask=settings['mask'],
                           sample_sheet_path=settings['sample_sheet'],
                           bin=settings['binpath']
                           )


def wait_sequence_finish():
    while not os.path.exists(os.path.join(settings['seq_dir'], 'RTAComplete.txt')):
        print('Sequence not finished! Wait for finishing...')
        time.sleep(60)


def check_sample_sheet_existence():
    if not os.path.exists(settings['sample_sheet']):
        sys.exit('{path} not found!'.format(path=settings['sample_sheet']))


def move_undetermined_files():
    dest_dir = os.path.join(settings['out_dir'], 'UndeterminedReads')
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.mkdir(dest_dir)
    shutil.move(os.path.join(settings['out_dir'], 'Undetermined_S0_R1_001.fastq.gz'), dest_dir)
    shutil.move(os.path.join(settings['out_dir'], 'Undetermined_S0_R2_001.fastq.gz'), dest_dir)


def run_bcl2fq(cmd):
    check_sample_sheet_existence()
    wait_sequence_finish()
    res = subprocess.Popen(cmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           encoding='utf-8',
                           shell=True)
    while True:
        output = res.stdout.readline()
        if res.poll() is not None:
            break
        if output:
            print(output.strip())
    return_code = res.poll()
    return return_code


def parse_args():
    usage = ''' bcl2fq-local -i <seq_dir> -o <ou_dir>
    
optional arguments:
    --sample-sheet Path  Using custom sample sheet file
    --mismatch N         Mismatch for barcode, default: 1
    --process N          Process number for demultiplexing and processing
    --io-process N       Process number for reading and writing
    --binpath   Path     Bcl2fastq binary file path
    --cmd-only           Only print the cmd without running it
    '''
    parser = argparse.ArgumentParser(usage=usage, add_help=False)
    parser.add_argument('-i', metavar='DirPath', help='Sequence run dir', required=True)
    parser.add_argument('-o', metavar='DirPath', help='Output dir for fastq files', required=True)
    parser.add_argument('--sample-sheet', dest='sample_sheet', metavar='File', help='Using custom sample sheet file')
    parser.add_argument('--mismatch', metavar='Num', type=int, default=1, help='Mismatch for barcode, default: 1')
    parser.add_argument('--process', metavar='Num', type=int, default=24,
                        help='Process number for demultiplexing and processing')
    parser.add_argument('--io-process', metavar='Num', type=int, dest='ioprocess', default=4,
                        help='Process number for reading and writing')
    parser.add_argument('--binpath', metavar='File', help='bcl2fastq binary file path')
    parser.add_argument('--cmd-only', dest='cmd_only', action='store_true', default=False,
                        help='Only print the cmd without running it')
    args = parser.parse_args(sys.argv[1:])

    settings['seq_dir'] = os.path.abspath(args.i)
    settings['out_dir'] = os.path.abspath(args.o)
    settings['sample_sheet'] = args.sample_sheet if args.sample_sheet else os.path.join(settings['seq_dir'],
                                                                                        'SampleSheet.csv')
    settings['mismatch'] = args.mismatch
    settings['process'] = args.process
    settings['ioprocess'] = args.ioprocess
    bcl2fastq_sys_path = os.popen('which bcl2fastq').read().strip()
    if args.binpath and os.path.exists(args.binpath):
        settings['binpath'] = args.binpath
    elif os.path.exists('/usr/bin/bcl2fastq'):
        settings['binpath'] = '/usr/bin/bcl2fastq'
    elif os.path.exists(bcl2fastq_sys_path):
        settings['binpath'] = bcl2fastq_sys_path
    else:
        sys.exit('bcl2fastq path not found, please specify the dir!')
    settings['cmd_only'] = args.cmd_only


def main():
    parse_args()
    gen_conf()
    cmd = gen_commmand()
    print(cmd)
    if not settings['cmd_only']:
        run_bcl2fq(cmd)
        move_undetermined_files()


if __name__ == '__main__':
    main()
