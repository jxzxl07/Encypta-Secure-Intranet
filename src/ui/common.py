"""Common imports used by the PyQt window modules."""

import base64
import collections
import json
import math
import os
import random
import re
import smtplib
import socket
import sqlite3
import struct
import sys
import threading
import time
import traceback
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple

import cv2
import numpy as np
import pyaudio
from PyQt5 import QtCore
from PyQt5.QtCore import Q_ARG, QDateTime, QMetaObject, QObject, QThread, QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QIcon, QImage, QPixmap
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..config import (
    CALL_AUDIO_PORT,
    CALL_SIGNAL_PORT,
    CONNECTION_PORT,
    DB_PATH,
    DIRECT_FILE_PORT,
    DIRECT_MESSAGE_PORT,
    GROUP_PORT,
    VIDEO_SIGNAL_PORT,
    asset_path,
)
