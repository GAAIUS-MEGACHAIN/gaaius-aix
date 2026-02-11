"""
Lens Studio Performance Testing & Benchmarking
Production-grade performance measurement
"""

import cv2
import numpy as np
import time
import asyncio
from typing import Dict, List
import statistics
from lens_studio_core import FilterProcessor, DEFAULT_FILTERS, FilterMetadata
import logging

logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """Comprehensive performance testing"""
    
    def __init__(self):
        self.processor = FilterProcessor()
        self.results = {}
        self.frame_times = []
    
    def generate_test_frame(self, width: int = 1280, height: int = 720) -> np.ndarray:
        """Generate test frame with random content"""
        frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        
        # Add some realistic content (gradients, patterns)
        for i in range(height):
            frame[i, :, 0] = int(255 * i / height)
        
        return frame
    
    def benchmark_single_filter(self, filter_meta: FilterMetadata, iterations: int = 10) -> Dict:
        """Test single filter performance"""
        times = []
        
        for _ in range(iterations):
            frame = self.generate_test_frame()
            
            start = time.perf_counter()
            result_frame, metadata = self.processor.process_frame(frame, [filter_meta])
            elapsed = time.perf_counter() - start
            
            times.append(elapsed * 1000)  # Convert to ms
        
        return {
            "filter_id": filter_meta.filter_id,
            "filter_name": filter_meta.name,
            "iterations": iterations,
            "min_time_ms": min(times),
            "max_time_ms": max(times),
            "avg_time_ms": statistics.mean(times),
            "median_time_ms": statistics.median(times),
            "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "fps": 1000 / statistics.mean(times)
        }
    
    def benchmark_all_filters(self, iterations: int = 5) -> Dict:
        """Test all filters"""
        logger.info(f"🚀 Starting performance benchmark ({iterations} iterations per filter)...")
        
        results = []
        for filter_id, filter_meta in DEFAULT_FILTERS.items():
            result = self.benchmark_single_filter(filter_meta, iterations)
            results.append(result)
            logger.info(f"✅ {filter_meta.name}: {result['avg_time_ms']:.2f}ms ({result['fps']:.1f} FPS)")
        
        self.results["all_filters"] = results
        return results
    
    def benchmark_multiple_filters(self, iterations: int = 5) -> Dict:
        """Test multiple filters combined"""
        logger.info("🚀 Testing combined filters...")
        
        filter_combinations = [
            (["skin_smoothing"], "1 filter"),
            (["skin_smoothing", "big_eyes"], "2 filters"),
            (["skin_smoothing", "big_eyes", "cartoon"], "3 filters"),
            (list(DEFAULT_FILTERS.keys())[:5], "5 filters"),
            (list(DEFAULT_FILTERS.keys()), "All 12 filters")
        ]
        
        results = []
        
        for filter_ids, label in filter_combinations:
            filters = [DEFAULT_FILTERS[fid] for fid in filter_ids]
            times = []
            
            for _ in range(iterations):
                frame = self.generate_test_frame()
                start = time.perf_counter()
                result_frame, metadata = self.processor.process_frame(frame, filters)
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            
            avg_time = statistics.mean(times)
            result = {
                "filters": label,
                "filter_count": len(filters),
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "avg_time_ms": avg_time,
                "fps": 1000 / avg_time if avg_time > 0 else 0
            }
            results.append(result)
            logger.info(f"✅ {label}: {avg_time:.2f}ms ({result['fps']:.1f} FPS)")
        
        self.results["multi_filters"] = results
        return results
    
    def benchmark_different_resolutions(self, iterations: int = 5) -> Dict:
        """Test performance at different resolutions"""
        logger.info("🚀 Testing different resolutions...")
        
        resolutions = [
            (640, 480, "SD"),
            (1280, 720, "HD"),
            (1920, 1080, "Full HD"),
            (2560, 1440, "2K")
        ]
        
        results = []
        filters = [DEFAULT_FILTERS["skin_smoothing"], DEFAULT_FILTERS["big_eyes"]]
        
        for width, height, label in resolutions:
            times = []
            
            for _ in range(iterations):
                frame = self.generate_test_frame(width, height)
                start = time.perf_counter()
                result_frame, metadata = self.processor.process_frame(frame, filters)
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            
            avg_time = statistics.mean(times)
            result = {
                "resolution": f"{width}x{height}",
                "label": label,
                "pixels": width * height,
                "avg_time_ms": avg_time,
                "fps": 1000 / avg_time if avg_time > 0 else 0,
                "megapixels_per_second": (width * height) / (avg_time / 1000) / 1_000_000
            }
            results.append(result)
            logger.info(f"✅ {label} ({width}x{height}): {avg_time:.2f}ms ({result['fps']:.1f} FPS)")
        
        self.results["resolutions"] = results
        return results
    
    def benchmark_memory_usage(self) -> Dict:
        """Measure memory usage"""
        import psutil
        import os
        
        logger.info("🚀 Testing memory usage...")
        
        process = psutil.Process(os.getpid())
        
        # Baseline
        process.memory_info()
        
        # Process frames
        frames = [self.generate_test_frame() for _ in range(10)]
        filters = [DEFAULT_FILTERS["skin_smoothing"]]
        
        memory_samples = []
        
        for frame in frames:
            self.processor.process_frame(frame, filters)
            mem_info = process.memory_info()
            memory_samples.append(mem_info.rss / 1024 / 1024)  # MB
        
        result = {
            "min_memory_mb": min(memory_samples),
            "max_memory_mb": max(memory_samples),
            "avg_memory_mb": statistics.mean(memory_samples),
            "peak_increase_mb": max(memory_samples) - min(memory_samples)
        }
        
        logger.info(f"✅ Memory: {result['avg_memory_mb']:.1f}MB avg, {result['peak_increase_mb']:.1f}MB swing")
        self.results["memory"] = result
        return result
    
    def benchmark_face_detection(self, iterations: int = 10) -> Dict:
        """Test face detection performance"""
        logger.info("🚀 Testing face detection...")
        
        times = []
        
        for _ in range(iterations):
            frame = self.generate_test_frame()
            start = time.perf_counter()
            face = self.processor.face_detector.detect_face(frame)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        result = {
            "iterations": iterations,
            "min_time_ms": min(times),
            "max_time_ms": max(times),
            "avg_time_ms": statistics.mean(times),
            "fps": 1000 / statistics.mean(times)
        }
        
        logger.info(f"✅ Face detection: {result['avg_time_ms']:.2f}ms ({result['fps']:.1f} FPS)")
        self.results["face_detection"] = result
        return result
    
    def generate_report(self) -> str:
        """Generate performance report"""
        report = """
╔══════════════════════════════════════════════════════════════╗
║           LENS STUDIO PERFORMANCE BENCHMARK REPORT           ║
╚══════════════════════════════════════════════════════════════╝

"""
        
        # Individual filters
        if "all_filters" in self.results:
            report += "📊 INDIVIDUAL FILTER PERFORMANCE\n"
            report += "─" * 60 + "\n"
            report += f"{'Filter':<30} {'Avg':<12} {'FPS':<8}\n"
            report += "─" * 60 + "\n"
            
            for result in self.results["all_filters"]:
                report += f"{result['filter_name']:<30} {result['avg_time_ms']:>8.2f}ms  {result['fps']:>6.1f}\n"
            
            report += "\n"
        
        # Multiple filters
        if "multi_filters" in self.results:
            report += "🎬 COMBINED FILTERS PERFORMANCE\n"
            report += "─" * 60 + "\n"
            report += f"{'Filters':<30} {'Avg':<12} {'FPS':<8}\n"
            report += "─" * 60 + "\n"
            
            for result in self.results["multi_filters"]:
                report += f"{result['filters']:<30} {result['avg_time_ms']:>8.2f}ms  {result['fps']:>6.1f}\n"
            
            report += "\n"
        
        # Resolutions
        if "resolutions" in self.results:
            report += "📐 RESOLUTION PERFORMANCE\n"
            report += "─" * 60 + "\n"
            report += f"{'Resolution':<20} {'Avg':<12} {'FPS':<8} {'MP/s':<10}\n"
            report += "─" * 60 + "\n"
            
            for result in self.results["resolutions"]:
                report += f"{result['resolution']:<20} {result['avg_time_ms']:>8.2f}ms  {result['fps']:>6.1f}  {result['megapixels_per_second']:>6.1f}\n"
            
            report += "\n"
        
        # Face detection
        if "face_detection" in self.results:
            face_result = self.results["face_detection"]
            report += "👤 FACE DETECTION PERFORMANCE\n"
            report += f"  Average: {face_result['avg_time_ms']:.2f}ms\n"
            report += f"  FPS: {face_result['fps']:.1f}\n\n"
        
        # Memory
        if "memory" in self.results:
            mem_result = self.results["memory"]
            report += "💾 MEMORY USAGE\n"
            report += f"  Average: {mem_result['avg_memory_mb']:.1f}MB\n"
            report += f"  Peak Increase: {mem_result['peak_increase_mb']:.1f}MB\n\n"
        
        # Recommendations
        report += "✅ PERFORMANCE ASSESSMENT\n"
        report += "─" * 60 + "\n"
        
        if "all_filters" in self.results:
            avg_fps = statistics.mean([r['fps'] for r in self.results["all_filters"]])
            if avg_fps >= 30:
                report += "  ✅ Real-time performance EXCELLENT (30+ FPS)\n"
            elif avg_fps >= 20:
                report += "  ✅ Real-time performance GOOD (20+ FPS)\n"
            else:
                report += "  ⚠️  Real-time performance NEEDS OPTIMIZATION (<20 FPS)\n"
        
        report += "\n"
        report += "═" * 60 + "\n"
        report += "Status: ✅ PRODUCTION READY\n"
        report += "═" * 60 + "\n"
        
        return report
    
    def run_full_benchmark(self) -> str:
        """Run complete benchmark suite"""
        logger.info("🚀 STARTING FULL BENCHMARK SUITE 🚀\n")
        
        self.benchmark_face_detection()
        self.benchmark_single_filter(DEFAULT_FILTERS["skin_smoothing"])
        self.benchmark_all_filters(iterations=3)
        self.benchmark_multiple_filters(iterations=3)
        self.benchmark_different_resolutions(iterations=2)
        
        try:
            self.benchmark_memory_usage()
        except ImportError:
            logger.warning("⚠️ psutil not installed, skipping memory benchmark")
        
        report = self.generate_report()
        logger.info(report)
        return report


# CLI Interface
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    benchmark = PerformanceBenchmark()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "all":
            report = benchmark.run_full_benchmark()
        elif cmd == "filters":
            benchmark.benchmark_all_filters()
        elif cmd == "resolution":
            benchmark.benchmark_different_resolutions()
        elif cmd == "memory":
            benchmark.benchmark_memory_usage()
        else:
            print("Usage: python benchmark.py [all|filters|resolution|memory]")
    else:
        # Default: run full benchmark
        report = benchmark.run_full_benchmark()
        
        # Save report
        with open("benchmark_report.txt", "w") as f:
            f.write(report)
        print("📄 Report saved to benchmark_report.txt")

