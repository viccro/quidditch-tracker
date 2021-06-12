import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pandas as pd
import matplotlib.style as style
import pylab
import datetime as dt
from numpy import arange
import paths

mpl.use('TkAgg')
# Colorblind-friendly colors
colors = [[0,0,0], [230/255,159/255,0], [86/255,180/255,233/255], [0,158/255,115/255],
          [213/255,94/255,0], [0,114/255,178/255]]
yellow = [230/255,159/255,0]
green = [86/255,180/255,233/255]
black = [0,0,0]

bg_color = "xkcd:bluegrey"
text_color = "#f0f0f0"

plot_path = paths.local_directory
plot_file_debug = paths.local_directory + "plot-debug.png"
plot_file = paths.local_directory + "local.png"


def plot_distance_over_time(data_by_team, debug_mode):
    print("Plotting distances over time")
    data_frame = pd.DataFrame(data = data_by_team)
    draw_plot(data_frame, debug_mode)

def bin_by_hour(data_by_team):
    print("Plotting miles binned by hour")

    pass

def dist_between_teams(data_by_team):
    print("Plotting diffs over time")
    pass

def draw_plot(data_frame, debug_mode):
    style.use('fivethirtyeight')
    fig, ax = plt.subplots(facecolor=bg_color)
    graph = data_frame.plot(figsize=(6, 4), color=colors, ax=ax, linewidth=3, marker="o", markersize=0)
    ax.set_title("Total Mileage Over Time", color=text_color)
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
    datemin = dt.datetime(2018, 4, 9, 12, 0)
    datenow = dt.datetime.now()
    raceDuration = datenow - datemin
    datemax = datenow + dt.timedelta(minutes=60)
    ax.set_xlim(datemin, datemax)

    days = dates.DayLocator()
    days.MAXTICKS = 2000
    ax.xaxis.set_major_locator(days)
    majorFormatter = dates.DateFormatter("%m/%d")
    ax.xaxis.set_major_formatter(majorFormatter)

    minorFormatter = dates.DateFormatter("%I%p")
    ax.xaxis.set_minor_formatter(minorFormatter)
    hours = dates.HourLocator(arange(2, 25, 2))
    hours.MAXTICKS = 2000
    ax.xaxis.set_minor_locator(hours)

    plt.setp(ax.xaxis.get_majorticklabels(), rotation='vertical', fontsize=12, ha='center')
    plt.setp(ax.xaxis.get_minorticklabels(), rotation='vertical', fontsize=8)
    plt.grid(which='minor')

    #fig.autofmt_xdate()

    if debug_mode:
        print("Saving plot to " +  plot_file_debug)
        pylab.savefig( plot_file_debug, bbox_inches='tight',
                      facecolor=fig.get_facecolor(), transparent=True)
    else:
        print("Saving plot to " +  plot_file)
        pylab.savefig( plot_file, bbox_inches='tight', facecolor=fig.get_facecolor(),
                      transparent=True)
    if debug_mode:
        plt.show()