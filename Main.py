import matplotlib.pyplot as plt
import scipy
import numpy as np
import csv
import os
import pandas as pd 

#----------------------GLOBAL VARIABLES------------------------
cross_sectional_area = 10.176
gauge_length = 9.53

def new_directory(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        print("Folder %s created!" % dir_name)
    else:
        print("Folder %s already exists" % dir_name)

def read_csv(csv_name):
    #this function will process the force displacement data in the named CSV file into an array

    #--------------INPUTS--------------------------------------------------------------------------------------
    #csv_name: the name of the CSV file that you want to read (**IMPORTANT: MUST BE IN THE SAME FOLDER AS MAIN**)
    global active_name
    active_name = csv_name
    #----------------------------------------------------------------------------------------------------------

    fileName = csv_name+".csv"
    new_directory(active_name)

    line_count = 0
    temp_displacement = []
    temp_force = []
    e_array = []

    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        sinusoid_count = 1 
        for row in csv_reader:            
            if line_count == 0:
                pass
            else:
                definer = list(row[1]) 
                #at index 1 we expect to see a string of the form int_word (e.g. 1_Stretch), but we only care if it is int_"stretch"
                #that is going to give us a character array "1","_","S","t","r","e","t","c","h"
                #definer[0] will tell us which cycle we're in (1-20)
                #definer[2] will be either S (we want this data) or P or R (we dont want this data)
                if sinusoid_count<10:
                    if definer[2] == "P" or definer[2] == "R":
                        pass
                    else:
                        #now we've determined we are in a stretch phase 
                        if int(definer[0])==sinusoid_count:
                            temp_displacement.append(float(row[4]))
                            temp_force.append(float(row[5]))
                            #add the force and displacement to the temp arrays
                        else:
                            #we're on a new sinusoid
                            e = find_e(temp_force, temp_displacement, sinusoid_count)
                            e_array.append(e)
                            print("youngs modulus for sinusoid", sinusoid_count, "is", e)
                            sinusoid_count = sinusoid_count+1
                            temp_displacement = []
                            temp_force = []
                            #so append the two arrays to our bigger array, empty them, and start brand new
                            #and then increment sinusoid_count
                else:
                    if definer[3] == "P" or definer[3] == "R":
                        pass
                    else:
                        #now we've determined we are in a stretch phase 
                        if int(definer[0]+definer[1])==sinusoid_count:
                            temp_displacement.append(float(row[4]))
                            temp_force.append(float(row[5]))
                            #add the force and displacement to the temp arrays
                        else:
                            #we're on a new sinusoid
                            e = find_e(temp_force, temp_displacement, sinusoid_count)
                            e_array.append(e)
                            print("youngs modulus for sinusoid", sinusoid_count, "is", e)
                            sinusoid_count = sinusoid_count+1
                            temp_displacement = []
                            temp_force = []
                            #so append the two arrays to our bigger array, empty them, and start brand new
                            #and then increment sinusoid_count                    
            line_count += 1
        e = find_e(temp_force, temp_displacement, sinusoid_count)
        e_array.append(e)
        print("youngs modulus for sinusoid", sinusoid_count, "is", e)
        sinusoid_count = sinusoid_count+1
        print(f'Processed {line_count} lines.')
        print(e_array)
        pd.DataFrame(e_array).to_csv(active_name+"/"+active_name+'youngs modulus.csv')    

def find_e(force, displacement, sinusoid_count):
    #this function will process the force displacement data in the two arrays and return youngs modulus

    #--------------INPUTS----------------
    #force: an array of doubles represeting force in newtons
    #displacement: an array of doubles representing displacement in mm
    #------------------------------------
    print("force array length is", len(force), "displacement array length is", len(displacement))
    stress_array = []
    strain_array = []

    #find stress: force/cross sectional area
    #find strain: displacement/gauge length

    for i in range (len(displacement)):
        stress = displacement[i]/cross_sectional_area
        stress_array.append(stress)
    for i in range (len(force)):
        strain = force[i]/gauge_length
        strain_array.append(strain)

    stress_strain_plot(stress_array, strain_array, sinusoid_count)
    res = scipy.stats.linregress(stress_array, strain_array)
    return float(res[0])

def stress_strain_plot(stress, strain, sinusoid_count):
    
    plt.plot(strain, stress)
    plt.ylabel("Stress")
    plt.xlabel("Strain")
    plt.title("Stress-Strain Curve for Sinusoid Repetition #"+str(sinusoid_count))
    #save the plot
    plt.savefig(active_name+"/"+str(sinusoid_count)+".png")    
    plt.clf()


def main():  
    read_csv("20minuteCure_Sinuoid013Data")

main()

