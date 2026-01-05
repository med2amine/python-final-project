import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setParent(parent)

    def clear_plot(self):
        """Clear the current plot"""
        self.ax.clear()
        self.draw()

    def plot_histogram(self, data, bins=20, title="Histogram"):
        """Plot a histogram"""
        self.ax.clear()
        self.ax.hist(data, bins=bins, edgecolor='black', alpha=0.7)
        self.ax.set_title(title)
        self.ax.set_xlabel("Values")
        self.ax.set_ylabel("Frequency")
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.draw()

    def box_plot(self, data_list, labels=None, title="Box Plot"):
        """Plot a box plot for one or more columns"""
        self.ax.clear()
        self.ax.boxplot(data_list, labels=labels)
        self.ax.set_title(title)
        self.ax.set_ylabel("Values")
        if labels:
            self.ax.set_xticklabels(labels, rotation=45, ha='right')
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.draw()

    def scatter(self, x_data, y_data, title="Scatter Plot", x_label="X", y_label="Y"):
        """Plot a scatter plot"""
        self.ax.clear()
        self.ax.scatter(x_data, y_data, alpha=0.6)
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.draw()

    def bar_chart(self, categories, values, title="Bar Chart"):
        """Plot a bar chart"""
        self.ax.clear()
        self.ax.bar(categories, values, edgecolor='black', alpha=0.7)
        self.ax.set_title(title)
        self.ax.set_xlabel("Category")
        self.ax.set_ylabel("Count")
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.grid(True, alpha=0.3, axis='y')
        self.fig.tight_layout()
        self.draw()

    def line_plot(self, x_data, y_data, title="Line Plot", x_label="X", y_label="Y"):
        """Plot a line plot"""
        self.ax.clear()
        self.ax.plot(x_data, y_data, marker='o', linestyle='-', markersize=4)
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.draw()

    def correlation_heatmap(self, data, title="Correlation Heatmap"):
        """Plot a correlation heatmap"""
        self.ax.clear()
        corr = data.corr()
        im = self.ax.imshow(corr, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)

        self.ax.set_xticks(range(len(corr.columns)))
        self.ax.set_yticks(range(len(corr.columns)))
        self.ax.set_xticklabels(corr.columns, rotation=45, ha='right')
        self.ax.set_yticklabels(corr.columns)

        # Add correlation values as text
        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                text = self.ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                                    ha="center", va="center", color="black", fontsize=8)

        self.ax.set_title(title)
        self.fig.colorbar(im, ax=self.ax)
        self.fig.tight_layout()
        self.draw()

    def save_plot(self, filepath):
        """Save the current plot to a file"""
        self.fig.savefig(filepath, dpi=300, bbox_inches='tight')






