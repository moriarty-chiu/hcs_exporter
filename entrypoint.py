#!/usr/bin/env python3

import sys
import os

def main():
    """Unified entrypoint for HCS Exporter"""
    
    # 获取命令行参数
    if len(sys.argv) > 1:
        exporter_type = sys.argv[1]
    else:
        # 默认运行OBS exporter
        exporter_type = "obs"
    
    if exporter_type == "obs":
        # 运行OBS exporter
        try:
            from obs_exporter import main as obs_main
            obs_main()
        except ImportError as e:
            print(f"Failed to import obs_exporter: {e}")
            sys.exit(1)
    elif exporter_type == "dcs":
        # 运行DCS exporter
        try:
            from dcs_exporter import main as dcs_main
            dcs_main()
        except ImportError as e:
            print(f"Failed to import dcs_exporter: {e}")
            sys.exit(1)
    else:
        print(f"Unknown exporter type: {exporter_type}")
        print("Usage: python entrypoint.py [obs|dcs]")
        sys.exit(1)

if __name__ == "__main__":
    main()