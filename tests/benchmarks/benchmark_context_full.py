
import timeit
import sys
import os

# Add project's src directory to path for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from core.context import ContextLoader

def benchmark_load_tech_stack():
    loader = ContextLoader()
    # Ensure first run is cached (setup)
    loader.load_tech_stack()

    def run():
        loader.load_tech_stack()

    execution_time = timeit.timeit(run, number=100000)
    print(f"load_tech_stack (100k calls): {execution_time:.6f} seconds")
    return execution_time

def benchmark_build_system_context():
    loader = ContextLoader()
    # Ensure first run is cached (setup)
    loader.build_system_context("brain")

    def run():
        loader.build_system_context("brain")

    execution_time = timeit.timeit(run, number=100000)
    print(f"build_system_context (100k calls): {execution_time:.6f} seconds")
    return execution_time

if __name__ == "__main__":
    print("--- Baseline Benchmark ---")
    benchmark_load_tech_stack()
    benchmark_build_system_context()
