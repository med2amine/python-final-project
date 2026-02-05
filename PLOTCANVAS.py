import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')

        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#f8f9fa')
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setParent(parent)

        # Color schemes
        self.primary_color = '#3498db'
        self.secondary_color = '#2ecc71'
        self.accent_color = '#e74c3c'
        self.palette = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']

    def _style_axes(self, title=""):
        """Apply consistent styling to axes"""
        self.ax.set_title(title, fontsize=14, fontweight='bold',
                          color='#2c3e50', pad=20)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#95a5a6')
        self.ax.spines['bottom'].set_color('#95a5a6')
        self.ax.tick_params(colors='#7f8c8d', labelsize=9)
        self.ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.8)

    def clear_plot(self):
        """Clear the current plot"""
        self.ax.clear()
        self.draw()

    def plot_histogram(self, data, bins=20, title="Histogram"):
        """Plot a modern histogram with enhanced styling"""
        self.ax.clear()

        # Plot histogram with gradient effect
        n, bins_edge, patches = self.ax.hist(data, bins=bins,
                                             edgecolor='white',
                                             linewidth=1.2,
                                             alpha=0.85)

        # Apply gradient coloring to bars
        cm = plt.cm.viridis
        bin_centers = 0.5 * (bins_edge[:-1] + bins_edge[1:])
        col = bin_centers - min(bin_centers)
        col /= max(col)

        for c, p in zip(col, patches):
            plt.setp(p, 'facecolor', cm(c))

        self.ax.set_xlabel("Values", fontsize=11, fontweight='bold', color='#34495e')
        self.ax.set_ylabel("Frequency", fontsize=11, fontweight='bold', color='#34495e')

        # Add statistics annotation
        mean_val = data.mean()
        median_val = data.median()
        self.ax.axvline(mean_val, color='#e74c3c', linestyle='--',
                        linewidth=2, label=f'Mean: {mean_val:.2f}')
        self.ax.axvline(median_val, color='#f39c12', linestyle='--',
                        linewidth=2, label=f'Median: {median_val:.2f}')
        self.ax.legend(fontsize=9, framealpha=0.9)

        self._style_axes(title)
        self.fig.tight_layout()
        self.draw()

    def box_plot(self, data_list, labels=None, title="Box Plot"):
        """Plot enhanced box plot with colors"""
        self.ax.clear()

        bp = self.ax.boxplot(data_list, labels=labels, patch_artist=True,
                             notch=True, showmeans=True,
                             meanprops=dict(marker='D', markerfacecolor='red',
                                            markersize=6))

        # Color the boxes
        for patch, color in zip(bp['boxes'], self.palette):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Style whiskers and caps
        for whisker in bp['whiskers']:
            whisker.set(linewidth=1.5, linestyle='--', color='#7f8c8d')
        for cap in bp['caps']:
            cap.set(linewidth=2, color='#34495e')
        for median in bp['medians']:
            median.set(linewidth=2.5, color='#c0392b')

        self.ax.set_ylabel("Values", fontsize=11, fontweight='bold', color='#34495e')
        if labels:
            self.ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)

        self._style_axes(title)
        self.fig.tight_layout()
        self.draw()

    def scatter(self, x_data, y_data, title="Scatter Plot", x_label="X", y_label="Y"):
        """Plot enhanced scatter plot with trend line"""
        self.ax.clear()

        # Main scatter plot with gradient
        scatter = self.ax.scatter(x_data, y_data, alpha=0.6, s=50,
                                  c=range(len(x_data)), cmap='viridis',
                                  edgecolors='white', linewidth=0.5)

        # Add trend line
        z = np.polyfit(x_data, y_data, 1)
        p = np.poly1d(z)
        self.ax.plot(x_data, p(x_data), "--", color='#e74c3c',
                     linewidth=2, alpha=0.8, label=f'Trend: y={z[0]:.2f}x+{z[1]:.2f}')

        # Calculate and display correlation
        corr = np.corrcoef(x_data, y_data)[0, 1]
        self.ax.text(0.05, 0.95, f'r = {corr:.3f}',
                     transform=self.ax.transAxes,
                     fontsize=11, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        self.ax.set_xlabel(x_label, fontsize=11, fontweight='bold', color='#34495e')
        self.ax.set_ylabel(y_label, fontsize=11, fontweight='bold', color='#34495e')
        self.ax.legend(fontsize=9)

        # Add colorbar
        cbar = self.fig.colorbar(scatter, ax=self.ax)
        cbar.set_label('Data Point Index', rotation=270, labelpad=15)

        self._style_axes(title)
        self.fig.tight_layout()
        self.draw()

    def bar_chart(self, categories, values, title="Bar Chart"):
        """Plot modern bar chart with enhanced styling"""
        self.ax.clear()

        # Create bars with gradient colors
        colors_list = [self.palette[i % len(self.palette)] for i in range(len(categories))]
        bars = self.ax.bar(categories, values, color=colors_list,
                           edgecolor='white', linewidth=1.5, alpha=0.8)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{int(height)}',
                         ha='center', va='bottom', fontsize=9,
                         fontweight='bold', color='#2c3e50')

        self.ax.set_xlabel("Category", fontsize=11, fontweight='bold', color='#34495e')
        self.ax.set_ylabel("Count", fontsize=11, fontweight='bold', color='#34495e')
        self.ax.tick_params(axis='x', rotation=45)

        self._style_axes(title)
        self.fig.tight_layout()
        self.draw()

    def line_plot(self, x_data, y_data, title="Line Plot", x_label="X", y_label="Y"):
        """Plot enhanced line plot with area fill"""
        self.ax.clear()

        # Main line plot
        self.ax.plot(x_data, y_data, marker='o', linestyle='-',
                     markersize=6, linewidth=2.5, color=self.primary_color,
                     markerfacecolor='white', markeredgewidth=2,
                     markeredgecolor=self.primary_color, alpha=0.9)

        # Add area under curve
        self.ax.fill_between(x_data, y_data, alpha=0.2, color=self.primary_color)

        # Add max/min points
        max_idx = y_data.argmax()
        min_idx = y_data.argmin()
        self.ax.plot(x_data.iloc[max_idx], y_data.iloc[max_idx], 'r*',
                     markersize=15, label=f'Max: {y_data.iloc[max_idx]:.2f}')
        self.ax.plot(x_data.iloc[min_idx], y_data.iloc[min_idx], 'b*',
                     markersize=15, label=f'Min: {y_data.iloc[min_idx]:.2f}')

        self.ax.set_xlabel(x_label, fontsize=11, fontweight='bold', color='#34495e')
        self.ax.set_ylabel(y_label, fontsize=11, fontweight='bold', color='#34495e')
        self.ax.legend(fontsize=9, loc='best', framealpha=0.9)

        self._style_axes(title)
        self.fig.tight_layout()
        self.draw()

    def correlation_heatmap(self, data, title="Correlation Heatmap"):
        """Plot enhanced correlation heatmap"""
        self.ax.clear()

        corr = data.corr()
        im = self.ax.imshow(corr, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)

        # Set ticks
        self.ax.set_xticks(range(len(corr.columns)))
        self.ax.set_yticks(range(len(corr.columns)))
        self.ax.set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=9)
        self.ax.set_yticklabels(corr.columns, fontsize=9)

        # Add correlation values with smart coloring
        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                val = corr.iloc[i, j]
                # Choose text color based on background
                text_color = 'white' if abs(val) > 0.5 else 'black'
                text = self.ax.text(j, i, f'{val:.2f}',
                                    ha="center", va="center",
                                    color=text_color, fontsize=8,
                                    fontweight='bold')

        # Colorbar
        cbar = self.fig.colorbar(im, ax=self.ax)
        cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20, fontsize=10)

        self._style_axes(title)
        self.fig.tight_layout()
        self.draw()

    def save_plot(self, filepath, dpi=300):
        """Save the current plot with high quality"""
        self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                         facecolor='white', edgecolor='none')






