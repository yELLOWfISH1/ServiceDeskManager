"""
Ping Manager module for network operations and IP resolution
"""
import socket
import subprocess
import platform
from typing import List, Tuple
from dataclasses import dataclass
import pandas as pd
from threading import Thread
from queue import Queue

try:
    from .logger import log_info, log_error, log_warning
except ImportError:
    # Fallback if logger not available
    def log_info(msg): print(f"INFO: {msg}")
    def log_error(msg, e=None): print(f"ERROR: {msg}: {e}")
    def log_warning(msg): print(f"WARNING: {msg}")


@dataclass
class PingResult:
    """Data class for ping results"""
    hostname: str
    ip_address: str
    status: str
    response_time: str = ""
    
    def to_dict(self):
        return {
            'Hostname': self.hostname,
            'IP Address': self.ip_address,
            'Ping Status': self.status,
            'Response Time': self.response_time
        }


class PingManager:
    """Manages ping operations and hostname resolution"""
    
    def __init__(self):
        self.ping_count_param = "-n" if platform.system().lower() == "windows" else "-c"
        self.results: List[PingResult] = []
        self.callback = None  # For progress updates
    
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.callback = callback
    
    def ping_host(self, hostname: str) -> PingResult:
        """
        Ping a single host and resolve its IP address
        
        Args:
            hostname: Hostname or IP address to ping
            
        Returns:
            PingResult object
        """
        # Attempt DNS resolution
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            return PingResult(
                hostname=hostname,
                ip_address="",
                status="DNS failed"
            )
        except Exception as e:
            return PingResult(
                hostname=hostname,
                ip_address="",
                status=f"Error: {str(e)}"
            )
        
        # Attempt ping
        try:
            result = subprocess.run(
                ["ping", self.ping_count_param, "1", ip_address],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                text=True
            )
            status = "Reachable" if result.returncode == 0 else "Unreachable"
            
            # Extract response time from ping output
            response_time = ""
            if result.returncode == 0 and result.stdout:
                import re
                # Windows: "Reply from X: time=Xms"
                # Linux: "time=X ms"
                match = re.search(r'time[=<](\d+)\s*m?s', result.stdout, re.IGNORECASE)
                if match:
                    response_time = f"{match.group(1)}ms"
        except subprocess.TimeoutExpired:
            status = "Timeout"
            response_time = ""
        except Exception as e:
            status = f"Error: {str(e)}"
            response_time = ""
        
        return PingResult(
            hostname=hostname,
            ip_address=ip_address,
            status=status,
            response_time=response_time
        )
    
    def ping_multiple(self, hostnames: List[str], use_threading: bool = True) -> List[PingResult]:
        """
        Ping multiple hosts
        
        Args:
            hostnames: List of hostnames to ping
            use_threading: Whether to use threading for concurrent pings
            
        Returns:
            List of PingResult objects
        """
        self.results = []
        
        if use_threading:
            return self._ping_multithreaded(hostnames)
        else:
            return self._ping_sequential(hostnames)
    
    def _ping_sequential(self, hostnames: List[str]) -> List[PingResult]:
        """Ping hosts sequentially"""
        for hostname in hostnames:
            result = self.ping_host(hostname)
            self.results.append(result)
            if self.callback:
                self.callback(len(self.results), len(hostnames))
        
        return self.results
    
    def _ping_multithreaded(self, hostnames: List[str], max_threads: int = 5) -> List[PingResult]:
        """Ping hosts using threading"""
        queue = Queue()
        results_dict = {}
        
        def worker():
            while True:
                item = queue.get()
                if item is None:
                    break
                
                index, hostname = item
                result = self.ping_host(hostname)
                results_dict[index] = result
                
                if self.callback:
                    self.callback(len(results_dict), len(hostnames))
                
                queue.task_done()
        
        # Start worker threads
        threads = []
        for _ in range(min(max_threads, len(hostnames))):
            t = Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)
        
        # Queue items
        for index, hostname in enumerate(hostnames):
            queue.put((index, hostname))
        
        # Wait for completion
        queue.join()
        
        # Stop workers
        for _ in threads:
            queue.put(None)
        
        for t in threads:
            t.join()
        
        # Sort results by original order
        self.results = [results_dict[i] for i in range(len(hostnames))]
        return self.results
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Get results as pandas DataFrame
        
        Returns:
            DataFrame with columns: Hostname, IP Address, Ping Status
        """
        data = [result.to_dict() for result in self.results]
        return pd.DataFrame(data)
    
    def load_from_spreadsheet(self, df: pd.DataFrame, hostname_column: str = "hostname") -> List[str]:
        """
        Load hostnames from spreadsheet
        
        Args:
            df: DataFrame containing hostnames
            hostname_column: Name of column containing hostnames
            
        Returns:
            List of hostnames
        """
        # Try to find hostname column (case-insensitive)
        df.columns = df.columns.str.lower()
        
        if hostname_column.lower() not in df.columns:
            # Try common variations
            for col in df.columns:
                if "host" in col.lower():
                    hostname_column = col
                    break
            else:
                raise ValueError(f"Could not find hostname column. Available: {list(df.columns)}")
        
        hostnames = df[hostname_column.lower()].dropna().astype(str).tolist()
        return [h.strip() for h in hostnames if h.strip()]
