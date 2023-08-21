from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
import matplotlib.patches as mpatches

COLORS = ['maroon', 'mediumorchid']
LABELS = ['Treatment', 'Control']

def plot_scatter(df1, df2, cord_map = {}, ax = None, trendline = False, xlabel = None, ylabel = None, title = None, color = None, label = None, treat_list = None, label_loc = None):

    if label_loc is None:
        label_loc = "center left"
        bbox = (1, 0.5)
    else:
        label_loc = "upper right"
        bbox = None


    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))

    if color is None:
        color = "tab:blue"

    for x, y, key in zip(df1, df2, df2.index):
        if key in cord_map.keys():
            ax.annotate(key, xy=(x, y), xytext=cord_map[key], textcoords='offset points')
            continue
        ax.annotate(key, xy=(x, y), xytext=(5, 0), textcoords='offset points')

    if treat_list:
        for i, treat in enumerate(treat_list):
            if treat == 1:
                ax.scatter(df1[i], df2[i], color = COLORS[0])
            else:
                ax.scatter(df1[i], df2[i], color = COLORS[1])
    else:
        if label:
            ax.scatter(  df1 , df2 , color = color, label = label)
            ax.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))
        else:
            ax.scatter(  df1 , df2 , color = color)


    # set title and labels in one line
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)

    if trendline:
        z = np.polyfit(df1, df2, 1)
        #print(np.)
        p = np.poly1d(z)
        
        #shamp = np.sort(p(df1))
        #shamp = p(df1)
        min_p = p(np.min(df1))
        max_p = p(np.max(df1))
        # reverse if trend is decreasing
        #if shamp[0] > shamp[-1]:
        #    shamp = shamp[::-1]

        trend = [min_p, max_p]
        xs = [np.min(df1), np.max(df1)]
        #trend = shamp
        # reverse trend 
        #trend = trend[::-1]
        #ax.plot(df1,  shamp, label ="d")
        ax.plot(xs,  trend,"--", color = "black", label = f"Trendline,  $R^2$ = {r2_score(df2,p(df1)):0.2f}")
        
        #ax.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))




    if treat_list:
        # get handles 
        handles = ax.get_legend_handles_labels()

        treat_patch = mpatches.Patch(color='maroon', label='Treatment')
        control_patch = mpatches.Patch(color='mediumorchid', label='Control')

        if trendline:
            handles = ax.get_legend_handles_labels()[0]

            #print([ handles])
            ax.legend(handles=[treat_patch, control_patch, handles[0]], loc = label_loc, bbox_to_anchor=bbox)
        else:
            # place legend to the right of the plot outside
            ax.legend(handles=[treat_patch, control_patch], loc = label_loc, bbox_to_anchor=bbox)