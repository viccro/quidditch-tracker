import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pandas as pd
import matplotlib.style as style
import pylab
import datetime as dt
from numpy import arange
import paths

# Colorblind-friendly colors
colors = ['#000000', '#E69F00', '#56B4E9', '#009E73',
          '#D55E00', '#0072B2', '#ff0000', '#ffa500', 
          '#ffff00', '#008000', '#0000ff', '#ee82ee']
yellow = '#E69F00'
green = '#56B4E9'
black = '#000000'

bg_color = "xkcd:bluegrey"
text_color = "#f0f0f0"

plot_file_debug = paths.local_directory + "plot-debug.png"

def plot_distance_over_time(data_by_team, start_time, debug_mode, graph_name, file_path, end_time=None):
    print("Plotting distances over time")
    data_frame = pd.DataFrame(data = data_by_team)
    draw_plot(data_frame, start_time, debug_mode, graph_name, file_path, end_time)


def draw_plot(data_frame, start_time, debug_mode, graph_name, file_path, end_time):
    style.use('fivethirtyeight')
    fig, ax = plt.subplots(facecolor=bg_color)
    graph = data_frame.plot(figsize=(6, 4), color=colors, ax=ax, linewidth=3, marker="o", markersize=0)
    ax.set_title(graph_name, color=text_color)
    ax.set_facecolor(bg_color)
    ax.set_clip_on(False)
    ax.set_ylim(ymin=-0.1)
    ax.set_ylabel('Total Miles Run', color=text_color)
    ax.set_xlabel('Times in EST', color=text_color, fontsize=10)

    # Legend format
    plt.legend(loc=2, numpoints=1, bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize='xx-small')

    # Date formatting
    graph.tick_params(axis='both', which='major', labelsize=10)
    
    if not end_time or end_time > dt.datetime.now():
        end_time = dt.datetime.now() + dt.timedelta(minutes=60)
    ax.set_xlim(start_time, end_time)

    days = dates.DayLocator()
    ax.xaxis.set_major_locator(days)
    majorFormatter = dates.DateFormatter("%m/%d")
    ax.xaxis.set_major_formatter(majorFormatter)

    minorFormatter = dates.DateFormatter("%I%p")
    ax.xaxis.set_minor_formatter(minorFormatter)
    hours = dates.HourLocator(arange(2, 25, 2))
    ax.xaxis.set_minor_locator(hours)

    plt.setp(ax.xaxis.get_majorticklabels(), rotation='vertical', fontsize=12, ha='center')
    plt.setp(ax.xaxis.get_minorticklabels(), rotation='vertical', fontsize=8)
    plt.grid(which='minor')

    #fig.autofmt_xdate()

    if debug_mode:
        print("Saving plot to " +  paths.local_directory + 'plot-debug.png')
        pylab.savefig( plot_file_debug, bbox_inches='tight',
                      facecolor=fig.get_facecolor(), transparent=True)
    else:
        print("Saving plot to " +  file_path)
        pylab.savefig( file_path, bbox_inches='tight', facecolor=fig.get_facecolor(),
                      transparent=True)
    if debug_mode:
        plt.show()