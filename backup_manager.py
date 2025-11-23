"""
Real-time backup manager for best code
Saves best code whenever it improves
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional


class BackupManager:
    """Manages real-time backup of best code"""
    
    def __init__(self, backup_dir: str = "backups", max_backups: int = 100):
        """
        Initialize backup manager
        
        Args:
            backup_dir: Directory to save backups
            max_backups: Maximum number of backup files to keep
        """
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self.best_energy = float('inf')
        self.best_iteration = 0
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create index file to track backups
        self.index_file = os.path.join(backup_dir, "backup_index.json")
        self.backups = self._load_index()
    
    def _load_index(self) -> list:
        """Load backup index from file"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_index(self):
        """Save backup index to file"""
        with open(self.index_file, 'w') as f:
            json.dump(self.backups, f, indent=2)
    
    def should_backup(self, energy: float, iteration: int) -> bool:
        """
        Check if code should be backed up (if it's better than current best)
        
        Args:
            energy: Current energy value
            iteration: Current iteration number
            
        Returns:
            True if should backup, False otherwise
        """
        # Always backup if it's better
        if energy < self.best_energy:
            return True
        return False
    
    def backup_code(self, code: str, metrics: Dict, energy: float, 
                   iteration: int, history_entry: Optional[Dict] = None) -> Optional[str]:
        """
        Backup code if it's better than current best
        
        Args:
            code: Code to backup
            metrics: Performance metrics
            energy: Energy value
            iteration: Iteration number
            history_entry: Full history entry (optional)
            
        Returns:
            Path to backup file if saved, None otherwise
        """
        if not self.should_backup(energy, iteration):
            return None
        
        # Update best values
        old_best_energy = self.best_energy
        self.best_energy = energy
        self.best_iteration = iteration
        
        # Create backup entry
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"best_code_iter_{iteration:04d}_{timestamp}.py"
        filepath = os.path.join(self.backup_dir, filename)
        
        # Create backup metadata
        backup_info = {
            "iteration": iteration,
            "energy": energy,
            "timestamp": timestamp,
            "metrics": metrics,
            "improvement": ((old_best_energy - energy) / old_best_energy * 100) if old_best_energy != float('inf') else 0,
            "filepath": filename
        }
        
        if history_entry:
            backup_info.update({
                "llm_idea": history_entry.get("llm_idea", ""),
                "llm_reasoning": history_entry.get("llm_reasoning", ""),
                "estimated_improvement": history_entry.get("estimated_improvement", ""),
                "actual_time_change": history_entry.get("actual_time_change", ""),
                "actual_mem_change": history_entry.get("actual_mem_change", "")
            })
        
        # Save code file
        with open(filepath, 'w') as f:
            f.write(code)
        
        # Save metadata JSON
        json_filepath = filepath.replace('.py', '.json')
        with open(json_filepath, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        # Update index
        self.backups.append(backup_info)
        
        # Keep only recent backups
        if len(self.backups) > self.max_backups:
            # Remove oldest backup files
            old_backup = self.backups.pop(0)
            old_filepath = os.path.join(self.backup_dir, old_backup["filepath"])
            old_jsonpath = old_filepath.replace('.py', '.json')
            
            try:
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
                if os.path.exists(old_jsonpath):
                    os.remove(old_jsonpath)
            except:
                pass
        
        # Save updated index
        self._save_index()
        
        # Also update "latest" symlink/file
        latest_filepath = os.path.join(self.backup_dir, "latest_best_code.py")
        latest_jsonpath = os.path.join(self.backup_dir, "latest_best_code.json")
        
        try:
            # Copy to latest files
            with open(filepath, 'r') as src, open(latest_filepath, 'w') as dst:
                dst.write(src.read())
            with open(json_filepath, 'r') as src, open(latest_jsonpath, 'w') as dst:
                dst.write(src.read())
        except Exception as e:
            print(f"Warning: Could not update latest backup files: {e}")
        
        return filepath
    
    def get_latest_backup(self) -> Optional[Dict]:
        """Get information about the latest backup"""
        if not self.backups:
            return None
        return self.backups[-1]
    
    def get_all_backups(self) -> list:
        """Get list of all backups"""
        return self.backups.copy()

