
#Vercel serves each file in api/ as one function; this one answers POST /api/news with the shared web handler
import os
import sys

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from web.server import DashboardHandler


class handler(DashboardHandler):
    pass
