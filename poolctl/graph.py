import matplotlib.pyplot as plt
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
    xtmax = len(x3)                     # how many records are there
#    print(xtmax)                        # show me
    itr = xtmax / 7                     # create an iteration value
#    print(itr)                          # show me
    xtlbase = []                        # initialize a new list
    stepval = 0                         # initialize a value to be incremented
    while stepval <= xtmax:              # start the 'while' loop
        xtlbase.append(x3[stepval])     # append to the list the stepval'th record
        stepval = stepval + int(itr)    # increment stepval by the itr amount
#        print(xtlbase)                  # show me
    axes.plot(x1, label='IN')
    axes.plot(x2, label='OUT')
    #axes.plot(x3, label='AIR')
    axes.set_ylim([0,100])
    axes.set_xticklabels(xtlbase)
    axes.set_ylabel('Degrees F')
    axes.set_xlabel('Time of Day')
    axes.legend()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)