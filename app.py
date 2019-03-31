'''This example demonstrates embedding a standalone Bokeh document
into a simple Flask application, with a basic HTML web form.
To view the example, run:
    python simple.py
in this directory, and navigate to:
    http://localhost:5000
'''
from __future__ import print_function

import flask
from flask import Flask, render_template, request, redirect
from bokeh.embed import json_item
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.resources import CDN
from jinja2 import Template
import requests as re
import pandas as pd
import numpy as np
import simplejson as json
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

app = flask.Flask(__name__)

#colors = {
#    'Black': '#000000',
#    'Red':   '#FF0000',
#    'Green': '#00FF00',
#    'Blue':  '#0000FF',
#}

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

@app.route("/")
def polynomial():
    """ Very simple embedding of a polynomial chart
    """
    # Grab the inputs arguments from the URL
    args = flask.request.args

    # Get all the form arguments in the url with defaults
#    color = getitem(args, 'color', 'Black')
#    _from = int(getitem(args, '_from', 0))
#    to = int(getitem(args, 'to', 10))
    user_symbol = str(getitem(args, 'Stock Symbol', "FB"))

    # Get the data to plot
    geturl = 'https://www.quandl.com/api/v3/datasets/WIKI/'+user_symbol+'/data.json?api_key=xcpuajeyffeoNLoSEozx'
    r = re.get(geturl)
    json_data = json.loads(r.content.decode('utf-8'))['dataset_data']
    df = pd.DataFrame(data=json_data['data'],columns=json_data['column_names'])
    dates = np.array(df['Date'][::-1],dtype='datetime64')
    close = np.array(df['Close'][::-1])
    source = ColumnDataSource(data=dict(date=dates, close=close))

    # Create a graph with those arguments
    fig = figure(plot_height=300, plot_width=800, tools="", toolbar_location=None,
      x_axis_type="datetime", x_axis_location="above",
      background_fill_color="#efefef", x_range=(dates[0], dates[1000]))

    fig.line('date', 'close', source=source)
    fig.yaxis.axis_label = 'Closing Price'

#    x = list(range(_from, to + 1))
#    fig = figure(title="Polynomial")
#    fig.line(x, [i ** 2 for i in x], color=colors[color], line_width=2)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(fig)
    html = flask.render_template(
        'embed.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
#        color=color,
#        _from=_from,
#        to=to,
        user_symbol=user_symbol
    )
    return encode_utf8(html)

if __name__ == "__main__":
    print(__doc__)
    app.run()
