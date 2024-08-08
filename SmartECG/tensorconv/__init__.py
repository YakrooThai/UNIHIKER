import importlib.util
import sys
import os

# ............................. .pyc
def load_pyc(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# ......... classify_image_lib ....... .pyc
classify_image_lib = load_pyc("classify_image_lib", os.path.join(os.path.dirname(__file__), "classify_image_lib.pyc"))

# .......... classify_image ...............................
classify_image = classify_image_lib.classify_image

