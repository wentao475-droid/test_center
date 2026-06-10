# spider_plot.py
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib as mpl
import matplotlib.font_manager as fm

fe = fm.FontEntry(
    fname='/Users/qx211/Library/Fonts',
    name='Bell MT')
fm.fontManager.ttflist.insert(0, fe) # or append is fine
mpl.rcParams['font.family'] = fe.name # = 'your custom ttf font name'

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging

from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from textwrap import wrap


def generate_spider_plot(summary,loc='./'):
    logging.info("Entering generate_spider_plot function")
    logging.info(f"Summary keys: {summary.keys()}")

    num_of_topics = summary['num_of_topics']

    # Extract topic accuracies, converting to float if necessary
    TRACKS_N = []
    for i in range(1, num_of_topics + 1):
        key = f'topic{i}_accuracy'
        if key in summary:
            value = summary[key]
            if isinstance(value, str):
                try:
                    TRACKS_N.append(float(value))
                except ValueError:
                    logging.warning(f"Could not convert {key} value '{value}' to float")
                    TRACKS_N.append(0)  # or some default value
            else:
                TRACKS_N.append(float(value))
        else:
            logging.warning(f"Missing key in summary: {key}")
            TRACKS_N.append(0)  # or some default value

    TRACKS_N = np.array(TRACKS_N)

    logging.info(f"TRACKS_N: {TRACKS_N}")

    if len(TRACKS_N) == 0:
        logging.error("No valid topic accuracies found")
        # Create a default plot or return an error message
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No data available", ha='center', va='center')
        plt.axis('off')
        output_path = f"{summary['student_id']}_spider_plot.png"
        plt.savefig(output_path)
        plt.close(fig)
        return output_path

    # The rest of your function remains the same
    LENGTHS = TRACKS_N
    MEAN_GAIN = TRACKS_N

    # Values for the x axis
    ANGLES = np.linspace(0.05, 2 * np.pi - 0.05, num_of_topics, endpoint=False)

    GREY12 = "#1f1f1f"

    # Set default font to Bell MT
    plt.rcParams.update({"font.family": "Bell MT"})

    # Set default font color to GREY12
    plt.rcParams["text.color"] = GREY12

    # The minus glyph is not available in Bell MT
    # This disables it, and uses a hyphen
    plt.rc("axes", unicode_minus=False)

    # Colors
    # COLORS = ["#6C5B7B","#C06C84","#F67280","#F8B195"]
    if 'colors' in summary:
        COLORS = summary['colors']
    else:
        # COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]  # default colors
        COLORS = ["#9ca8aa","#ffb762","#576b7a","#9b9a9d","#2e3c52"]

    # Colormap
    cmap = mpl.colors.LinearSegmentedColormap.from_list("my color", COLORS, N=256)

    # Normalizer
    norm = mpl.colors.Normalize(vmin=TRACKS_N.min(), vmax=TRACKS_N.max())

    # Normalized colors. Each number of tracks is mapped to a color in the 
    # color scale 'cmap'
    COLORS = cmap(norm(TRACKS_N))

    REGION = [summary[f'topic{i}'] for i in range(1,num_of_topics+1)]

    # Some layout stuff ----------------------------------------------
    # Initialize layout in polar coordinates
    fig, ax = plt.subplots(figsize=(9, 12.6), subplot_kw={"projection": "polar"})

    # Set background color to white, both axis and figure.
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.set_theta_offset(1.2 * np.pi / 2)
    ax.set_ylim(-1, 100)

    # Add geometries to the plot -------------------------------------
    # See the zorder to manipulate which geometries are on top

    # Add bars to represent the cumulative track lengths
    ax.bar(ANGLES, LENGTHS, color=COLORS, alpha=0.9, width=0.52, zorder=10)

    # Add dashed vertical lines. These are just references
    ax.vlines(ANGLES, 0, 10, color=GREY12, ls=(0, (4, 4)), zorder=11)

    # Add dots to represent the mean gain
    ax.scatter(ANGLES, MEAN_GAIN, s=60, color=GREY12, zorder=11)


    # Add labels for the regions -------------------------------------
    # Note the 'wrap()' function.
    # The '5' means we want at most 5 consecutive letters in a word, 
    # but the 'break_long_words' means we don't want to break words 
    # longer than 5 characters.
    REGION = ["\n".join(wrap(r.replace('\\',''), 5, break_long_words=False)) for r in REGION]
    if summary.get('show_percentage', False):
        REGION = [r + '\n (' + str(round(acc, 2)) + '%)' for r, acc in zip(REGION, TRACKS_N)]

    # Set the labels
    ax.set_xticks(ANGLES)
    ax.set_xticklabels(REGION, size=12);

    # Remove unnecesary guides ---------------------------------------

    # Remove lines for polar axis (x)
    ax.xaxis.grid(False)

    # Put grid lines for radial axis (y) at 0, 1000, 2000, and 3000
    ax.set_yticklabels([])
    ax.set_yticks([0, 20, 40, 60, 80, 100])

    # Remove spines
    ax.spines["start"].set_color("none")
    ax.spines["polar"].set_color("none")

    XTICKS = ax.xaxis.get_major_ticks()
    for tick in XTICKS:
        tick.set_pad(10)

    width = 240/72.27
    height = width
    fig.set_size_inches(width, height)
    fig.savefig(loc+'spiderplot.pdf',dpi=400,bbox_inches='tight')

    output_path = loc+'spiderplot.pdf'
    logging.info("Exiting generate_spider_plot function")
    return output_path
