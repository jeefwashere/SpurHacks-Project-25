### DEEPSEEK ###
import subprocess
import os
import platform
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file

# Loads the environment file
load_dotenv()

app = Flask(__name__)
# Constant for output file name
