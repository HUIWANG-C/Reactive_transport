## sample varnm in proj_1 at bdnm boundary of proj_0

varnm = 'p'
bdnm = 'inlet'
formt = 'csv'

# dir_path = '/home/gsolemari/unsaturated/sims/first'
# proj_1 = 'flow'
# proj_0 = 'flow_b'

import os
import sys
import csv

dir_path = sys.argv[1]
proj_1 = sys.argv[2]
proj_0 = sys.argv[3]

lasttime = []
nproc1 = 0
proclst1 = os.listdir(dir_path + '/' + proj_1)
for procdir in proclst1:
    if procdir.startswith('processor'):
        nproc1 += 1
        lasttime.append(0)
        timelst = os.listdir(dir_path + '/' + proj_1 + '/' + procdir)
        for timedir in timelst:
            if timedir.isnumeric():
                lasttime[-1] = max(lasttime[-1], int(timedir))
lasttime = str(max(lasttime))

nproc0 = 0
proclst0 = os.listdir(dir_path + '/' + proj_0)
for procdir in proclst0:
    if procdir.startswith('processor'):
        nproc0 += 1
        bdfile = open(dir_path + '/' + proj_0 + '/' + procdir + '/' + 'patch_' + bdnm + '_constant.obj')
        Lines = bdfile.readlines()
        if len(Lines):
            txt = 'sets\n{\ntype sets;\nlibs ("libsampling.so");\nsetFormat ' + formt + ';\nfields (' + varnm + '); \
                    \ninterpolationScheme cellPoint;\nsets\n{\nmySet\n{\ntype cloud;\naxis xyz;\npoints\n(\n'
            for line in Lines:
                linesplit = line.split()
                txt += '(' + linesplit[1] + ' ' + linesplit[2] + ' ' + linesplit[3] + ')\n'
            txt += ');\n}\n}\n}'
            f = open(dir_path + '/' + proj_1 + '/system/sets', 'w')
            f.write(txt)
            f.close()
            os.system('cd ' + dir_path + '/' + proj_1 + '; srun --mpi=pmix -K1 --resv-ports -n ' + str(nproc1) + ' postProcess -func sets -time ' + lasttime + ' -parallel')
            nonuniformList = []
            with open(dir_path + '/' + proj_1 + '/postProcessing/sets/' + lasttime + '/mySet_p.csv', newline='') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=',')
                for row in csvreader:
                    if csvreader.line_num > 1:
                        nonuniformList.append(row[3])
            nlst = len(nonuniformList)
            txt = 'value nonuniform List<scalar>\n' + str(nlst) + '\n(\n'
            for p in nonuniformList:
                txt += p + '\n'
            txt += ')\n;'
            f = open(dir_path + '/' + proj_0 + '/' + procdir + '/0/' + varnm, "r")
            nwfile = []
            ininlet = False
            while True:
                content = f.readline()
                if content:
                    nwfile.append(content)
                    if bdnm in content:
                        while True:
                            content = f.readline()
                            if 'value' in content:
                                nwfile.append(txt)
                            else:
                                nwfile.append(content)
                            if '}' in content:
                                break
                else:
                    break
            f.close()
            f = open(dir_path + '/' + proj_0 + '/' + procdir + '/0/' + varnm, "w")
            f.write(''.join(nwfile))
