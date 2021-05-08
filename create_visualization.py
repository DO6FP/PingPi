#!/usr/bin/python3

def create_plot(t_list, value_list, filename, color_levels, ylabel, high_value_is_good):
  """
  Create a colored plot of the given data and create a png file of it.
  :param t_list:             list time stamps, given as datetime.datatime objects
  :param value_list:         the actual values to plot
  :param filename:           the resulting plot file 
  :param color_levels:       a list of 5 values that are used to color the value range
  :param ylabel:             label of the y axis
  :param high_value_is_good: boolean value whether high values get the green color and low values the red color or vice-versa
  """

  import sys,os
  import time
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  from matplotlib.collections import LineCollection
  from matplotlib.colors import ListedColormap, BoundaryNorm
  import matplotlib.dates as mdates
  import matplotlib.units as munits
  import numpy as np
  import datetime
  import timeit

  N = 20   # length of moving average

  # prepare matplotlib
  converter = mdates.ConciseDateConverter()
  munits.registry[np.datetime64] = converter
  munits.registry[datetime.date] = converter
  munits.registry[datetime.datetime] = converter

  fig = plt.figure(figsize=(18,8))
  ax = fig.add_subplot(111)
  
  # plot dot markers of individual values
  ax.plot(t_list, value_list, color="grey", marker="+", linestyle="None", zorder=1)

  # plot moving average
  if len(value_list) > N:
    # compute moving average
    value_list_moving_average = np.convolve(value_list, np.ones(N)/N, mode='valid')
    inxval = mdates.date2num(t_list[N-1:])
    points = np.array([inxval, value_list_moving_average]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # prepare color map
    if high_value_is_good:
      cmap = ListedColormap(['r', 'y', 'g', 'darkgreen'])
    else:
      cmap = ListedColormap(['darkgreen', 'g', 'y', 'r'])
    base_value = 0
    norm = BoundaryNorm(color_levels, cmap.N)
    lc = LineCollection(segments, cmap=cmap, norm=norm, zorder=10)
    lc.set_array(value_list_moving_average)
    lc.set_linewidth(2)
    line = ax.add_collection(lc)
    
    # add color map
    fig.colorbar(line, ax=ax)
    #plt.figtext(0.2, 0.92, "Latenz [ms]", ha="left")
    #plt.figtext(0.95, 0.92, "Latenz [ms]", weight="bold", ha="right")
    #plt.figtext(0.83, 0.2, "gut", color="darkgreen", weight="bold")
    #plt.figtext(0.83, 0.4, "mittel", color="g", weight="bold")
    #plt.figtext(0.83, 0.6, "mäßig", color="y", weight="bold")
    #plt.figtext(0.83, 0.8, "schlecht", color="r", weight="bold")
  

  # configure axes
  ax.set_xlim(t_list[0],t_list[-1]);
  ax.xaxis_date()
  ax.autoscale_view()
  ax.set_ylabel(ylabel)
  ax.grid(which="both")
  
  print("save to {}".format(filename))
  plt.savefig(filename)
  plt.close()
    
