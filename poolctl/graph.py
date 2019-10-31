import matplotlib.pyplot as plt
import io
import base64
 
def build_graph(x1,x2,x3):
    img = io.BytesIO()
    fig = plt.figure()
    axes = fig.add_axes([0.1,0.1,0.8,0.8])

    axes.plot(x1, label='IN')
    axes.plot(x2, label='OUT')
    #axes.plot(x3, label='AIR')
    axes.set_ylim([0,100])
    axes.set_ylabel('Degrees F')
    axes.set_xlabel('Record Number')
    axes.legend()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)