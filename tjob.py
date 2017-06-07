#! /usr/bin/env python

import os, datetime, re, argparse

def qstatJR(jobid, state):
	QJs = os.popen('qstat -j {id}'.format(id = jobid)).readlines()
	for qj in QJs:
		if qj.startswith('owner'):
			user = qj.strip().split()[1]
		if qj.startswith('sge_o_workdir'):
			path = qj.strip().split()[1]
		if qj.startswith('hard resource_list'):
			P = re.search('num_proc=(\d+)', qj.strip()).group(1)
			VF = re.search('virtual_free=(\d+)', qj.strip()).group(1)+'G'
		if qj.startswith('job_name'):
			job_name = qj.strip().split()[1]
			CMD = path+'/'+job_name
		if qj.startswith('usage'):
			CPU = re.search('cpu=([\d:]*),', qj.strip()).group(1)
			vmem = re.search('vmem=(.*)([GMA]),', qj.strip())
			Mnow = shift_unit(vmem)
			maxvmem = re.search('maxvmem=(.*)([GMA])', qj.strip())
			Mmax = shift_unit(maxvmem)
	if state == 'r' and (Mnow != 'NA' or Mmax != 'NA'):
		if float(Mnow[:-1]) > float(VF[:-1]):
			VF = '**'+VF
		elif float(Mmax[:-1]) > float(VF[:-1]):
			VF = '*'+VF
	if not 'VF' in dir(): VF = '-'
	if not 'P' in dir(): P = '-'
	if not 'CPU' in dir(): CPU = '-'
	if not 'Mmax' in dir(): Mmax = '-'
	if not 'Mnow' in dir(): Mnow = '-'
	return P, CPU, Mnow, Mmax, VF, CMD, user

def shift_unit(research):
	if research.group(2) == 'A':
		mem = 'NA'
	elif research.group(2) == 'G':
		mem = str(round(float(research.group(1)), 1))+research.group(2)
	elif research.group(2) == 'M':
		mem = str(round(float(research.group(1))/1024, 1))+'G'
	return mem

def read_infor(user):
	if user == 'myself':
		qstat = os.popen('qstat').read()
	else:
		qstat = os.popen('qstat -u {u}'.format(u = user)).read()
	allinfor = {i.strip().split()[0]:i for i in qstat.strip().split('\n')[2:]}
	states = [i.strip().split()[4] for i in qstat.strip().split('\n')[2:]]
	allnum = len(states)
	Rnum = states.count('r')
	top = '%-8s%-15s%-6s%3s   %-13s%9s%9s%9s%9s  %-22s%-s [%d/%d]\n%s' % ('jobID', 'User','State', 'P', 'CPU', 'Mnow', 'Mmax', 'VF', 'TIME', 'node', 'CMD', Rnum, allnum, '-'*120)
	print(top)
	return allinfor

def deal_infor(allinfor):
	for id in sorted(allinfor.keys()):
		state = allinfor[id].strip().split()[4]
		State_time = ' '.join(allinfor[id].strip().split()[5:7])
		state_time = datetime.datetime.strptime(State_time, '%m/%d/%Y %H:%M:%S')
		now = datetime.datetime.now()
		diff_time = now - state_time
		TIME = str(round((diff_time.days*24*3600+diff_time.seconds)/3600.0, 1))+'h'
		if state == 'r':
			node = allinfor[id].strip().split()[7].split('@')[1]
		else:
			node = '-'
		P, CPU, Mnow, Mmax, VF, CMD, user = qstatJR(id, state)
		infor = '%-8s%-15s %-5s%3s   %-13s%9s%9s%9s%9s  %-22s%-s' % (id, user, state, P, CPU, Mnow, Mmax, VF, TIME, node, CMD)
		print(infor)

def Parser_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', default = 'myself', metavar = '', help = 'User')
	args = parser.parse_args()
	return args

def main():
	args = Parser_args()
	infor = read_infor(args.u)
	deal_infor(infor)

if __name__ == '__main__':
	main()
