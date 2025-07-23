#!/bin/bash
#SBATCH -J python_post               #Job name
#SBATCH -p normal_q                  #Partition requested
#SBATCH --ntasks=1                   #Request a single core
#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=1                     #1 threads per core
# #SBATCH --mem=256G                   # Request 256 GB memory for the job
#SBATCH --time=WALLTIME              #Time limit
#SBATCH --account=are_diagnost
#SBATCH --output=stdout              #file for batch script's standard output
#SBATCH --error=stderr               # Error file
#SBATCH --exclusive

##--------------------------- Load Module--------------------------------------##
module reset                                     #reset module
module load Miniconda3
module list

##--------------------------- Run python code--------------------------------------##
echo "start load env and run python"

source activate myPyenv
python Pposition_Mass.py


echo "Python Job Finished"
exit;

