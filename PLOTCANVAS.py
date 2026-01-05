import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotCanvas(FigureCanvas):
    def __init__(self,parent=None,width=8,height=6,dpi=100):
        self.fig = Figure(figsize=(width,height),dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.setParent(parent)
