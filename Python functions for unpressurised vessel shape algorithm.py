#!/home/zm297/Python/bin/python
#
# shrinkage_functions.py
# information: this is a function bin which contains the functions called during the 
#              process of obtaining the pressure-free shape during mechanical analysis. 
#
# contains get_F_matrix, update_coordinates, write_new_datfile, clean_up_lst, GET_NEW_DAT


def get_F_matrix(row_number, F_by_nodes):
    #
    #
    # get the 3x3 deformation gradient matrix from the array F_by_nodes which is structured as # Fxx Fxy ...etc
    #
    # initialise
    import numpy as np
    F_out = np.zeros((3,3))
    row = F_by_nodes[row_number, :]

    # assign 
    F_out[0,0] = row[0] #xx
    F_out[0,1] = row[1] #xy
    F_out[0,2] = row[2] #xz
    F_out[1,0] = row[3] #yz
    F_out[1,1] = row[4] #yy
    F_out[1,2] = row[5] #yz
    F_out[2,0] = row[6] #xz
    F_out[2,1] = row[7] #zy
    F_out[2,2] = row[8] #zz

    return F_out
    #

def update_coordinates(alpha, S1, S, D, F_by_nodes, bad_nodes_list):

    # initialisations
    import numpy as np

    # initialise the new co-ordinate array. 
    lengths = S.shape
    n_rows = lengths[0]
    Snew = np.zeros(S.shape) # initialise the new co-ordinate array. 

    # initialise the counter.
    i = 0 
    
    residual = [] #initialise the residual. 
    while i < n_rows: 
        #
        # make the matrix of co-ordinates for this particular node. (x y z)'
        rowS  = np.r_[S[i,:]]
        xyzS = np.zeros((3,1))
        xyzS[0] = rowS[1]; xyzS[1] = rowS[2]; xyzS[2] = rowS[3]; 
   
        rowS1=  np.r_[S1[i,:]]
        rowD =  np.r_[D[i,:]]
        xyzS1=np.zeros((3,1))
        xyzD=np.zeros((3,1))
        xyzS1[0] = rowS1[1]; xyzS1[1] = rowS1[2]; xyzS1[2] = rowS1[3]; 
        xyzD[0] = rowD[1]; xyzD[1] = rowD[2]; xyzD[2] = rowS[3]; 
        

        if not i in bad_nodes_list:

            # get the deformation gradient matrix F
            F=get_F_matrix(i, F_by_nodes)
            # now perform the operation to update the new matrix xyzSnew
            matrixFt = np.matrix.transpose(F)
            matrixDS1 = xyzD - xyzS1
            difference=alpha*np.matmul(matrixFt, matrixDS1)

            # print(f'row {i} - difference between old and new is: {difference}')
             
            xyzSnew = xyzS - difference
	    #
            #... and calculate the residual.
            #frobenius norm
            frob_norm = np.linalg.norm(matrixDS1)
            residual.append(0.5*frob_norm*frob_norm)
	    #


            rowSnew = rowS
            rowSnew[0] = rowS[0] # node number.
            rowSnew[1] = xyzSnew[0] # x coordinate
            rowSnew[2] = xyzSnew[1] # y coordinate
            rowSnew[3] = xyzSnew[2] # z coordinate
            Snew[i,:] = rowSnew 
        
        i = i + 1 # update counter.
    # end of while loop
    avg_residual = sum(residual)/len(residual)
    return Snew, avg_residual
    #


 
