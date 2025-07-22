#!/bin/bash
#SBATCH -J of                                    #Job name
#SBATCH -p normal_q                              #Partition requested
#SBATCH --nodes=1                                #Request exclusive access to all resources on 1 node
#SBATCH --ntasks-per-node=128
#SBATCH --threads-per-core=1                     #1 threads per core
#SBATCH --time=WALLTIME                          #Time limit
#SBATCH --account=are_diagnost
#SBATCH --output=zslurm                          #file for batch script's standard output
#SBATCH --exclusive

##--------------------------- Load Module--------------------------------------##
module reset                                     #reset module
module load OpenFOAM/v2406-foss-2023a
source $FOAM_BASH

##--------------------------- Case set --------------------------------------##
source parms
echo -e "Simulation case: set$setid--saturated\n" > zlog_cmd

echo "Case parameter setting" >> zlog_cmd

cp ../../../data/set$setid/stl/solid.stl constant/triSurface/wallFluidSolid.stl
cp ../../../data/set$setid/stl/"$caseid"_phases.stl constant/triSurface/wallFluidFluid.stl

bb="$(surfaceCheck constant/triSurface/wallFluidSolid.stl -outputThreshold 0 | grep 'Bounding Box')"
bb_arr=$(echo $bb | tr -dc '.[:space:][:digit:]-')
x0="`echo $bb_arr | cut -d' ' -f1`"
y0="`echo $bb_arr | cut -d' ' -f2`"
x1="`echo $bb_arr | cut -d' ' -f4`"
y1="`echo $bb_arr | cut -d' ' -f5`"
z0=-0.5
z1=0.5
lx="`echo "$x1 - $x0" | bc -l`"
ly="`echo "$y1 - $y0" | bc -l`"
x_cells="`echo "($lx + $buff) * $discr" | bc -l`"
x_cells="`printf "%.0f\n" $(bc <<< $x_cells)`"
y_cells="`echo "$ly * $discr" | bc -l`"
y_cells="`printf "%.0f\n" $(bc <<< $y_cells)`"
x0_full="`echo "$x0" | bc -l`"
x1_full="`echo "$x1 + $buff" | bc -l`"
buffvol=$(awk -v buff="$buff" -v ly="$ly" -v scxy="$scale_xy" -v scz="$scale_z" 'BEGIN{printf("%.15G",buff*ly*scxy*scxy*scz)}')
medvol=$(awk -v lx="$lx" -v ly="$ly" -v scxy="$scale_xy" -v scz="$scale_z" 'BEGIN{printf("%.15G",lx*ly*scxy*scxy*scz)}')

foamDictionary constant/flowParms -entry mediumVolume -set "$medvol" -precision 15
foamDictionary constant/flowParms -entry bufferVolume -set "$buffvol" -precision 15
foamDictionary system/blockMeshDict -entry vertices -set "( ($x0_full $y0 $z0) ($x1_full $y0 $z0) ($x1_full $y1 $z0) ($x0_full $y1 $z0) ($x0_full $y0 $z1) ($x1_full $y0 $z1) ($x1_full $y1 $z1) ($x0_full $y1 $z1) )"
foamDictionary system/blockMeshDict -entry blocks -set "( hex ( 0 1 2 3 4 5 6 7 ) ( $x_cells $y_cells 1 ) simpleGrading ( 1 1 1 ) )"

echo -e "Finish case parameters setting\n" >> zlog_cmd

##--------------------------- Meshing --------------------------------------##
rm -r constant/polyMesh
rm -r processor*

# meshing
echo "Starting blockMesh..." >> zlog_cmd                    
blockMesh > zlog_meshing 2>&1                                      # blockMesh
echo -e "Finish blockMesh\n" >> zlog_cmd

echo "Starting decomposePar..." >> zlog_cmd 
foamDictionary system/decomposeParDict -entry numberOfSubdomains -set $SLURM_NTASKS
decomposePar -copyZero >> zlog_meshing 2>&1                        # decompose parallel   
echo -e "FinishdecomposePar\n" >> zlog_cmd

echo "Starting snappyHexMesh..." >> zlog_cmd     
srun --mpi=pmix -K1 --resv-ports -n $SLURM_NTASKS snappyHexMesh -overwrite -parallel >> zlog_meshing 2>&1     # snappyHexMesh
echo -e "Finish snappyHexMesh\n" >> zlog_cmd

echo "Starting transformPoints..." >> zlog_cmd     
srun --mpi=pmix -K1 --resv-ports -n $SLURM_NTASKS transformPoints -scale "($scale_xy $scale_xy $scale_z)" -parallel >> zlog_transform 2>&1     # transformPoints
echo -e "Finish transformPoints\n" >> zlog_cmd

##--------------------------- simpleHeleShaw --------------------------------------##
for d in processor*; do
    cp 0/U $d/0/U; cp 0/p $d/0/p
    test -f $d/constant/flowParms && rm $d/constant/flowParms
done

echo "Running writeMeshObj" >> zlog_cmd
srun --mpi=pmix -K1 --resv-ports -n $SLURM_NTASKS writeMeshObj -constant -parallel >> zlog_MeshObj 2>&1     # writeMeshObj
echo -e "Finish writeMeshObj\n" >> zlog_cmd

echo "Copy boundary condition" >> zlog_cmd
parentdir="$(dirname `pwd`)"
python3 ../../../sample.py $parentdir flow flow_b >> zlog_PythonBC 2>&1                   # Python copy boundary condition
echo -e "Finish copy boundary condition\n" >> zlog_cmd

echo "Running simpleHeleShaw" >> zlog_cmd
srun --mpi=pmix -K1 --resv-ports -n $SLURM_NTASKS simpleHeleShaw -parallel >> zlog_flow 2>&1     # simpleHeleShaw
echo -e "Finish transformPoints\n" >> zlog_cmd

cp processor0/constant/flowParms constant/
for d in processor*; do
    test -f $d/constant/flowParms && rm $d/constant/flowParms
done

echo "Finish Simulation" >> zlog_cmd

