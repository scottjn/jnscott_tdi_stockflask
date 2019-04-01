from __future__ import print_function

import flask
from flask import Flask, render_template, request, redirect
from bokeh.embed import json_item, components
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import RangeTool, DatetimeTickFormatter
from bokeh.resources import CDN, INLINE
from bokeh.util.string import encode_utf8
from bokeh.layouts import widgetbox
from bokeh.models.widgets import Button, Dropdown, Select
from jinja2 import Template
from math import pi
import requests as re
import pandas as pd
import numpy as np
import simplejson as json

# Start the Flask
app = Flask(__name__)

# Use to set selection defaults in the Bokeh plot (will expand)
def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

@app.route("/")
def stock_plot():
    # Grab the inputs arguments from the URL
    args = flask.request.args

#    menu = [("Closing", "close"), ("Opening", "open"), ("High", "high"), ("Low", "low")]
#    dropdown = Dropdown(label="Select stock price to plot", button_type="warning", menu=menu)

#    def function_to_call(attr, old, new):
#        print dropdown.value

#    dropdown.on_change('value', function_to_call)
#    dropdown.on_click(function_to_call)
#    dropdown.value

    # Get all the form arguments in the url with defaults
    user_symbol = getitem(args, 'user_symbol', "GOOG")
#    plot_type = getitem(args, 'plot_type', "close")

    # Get the data to plot
    geturl = 'https://www.quandl.com/api/v3/datasets/WIKI/'+user_symbol+'/data.json?api_key=xcpuajeyffeoNLoSEozx'
    r = re.get(geturl)
    json_data = json.loads(r.content.decode('utf-8'))['dataset_data']
    df = pd.DataFrame(data=json_data['data'],columns=json_data['column_names'])

    dates = np.array(df['Date'][::-1],dtype='datetime64')
    open = np.array(df['Open'][::-1])
    high = np.array(df['High'][::-1])
    low = np.array(df['Low'][::-1])
    close = np.array(df['Close'][::-1])
    source = ColumnDataSource(data=dict(dates=dates, close=close))
 
    # Working to add buttons to allow switching between prices
    text = "Closing"

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    # Create a graph with those arguments
    fig = figure(plot_height=300, plot_width=800, tools=TOOLS, toolbar_location="right",
      x_axis_type="datetime", x_axis_location="below",
      background_fill_color="#efefef", x_range=(dates[len(dates)-31], dates[len(dates)-1]),
      y_range=(np.min(close[len(dates)-31:len(dates)-1:1])*0.95,np.max(close[len(dates)-31:len(dates)-1:1])*1.05))
    fig.line('dates', 'close', source=source)
    fig.yaxis.axis_label = text+" Price (in USD)"
    fig.xaxis.formatter=DatetimeTickFormatter(
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
        )
    fig.xaxis.major_label_orientation = pi/4

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(fig)

    html = flask.render_template(
        'embed.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        user_symbol=user_symbol
    )
    return encode_utf8(html)

if __name__ == "__main__":
    print(__doc__)
    app.run()
