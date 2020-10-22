from flask import render_template, send_file

def index():
  return render_template('index.j2', title='Light CI/CD', devices=remote_control.get_devices())

def stylesheet():
  return send_file('files/stylesheet.css')

def main_js():
  return send_file('files/main.js')

def login():
  return send_file('templates/login.vue', mimetype = "text/html")
