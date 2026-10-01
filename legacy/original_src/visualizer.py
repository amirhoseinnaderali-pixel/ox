"""
Real-time visualization module for optimizer
Displays iteration vs time, iteration vs memory, and history
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from collections import deque
from typing import Dict, List, Optional
import os
from datetime import datetime


class OptimizerVisualizer:
    """Real-time visualizer for optimizer progress"""
    
    def __init__(self, max_history: int = 1000, save_dir: str = "optimizer_plots"):
        """
        Initialize visualizer
        
        Args:
            max_history: Maximum number of data points to keep in memory
            save_dir: Directory to save plots
        """
        self.max_history = max_history
        self.save_dir = save_dir
        
        # Create save directory
        os.makedirs(save_dir, exist_ok=True)
        
        # Data storage
        self.iterations = deque(maxlen=max_history)
        self.execution_times = deque(maxlen=max_history)
        self.memory_usage = deque(maxlen=max_history)
        self.energy = deque(maxlen=max_history)
        self.accepted = deque(maxlen=max_history)
        self.is_best = deque(maxlen=max_history)
        
        # Setup figure with subplots
        self.fig = plt.figure(figsize=(16, 10))
        self.gs = GridSpec(3, 2, figure=self.fig, hspace=0.3, wspace=0.3)
        
        # Subplot 1: Iteration vs Execution Time
        self.ax_time = self.fig.add_subplot(self.gs[0, 0])
        self.ax_time.set_xlabel('Iteration', fontsize=10)
        self.ax_time.set_ylabel('Execution Time (s)', fontsize=10)
        self.ax_time.set_title('Execution Time vs Iteration', fontsize=12, fontweight='bold')
        self.ax_time.grid(True, alpha=0.3)
        self.line_time, = self.ax_time.plot([], [], 'b-', alpha=0.5, label='All')
        self.line_time_best, = self.ax_time.plot([], [], 'g-', linewidth=2, label='Best')
        self.ax_time.legend()
        
        # Subplot 2: Iteration vs Memory Usage
        self.ax_mem = self.fig.add_subplot(self.gs[0, 1])
        self.ax_mem.set_xlabel('Iteration', fontsize=10)
        self.ax_mem.set_ylabel('Memory Usage (MB)', fontsize=10)
        self.ax_mem.set_title('Memory Usage vs Iteration', fontsize=12, fontweight='bold')
        self.ax_mem.grid(True, alpha=0.3)
        self.line_mem, = self.ax_mem.plot([], [], 'r-', alpha=0.5, label='All')
        self.line_mem_best, = self.ax_mem.plot([], [], 'g-', linewidth=2, label='Best')
        self.ax_mem.legend()
        
        # Subplot 3: Iteration vs Energy
        self.ax_energy = self.fig.add_subplot(self.gs[1, 0])
        self.ax_energy.set_xlabel('Iteration', fontsize=10)
        self.ax_energy.set_ylabel('Energy', fontsize=10)
        self.ax_energy.set_title('Energy vs Iteration', fontsize=12, fontweight='bold')
        self.ax_energy.grid(True, alpha=0.3)
        self.line_energy, = self.ax_energy.plot([], [], 'purple', alpha=0.5, label='All')
        self.line_energy_best, = self.ax_energy.plot([], [], 'g-', linewidth=2, label='Best')
        self.ax_energy.legend()
        
        # Subplot 4: Accept/Reject Status
        self.ax_status = self.fig.add_subplot(self.gs[1, 1])
        self.ax_status.set_xlabel('Iteration', fontsize=10)
        self.ax_status.set_ylabel('Status', fontsize=10)
        self.ax_status.set_title('Accept/Reject Status', fontsize=12, fontweight='bold')
        self.ax_status.set_ylim(-0.5, 1.5)
        self.ax_status.set_yticks([0, 1])
        self.ax_status.set_yticklabels(['Rejected', 'Accepted'])
        self.ax_status.grid(True, alpha=0.3)
        self.scatter_status = self.ax_status.scatter([], [], c=[], cmap='RdYlGn', s=50, alpha=0.7)
        
        # Subplot 5: History Statistics
        self.ax_stats = self.fig.add_subplot(self.gs[2, :])
        self.ax_stats.axis('off')
        self.stats_text = self.ax_stats.text(0.1, 0.5, '', fontsize=11, 
                                              family='monospace',
                                              verticalalignment='center',
                                              transform=self.ax_stats.transAxes)
        
        # Initialize plot
        plt.tight_layout()
        plt.ion()  # Turn on interactive mode
        plt.show(block=False)
        
        # Best values tracking
        self.best_time = float('inf')
        self.best_mem = float('inf')
        self.best_energy = float('inf')
        self.best_iter = 0
        
    def update(self, history_entry: Dict):
        """
        Update visualization with new history entry
        
        Args:
            history_entry: Dictionary with keys: iteration, energy, metrics, accepted, is_best
        """
        iteration = history_entry.get('iteration', 0)
        energy = history_entry.get('energy', float('inf'))
        metrics = history_entry.get('metrics', {})
        accepted = history_entry.get('accepted', False)
        is_best = history_entry.get('is_best', False)
        
        exec_time = metrics.get('execution_time', float('inf'))
        mem_usage = metrics.get('memory_usage', float('inf'))
        
        # Handle infinite values
        exec_time_val = exec_time if exec_time != float('inf') else None
        mem_usage_val = mem_usage if mem_usage != float('inf') else None
        energy_val = energy if energy != float('inf') else None
        
        # Update data
        self.iterations.append(iteration)
        self.execution_times.append(exec_time_val)
        self.memory_usage.append(mem_usage_val)
        self.energy.append(energy_val)
        self.accepted.append(1 if accepted else 0)
        self.is_best.append(is_best)
        
        # Update best values (only update if we have valid values and it's a best)
        if is_best:
            if exec_time_val is not None and exec_time_val < self.best_time:
                self.best_time = exec_time_val
            if mem_usage_val is not None and mem_usage_val < self.best_mem:
                self.best_mem = mem_usage_val
            if energy_val is not None and energy_val < self.best_energy:
                self.best_energy = energy_val
                self.best_iter = iteration
        
        # Update plots
        self._update_plots()
        
    def _update_plots(self):
        """Update all plot elements"""
        if not self.iterations:
            return
        
        # Convert deques to lists, filtering out None values
        iters = list(self.iterations)
        
        # Execution Time plot
        times_all = [t if t is not None else 0 for t in self.execution_times]
        times_best = [t if (best and t is not None) else None 
                     for t, best in zip(self.execution_times, self.is_best)]
        
        self.line_time.set_data(iters, times_all)
        best_iters = [i for i, t in zip(iters, times_best) if t is not None]
        best_times = [t for t in times_best if t is not None]
        if best_iters:
            self.line_time_best.set_data(best_iters, best_times)
        
        if iters:
            self.ax_time.relim()
            self.ax_time.autoscale_view()
        
        # Memory Usage plot
        mem_all = [m if m is not None else 0 for m in self.memory_usage]
        mem_best = [m if (best and m is not None) else None 
                   for m, best in zip(self.memory_usage, self.is_best)]
        
        self.line_mem.set_data(iters, mem_all)
        best_iters_mem = [i for i, m in zip(iters, mem_best) if m is not None]
        best_mems = [m for m in mem_best if m is not None]
        if best_iters_mem:
            self.line_mem_best.set_data(best_iters_mem, best_mems)
        
        if iters:
            self.ax_mem.relim()
            self.ax_mem.autoscale_view()
        
        # Energy plot
        energy_all = [e if e is not None else 0 for e in self.energy]
        energy_best = [e if (best and e is not None) else None 
                      for e, best in zip(self.energy, self.is_best)]
        
        self.line_energy.set_data(iters, energy_all)
        best_iters_energy = [i for i, e in zip(iters, energy_best) if e is not None]
        best_energies = [e for e in energy_best if e is not None]
        if best_iters_energy:
            self.line_energy_best.set_data(best_iters_energy, best_energies)
        
        if iters:
            self.ax_energy.relim()
            self.ax_energy.autoscale_view()
        
        # Status plot
        if iters:
            colors = ['green' if acc else 'red' for acc in self.accepted]
            self.ax_status.clear()
            self.ax_status.set_ylim(-0.5, 1.5)
            self.ax_status.set_yticks([0, 1])
            self.ax_status.set_yticklabels(['Rejected', 'Accepted'])
            self.ax_status.set_xlabel('Iteration', fontsize=10)
            self.ax_status.set_ylabel('Status', fontsize=10)
            self.ax_status.set_title('Accept/Reject Status', fontsize=12, fontweight='bold')
            self.ax_status.grid(True, alpha=0.3)
            self.ax_status.scatter(iters, list(self.accepted), c=colors, s=50, alpha=0.7)
        
        # Statistics text
        if iters:
            total_iters = len(iters)
            accepted_count = sum(self.accepted)
            rejected_count = total_iters - accepted_count
            best_count = sum(self.is_best)
            
            stats = f"""
