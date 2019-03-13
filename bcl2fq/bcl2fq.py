#!/usr/bin/env python
"""
    Usage: bcl2fq -i <input dir> -o <output dir>
            [--sample-sheet <sample sheet path, default: input_dir/SampleSheet.csv>]
            [--mismatch <mismatch num, default: 1>]
            [--process <process num, default:24>]
            [--binpath <bcl2fastq bin path, default: /usr/local/bin/bcl2fastq>]
            [--cmd-only]
"""
import xmltodict
import subprocess
import argparse
import os
import sys
# import json


settings = {}


def parse_params(xmlfile):
    with open(xmlfile) as f:
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
    template = '{bin} -r {read_process_num} -d {demulti_process_num} -p {parse_process_num} -w {write_process_num} ' + \
        '--barcode-mismatches {mismatch} --no-lane-splitting -R {seq_dir} --output-dir {out_dir} ' + \
        '--use-bases-mask {mask} --sample-sheet {sample_sheet_path}'

    return template.format(read_process_num=settings['ioprocess'],
                           parse_process_num=settings['process'],
                           write_process_num=settings['ioprocess'],
                           demulti_process_num=settings['process'],
                           mismatch=settings['mismatch'],
                           seq_dir=settings['seq_dir'],
                           out_dir=settings['out_dir'],
                           mask=settings['mask'],
                           sample_sheet_path=settings['sample_sheet'],
                           bin=settings['binpath']
                           )


def run_bcl2fq(cmd):
    res = subprocess.Popen(cmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           encoding='utf-8',
                           shell=True)
    for line in res.stdout.read():
        print(line)
    return res.returncode


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help='Sequence run dir', required=True)
    parser.add_argument('-o', help='Output dir for fastq files', required=True)
    parser.add_argument('--sample-sheet', dest='sample_sheet', help='Using custom sample sheet file')
    parser.add_argument('--mismatch', type=int, default=1, help='Mismatch for barcode, default: 1')
    parser.add_argument('--process', type=int, default=24, help='Process number for demultiplexing and processing')
    parser.add_argument('--io-process', type=int, dest='ioprocess', default=4,
                        help='Process number for reading and writing')
    parser.add_argument('--binpath', default='/usr/local/bin/bcl2fastq', help='bcl2fastq binary file path')
    parser.add_argument('--cmd-only', dest='debug', action='store_true', default=False,
                        help='Only print the cmd with out running it')
    args = parser.parse_args()
    settings['seq_dir'] = os.path.abspath(args.i)
    settings['out_dir'] = os.path.abspath(args.o)
    settings['sample_sheet'] = args.sample_sheet if args.sample_sheet else os.path.join(settings['seq_dir'],
                                                                                        'SampleSheet.csv')
    settings['mismatch'] = args.mismatch
    settings['process'] = args.process
    settings['ioprocess'] = args.ioprocess
    bcl2fastq_sys_path = os.popen('which bcl2fastq').read().strip()
    if os.path.exists(args.binpath):
        settings['binpath'] = args.binpath
    elif os.path.exists('/usr/bin/bcl2fastq'):
        settings['binpath'] = '/usr/bin/bcl2fastq'
    elif os.path.exists(bcl2fastq_sys_path):
        settings['binpath'] = bcl2fastq_sys_path
    else:
        sys.exit('bcl2fastq path not found, please specify the dir!')
    settings['debug'] = args.debug


def main():
    parse_args()
    gen_conf()
    cmd = gen_commmand()
    print(cmd)
    if not settings['debug']:
        run_bcl2fq(cmd)


if __name__ == '__main__':
    main()
