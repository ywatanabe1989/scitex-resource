"""scitex-resource quickstart: collect host specs + processor usage."""

import scitex_resource


def main():
    # 1. get_processor_usages: snapshot of CPU/RAM utilisation right now.
    usages = scitex_resource.get_processor_usages()
    print("processor usages:")
    print(usages)
    # Result is typically a DataFrame or dict; both expose len(...) > 0
    assert len(usages) > 0

    # 2. _cpu_info / _memory_info: low-level helpers used by get_specs.
    cpu = scitex_resource._cpu_info()
    mem = scitex_resource._memory_info()
    print("\ncpu_info:", cpu)
    print("memory_info:", mem)
    assert isinstance(cpu, dict) and cpu
    assert isinstance(mem, dict) and mem

    # 3. _disk_info gives us a per-mount disk usage summary.
    disk = scitex_resource._disk_info()
    print("\ndisk_info:", disk)
    assert isinstance(disk, dict) and disk


if __name__ == "__main__":
    main()
