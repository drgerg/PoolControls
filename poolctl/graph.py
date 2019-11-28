## graphy.py is called by poolGetSQL.py to create the graph 
## of pool water temperatures from the mySQL database

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import io
import base64
 
def build_graph(x1,x2,x3):
    img = io.BytesIO()
    fig = plt.figure()
    axes = fig.add_axes([0.1,0.1,0.8,0.8])
#
## I need to create x axis labels from the database dump.
## I have x3, which is the time values for the temp records in
## x1 and x2.
#
###   A HANDY LITTLE TOOL TO GET A .csv FILE FROM THE LIST
#
#    with open('output.csv','w') as out_file:
#        for row in x3:
#            print('{}'.format(row[0], ','.join(row[1:])), file=out_file)
###
#
    xtmax = len(x3)                     # how many records are there
    #print(xtmax)                        # show me
    itr = int(xtmax / 7)                # Divide the number of records by 7 to create an iteration value. Make it an integer.
    #print(itr)                          # show me
    xtltemp = []                        # initialize a temporary list 
    xtlbase = []                        # initialize the list for our final labels
    stepval = 0                         # initialize a value to be incremented
    while stepval <= xtmax - itr:       # start the 'while' loop to create the temporary list
        xtltemp.append(x3[stepval])     # append to the list the stepval'th record
        stepval = stepval + itr         # increment stepval by the itr amount
        #print(xtltemp)                      # show me
    for item in xtltemp:                # start a 'for' loop to build the final list
        xtlbase.append(item[11:16])     # slice off the first 11 characters and the last three
    xtlbase.append(x3[xtmax-1][11:16])  # add that last record (minus one)
    #print(xtlbase)                      # show me
    axes.plot(x1, label='IN')
    axes.plot(x2, label='OUT')
    axes.set_ylim([0,100])
    axes.xaxis.set_major_locator(ticker.LinearLocator(8))
    axes.set_xticklabels(xtlbase)
    axes.set_ylabel('Degrees F')
    axes.set_xlabel('Time of Day')
    axes.legend()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)
