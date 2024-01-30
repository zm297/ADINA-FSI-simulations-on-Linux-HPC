#!/home/zm297/Python/bin/python

#### PYTHON SCRIPT GET_NEW_DAT.py 

################################
#### preliminary housekeeping. #
################################

#### import libraries and functions
import sys
i=int(sys.argv[1]) #iteration number.
PID=sys.argv[2] #patient ID.
alpha=float(sys.argv[3]) #truncation factor.

f = open('simulation_log.out', 'a')
f.write(f'We are now in python.\n')  
f.write(f'Starting new DATFILE writing for iteration {i+1}...\n')  

#### we want to access functions from this directory...
sys.path.insert(1, '/home/zm297/rds/hpc-work/Mechanomics')
from shrinkage_functions import *
import numpy as np

#### clean up the current lst files
clean_up_lst(f'iter_{i}_S.lst',f'iter_{i}_S.lst')
clean_up_lst(f'iter_{i}_DF_a.lst',f'iter_{i}_DF_a.lst')
clean_up_lst(f'iter_{i}_DF_b.lst',f'iter_{i}_DF_b.lst')

######################################################################################
#### in this section we get the S, S1, D, and F matrices required for next iteration #
######################################################################################
####
#### get all the nodal coordinate arrays (# x y z) from these lst files. 
#### first initial co-ordinates (doesn't change with iterations) then current. shape = nnodes x 4.
S1 = np.genfromtxt('iter_1_S.lst')
S = np.genfromtxt(f'iter_{i}_S.lst')

#### you need to deal with NOT FOUNDs or NaN in the deformation gradient LST result. 
#### store these bad nodes using the clear_DF_a function.
#### bad node rows will not show up in the B matrix which is purely def gradient components,
#### whereas A contains co-ordinates and def gradient components in its columns. 
#### then get D=deformed nodenum x y z (nnodes by 4)
#### then, remove the bad-node rows from A. These obviously won't be in the F_by_nodes matrix.
#### B, since it only had deformation gradient components, will not have the bad node rows.

bad_nodes_list = find_bad_nodes(f'iter_{i}_DF_a.lst')
A = np.genfromtxt(f'iter_{i}_DF_a.lst')
B = np.genfromtxt(f'iter_{i}_DF_b.lst')
D = A[:,0:4] 
A = np.delete(A, bad_nodes_list, axis=0)

#### deformation gradient matrix. 
#### but in order for node accessing to match between S and F_by_nodes,
#### we need to insert zeros into F (which is A,B). A had these rows filled during find_bad_nodes
#### so we just need to fill these bad rows in B.
F_by_nodes = np.c_[A[:,4:7], B[:,1:]]
F_by_nodes = fill_in_array(F_by_nodes, bad_nodes_list)

#######################################################################
#### in this section we compute the new shape Snew, and the residual. #
#######################################################################
####
#### double check array shapes. F_by_nodes.shape = nnodes by 9. D.shape = nnodes by 4.
#### S.shape = nnodes by 4. A and B are ngoodnodes by 7
#### update new co-ordinates:
####
#### NOTE,IF THERE ARE CONVERGENCE/DISTORTED MESH ISSUES, RELAX ALPHA (REDUCE). 
#alpha = 1
#alpha=0.6
f.write(f'Writing new shape...\n')

Snew, residual = update_coordinates(alpha, S, S1, D, F_by_nodes, bad_nodes_list)

f.write(f'The residual (difference between current iteration ({i}) post-inflation co-ordinates and original co-ordinates) was {residual}.\n')


###################################################################################################
#### in this section we save the co-ordinates in an .npy file which can be used for visualisation #
###################################################################################################
####
#### at this point check the pt cloud view of these new co-ordinates. 
#### do below after moving S.npy from HPC to C:/Users/zakar/Downloads:
#### cd C:\Users\zakar\AppData\Local\Programs\Python\Python37\
#### python
#### from mechanomics_functions_bin import * ; import numpy as np; S1=np.load('C:/Users/zakar/Downloads/S_1.npy');D2=np.load('C:/Users/zakar/Downloads/D_2.npy');D1=np.load('C:/Users/zakar/Downloads/D_1.npy')
#### plot_point_cloud(S1[:,1:], D2[:,1:], np.array([[0,0,1]]), np.array([[1,0,0]]))
#### or: plot_point_cloud(S1[:,1:], D1[:,1:], np.array([[0,0,1]]), np.array([[1,0,0]]))
#### saving just the co-ordinates and new co-ordinates...
np.save(f'S_{i}', S)
np.save(f'D_{i}', D)
np.save(f'Snew_{i}', Snew)

#################################################
#### in this section we create the new DAT file #
#################################################
####
#### write new co-ordinates to new LST file.
#### this one will be created again by the Yuan PLO file. For now just keep it that way. 
#### then, use the new LST to create the new DAT file.
#### example: write_new_datfile('Test_2nd_Iteration.dat', 'Test_1st_Iteration.dat', f'iter_{i+1}_S.lst')

new_lst_name = f'iter_{i+1}_S.lst'
np.savetxt(f'{new_lst_name}', Snew)

#current_dat_name = f'Test_iter_{i}.dat'
#new_dat_name = f'Test_iter_{i+1}.dat'

current_dat_name = f'{PID}_Solid_dat_{i}.dat'
new_dat_name = f'{PID}_Solid_dat_{i+1}.dat'

f.write(f'Finished writing new DATFILE.\n')
write_new_datfile(new_dat_name, current_dat_name, new_lst_name)

##########################
### close the log file. ##
##########################
f.close()  # you can omit in most cases as the destructor will call it

####
####