def write_new_datfile(dat_out, dat_in, lst_in):
    #
    # open DAT solution file dat_in with read permissions.
    f = open(dat_in, "r")
    lines_dat = f.readlines()
    lines_dat_new = lines_dat


    # open LST input file with read permissions.
    g = open(lst_in, "r")
    lines_lst = g.readlines()

    #find idx_start which is the row which says: C***  NODAL POINT DATA.
    idx_start_dat = lines_dat.index('C***  NODAL POINT DATA\n')

    #find idx_end which is the row which says: C***  INITIAL CONDITIONS (end of nodal point data). 
    idx_end_dat = lines_dat.index('C***  INITIAL CONDITIONS\n')
 
    idx_replace_dat = idx_start_dat + 1  # row in DAT to replace. 
    lst_counter = 0 # count the first useful row in the LST file. 
	
    while idx_replace_dat < idx_end_dat:

        nodenum_dat = lines_dat[idx_replace_dat].split()[0]
        nodenum_lst = lines_lst[lst_counter].split()[0]

        line_replace_dat = lines_dat[idx_replace_dat]
        split_dat = line_replace_dat.split()

        line_replace_lst = lines_lst[lst_counter]
        split_lst = line_replace_lst.split()
        
        # wrote this small function to convert all numbers to floats (no E's...)
        # add significant figs to match the format of the original datfile.
        i = 0
        while i < len(split_lst):
            # split_lst[i] = str(float(split_lst[i]))
            split_lst[i]='{:#.13g}'.format(float(split_lst[i])) 
            i = i+1

        # if ordered correctly, node numbers should match up.
        # here i am just adding spaces etc so the new datfile has exact same formats as original.
        if float(nodenum_dat) == float(nodenum_lst):
            #updating datfile line with corresponding lst line. 

            nodenum_string = str(int(float(split_lst[0])))
            n_whitespaces = 10-len(nodenum_string)

            split_dat[0] = ' '*n_whitespaces + nodenum_string 
            split_dat[1] = ' ' + str(split_lst[1])
            split_dat[2] = '     ' + str(split_lst[2])
            split_dat[3] = '     ' + str(split_lst[3])
            split_dat[4] = '    ' + str(split_dat[4]) #space between last coord and first num on right.

            split_dat.append('\n')
            lines_dat_new[idx_replace_dat] = " ".join(split_dat)

        elif int(float(nodenum_lst)) == 0: #then it was one of the bad nodes in Snew.
            #in this case, lines_dat_new at this row = lines_dat (no change). 
            print(f'Did not update co-ordinates for node {nodenum_dat}')
        else:
            print(f'dat nodenumber is: {nodenum_dat}')
            print(f'lst nodenumber is: {nodenum_lst}')
            print(f'error while replacing datfile row: {idx_replace_dat}, which is line: {line_replace_dat}')
            print(f'the datfile line split is: {split_dat}, and the lstfile line split is: {split_lst}')
            print(f'the nodenum and lst num do not match...')
            print(f'dat line is: {split_dat} and lst: {split_lst}')
            return -1

        idx_replace_dat = idx_replace_dat + 3
        lst_counter = lst_counter + 1 

    # write new lines. 
    h = open(dat_out, 'w')
    h.writelines(lines_dat_new)

    # close the files which were opened.
    f.close()
    g.close()
    h.close()
    #


def clean_up_lst(infile,outfile):
    # open file to read.
    f=open(infile,'r')
    lines = f.readlines()

    #initialise the 'good lines' which do not have unnecessary information.
    # we only want to output a clean LST which is simply rows of: nodenum x y z . 
    good_lines = list()
    for line in lines: 
        split = line.split()
        if len(split) > 0 and split[0] == 'Node':
           split.append('\n')
           to_join = " ".join(split[1:len(split)])
           good_lines.append(to_join)
    f.close()
    if len(good_lines) > 0:
        g=open(outfile,'w')
        g.writelines(good_lines)
        g.close()

def find_bad_nodes(df_a_filename):
    f=open(df_a_filename,'r')
    lines_a = f.readlines()
    i=0
    # initialise bad nodes list.
    bad_nodes_list=[]
    while i < len(lines_a):
        line = lines_a[i]
        if 'NOT' in line or 'NaN' in line:
            print(f'we found a problem in the {i}th line!')
            split = line.split()

            # new line:
            lines_a[i] = split[0]+' '+split[1]+' '+split[2]+' '+split[3]+' '+'0 0 0\n'

            #append to the bad nodes list.
            bad_nodes_list.append(i)
        i=i+1
    f.close()
    g=open(df_a_filename,'w+')
    g.writelines(lines_a)
    g.close()
    return bad_nodes_list

def fill_in_array(ARRAY, bad_nodes_list):
    import numpy as np
    for row in bad_nodes_list:
        zero_row=np.zeros((1,9))
        # add this filler row. 
        ARRAY=np.insert(ARRAY, row, zero_row, 0)
    return ARRAY
