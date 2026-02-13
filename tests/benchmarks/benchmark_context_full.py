
import timeit
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

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
