# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 16:36:28 2015

Completes the milestone project for Data Incubator onboarding,
described in Day 8 of the 12-day preparation program.

Uses flask, bokeh, and heroku to display stock quotes for the last 
30 days of a user-entered stock. Data are pulled for the correct dates 
using Quandl's API. Handles bad requests and 404 errors.

No bells or whistles but it works!

@author: alhamood
"""

from flask import Flask, render_template, request, redirect
import requests
import simplejson as json
import pandas as pd
import time
import os
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.resources import INLINE
import sys
import logging

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route('/')
def main():
  return redirect('/index')  		
				
@app.route('/index')
def index():
  return render_template('index.html')
		
@app.route('/error')
def error():
  return render_template('error.html')
		
@app.route('/bad-request')
def bad_request():
  return render_template('bad-request.html')
		
@app.route('/show-plot',methods=['POST'])
def show_plot():
  ticker = request.form['ticker']	
  today_string = time.strftime("%x")
  today_list = today_string.split("/")
  year = int(today_list[2]) + 2000
  month = int(today_list[0])-1
  if month == 0:
    month = 12
    year -= year
  start_date=(str(year) + '-' + str(month) + '-' + today_list[1])	
  url = "https://www.quandl.com/api/v3/datasets/WIKI/" + ticker + ".json?start_date=" + start_date
  r = requests.get(url)
  if r.status_code == 404:
    return redirect('/error')
  if r.status_code == 400:
    return redirect('/bad-request')
  j = json.loads(r.text)
  data = pd.DataFrame(data=j['dataset']['data'], columns=j['dataset']['column_names'])
  data = data.set_index(['Date'])
  data.index = pd.to_datetime(data.index)
  output_file("test.html")
  p = figure(plot_width=400, plot_height=400, x_axis_type="datetime")
  p.line(data.index, data['Close'], line_width=2)		
  script, div = components(p)	
  return render_template('show-plot.css', name=j['dataset']['name'], stock=ticker, script=script, div=div)

	
if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))	
  app.run(host='0.0.0.0', port=port)

	