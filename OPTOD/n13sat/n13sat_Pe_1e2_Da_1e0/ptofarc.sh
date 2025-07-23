#!/bin/bash
#SBATCH -J PTOF                                  #Job name
#SBATCH -p normal_q                              #Partition requested
#SBATCH --ntasks=1                               #One MPI task
#SBATCH --cpus-per-task=8                        #Number of threads
#SBATCH --threads-per-core=1                     #1 threads per core
#SBATCH --time=144:00:00                         #Walltime
#SBATCH --account=are_diagnost
#SBATCH --output=stdout                          #file for batch script's standard output
#SBATCH --exclusive

##--------------------------- Load Module--------------------------------------##
module reset                                     #reset module
module load OpenFOAM/v2406-foss-2023a
source $FOAM_BASH

##--------------------------- Define path --------------------------------------##

EXECUTABLE="/home/huiwang/PTOF_main/ParticleTrackingOF-main-040725/bin/release/ParticleTrackingOF_parallel_advection_diffusion_surface_decay_2d"
CASE_DIR="../"  # One level up from the current working directory
CASE_NAME=$(basename "$PWD")  # Get current directory name
TRANSPORT="Pe_1e2"
REACTION="Da_1e0"
SOLVER="1e-1_1e-3_1e5"
INITIAL="fluxweighted"
OUTPUT="moments_breakthrough_mass_1e-3"
#OUTPUT="moments_breakthrough_mass_position_1e-1"
OUTPUT_LOG="log"

# Run executable with the correct number of threads
srun $EXECUTABLE "$CASE_DIR" "$CASE_NAME" "$TRANSPORT" "$REACTION" "$SOLVER" "$INITIAL" "$OUTPUT" "" "" 0 "$SLURM_CPUS_PER_TASK" \
  > "$OUTPUT_LOG" 2>&1