┌─────────────────────────────────────────────────────────────────────────┐
│                        OPTIMIZATION STATISTICS                           │
├─────────────────────────────────────────────────────────────────────────┤
│ Total Iterations: {total_iters:>10}                                     │
│ Accepted:         {accepted_count:>10} ({accepted_count/total_iters*100:.1f}%)                │
│ Rejected:         {rejected_count:>10} ({rejected_count/total_iters*100:.1f}%)                │
│ Best Updates:     {best_count:>10}                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ Best Values (Iteration {self.best_iter}):                               │
│   Execution Time: {self.best_time:.6f} s                                │
│   Memory Usage:   {self.best_mem:.6f} MB                                │
│   Energy:         {self.best_energy:.6e}                                │
└─────────────────────────────────────────────────────────────────────────┘
"""
            self.stats_text.set_text(stats)
        
        # Refresh plot
        plt.draw()
        plt.pause(0.01)  # Small pause to allow GUI to update
    
    def save_plot(self, filename: Optional[str] = None):
        """Save current plot to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"optimizer_progress_{timestamp}.png"
        
        filepath = os.path.join(self.save_dir, filename)
        self.fig.savefig(filepath, dpi=150, bbox_inches='tight')
        return filepath
    
    def close(self):
        """Close the visualization window"""
        plt.close(self.fig)

