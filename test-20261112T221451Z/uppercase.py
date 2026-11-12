import argparse
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('input');p.add_argument('output');p.add_argument('--mode',required=True,choices=['normal','fail_once','incomplete_once']);p.add_argument('--attempt',type=int,required=True,choices=[1,2]);a=p.parse_args()
text=Path(a.input).read_text(encoding='ascii').upper()
if a.attempt == 1 and a.mode == 'fail_once':
 Path(a.output).write_text(text[:7],encoding='ascii')
 print('Deliberate first-attempt failure after writing partial output',flush=True)
 raise SystemExit(23)
if a.attempt == 1 and a.mode == 'incomplete_once':
 Path(a.output).write_text(text[:7],encoding='ascii')
 print('Program completed with deliberate incomplete first-attempt result',flush=True)
else:
 Path(a.output).write_text(text,encoding='ascii')
 print('Program completed',flush=True)
