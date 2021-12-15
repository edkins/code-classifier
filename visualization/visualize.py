def _pyplot_stuff(x, y, names):
    import matplotlib.pyplot as plt
    import numpy as np

    norm = plt.Normalize(1,4)

    fig,ax = plt.subplots()
    sc = plt.scatter(x,y,norm=norm)

    annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):

        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))),
                               " ".join([names[n] for n in ind["ind"]]))
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor('#ccc')
        annot.get_bbox_patch().set_alpha(0.4)


    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()


def do_visualization(ssh_profile):
    import json
    import subprocess
    from matplotlib import pyplot as plt

    def hover(event):
        print(event)

    subprocess.run(['rsync','-r',f'{ssh_profile}:~/output.json','output.json'])

    with open('output.json') as f:
        data = json.load(f)

    _pyplot_stuff(data['x'], data['y'], data['labels'])

def make_html(ssh_profile):
    import json
    import subprocess
    subprocess.run(['rsync','-r',f'{ssh_profile}:~/output.json','output.json'])
    with open('output.json') as f:
        data = json.load(f)

    with open('visualization/template.t') as f:
        text = f.read().replace('{{data}}', json.dumps(data, indent=4))

    with open('output.html', 'w') as f:
        f.write(text)
