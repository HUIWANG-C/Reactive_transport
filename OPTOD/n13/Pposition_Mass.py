import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

output_dir="Pposition_Mass"
os.makedirs(output_dir, exist_ok=True)

N=100000

Xmin=3.06666e-05
Xmax=0.116008
Ymin=0.
Ymax=0.072956

#******** Automatically detect the file containing 'position_M'*************#
directory = '.'  # Current directory
file_path = None
for filename in os.listdir(directory):
    if 'position_M' in filename and filename.endswith('.dat'):
        file_path = os.path.join(directory, filename)
        break
if file_path is None:
    print("No file found with 'position_M' in the name.")
    exit()
print(f"Using file: {file_path}")

#******************* Read data from position...dat ***********************************************#
pd.set_option('display.unicode.east_asian_width', True) #solve the problem of out of order
Pposition = pd.read_table(file_path, skiprows=1, header=None, sep=r'\s+')  # read data file
#the data is constructed repeatedly every timestep (Time Tag Position_0 Position_1 Mass)
print(Pposition.head())       #output the first 5 line
bg_img = mpimg.imread("/home/huiwang/1_HeleShawRT/zFlow1e-4/n13/flow_b/drawcluster4_cut.png")   # Load the background image
Time=Pposition.iloc[:,0]                 # extract the first column, time

#******************* Loop data and draw ***********************************************#
for i in range(len(Time)):               # loop each time step and draw particle distribution
    partile=Pposition.iloc[i]            # extract ith row
    print(partile)
    Position_0=[]                        # define two empty lists to store particle x, y position
    Position_1=[]
    Mass=[]

    x = 2                                # extract and append Position_0
    while x < len(partile):              # Iterate while within bounds
        Position_0.append(partile[x])    # Append value
        x += 4                           # Move 4 steps forward
    print(Position_0)                    # Print the extracted values

    y = 3                                # extract and append Position_1
    while y < len(partile):
        Position_1.append(partile[y])
        y += 4
    print(Position_1)

    m = 4
    while m < len(partile):              # Iterate while within bounds
        Mass.append(partile[m])          # Append value
        m += 4                           # Move 4 steps forward
    print(Mass)                          # Print the extracted values

    Mass_normalized = [m / (1 / N) for m in Mass]     # nomolise the particle by its initial mass

    plt.imshow(bg_img, extent=[Xmin, Xmax, Ymin, Ymax], aspect='auto')  # place the background image correctly
    plt.scatter(Position_0, Position_1, c=Mass_normalized, cmap='plasma', vmin=0, vmax=1, s=0.3)                               # draw particle position
    plt.colorbar(label='Normalized Particle Mass', shrink=0.6, aspect=20)

    #**************** we set the font of label and legend ********************#
    rc = {"font.family": "serif", "mathtext.fontset": "cm"}
    plt.rcParams.update(rc)
    plt.rcParams['font.family'] = ['serif']
    plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
    font_label = {'family': 'Times New Roman', 'size': 15, 'style': 'italic'}
    font_legend = {'family': 'Times New Roman', 'size': 10, 'style': 'italic'}

    plt.xlabel(r'$X$', font_label)
    plt.ylabel(r'$Y$', font_label)
    plt.xlim(Xmin,Xmax)
    plt.ylim(Ymin,Ymax)
    plt.gca().set_aspect(1)
    #plt.legend(['L=20d','L=40d']
     #          ,loc='lower right',markerscale=1,prop=font_legend,frameon=True)
    plt.savefig(os.path.join(output_dir, 'Position'+str(Time[i])+'.png'), dpi=200, bbox_inches='tight', format='png')
    #plt.savefig('Draw_caviy_depth.pdf', dpi=500, bbox_inches='tight', format='pdf')
    #plt.show()

    plt.clf()
print("Image generation completed")
