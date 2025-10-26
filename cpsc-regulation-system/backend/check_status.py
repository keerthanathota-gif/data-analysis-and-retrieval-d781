#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

# Check if there's any global state with errors
try:
    from app.admin import routes
    print("Current pipeline_status_global:")
    print(routes.pipeline_status_global)

    if routes.pipeline_instance:
        print("\nPipeline instance exists:")
        print(routes.pipeline_instance.get_status())
    else:
        print("\nNo pipeline instance")
except Exception as e:
    print(f"Error: {e}")
