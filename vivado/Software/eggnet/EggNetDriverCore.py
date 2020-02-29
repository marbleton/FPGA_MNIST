# This file was automatically generated by SWIG (http://www.swig.org).
# Version 4.0.1
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.


from __future__ import absolute_import, print



from sys import version_info as _swig_python_version_info
if _swig_python_version_info < (2, 7, 0):
    raise RuntimeError("Python 2.7 or later required")

# Import the low-level C/C++ module
if __package__ or "." in __name__:
    from . import _EggNetDriverCore
else:
    import _EggNetDriverCore

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_instance_variable(set):
    def set_instance_attr(self, name, value):
        if name == "thisown":
            self.this.own(value)
        elif name == "this":
            set(self, name, value)
        elif hasattr(self, name) and isinstance(getattr(type(self), name), property):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add instance attributes to %s" % self)
    return set_instance_attr


def _swig_setattr_nondynamic_class_variable(set):
    def set_class_attr(cls, name, value):
        if hasattr(cls, name) and not isinstance(getattr(cls, name), property):
            set(cls, name, value)
        else:
            raise AttributeError("You cannot add class attributes to %s" % cls)
    return set_class_attr


def _swig_add_metaclass(metaclass):
    """Class decorator for adding a metaclass to a SWIG wrapped class - a slimmed down version of six.add_metaclass"""
    def wrapper(cls):
        return metaclass(cls.__name__, cls.__bases__, cls.__dict__.copy())
    return wrapper


class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""
    __setattr__ = _swig_setattr_nondynamic_class_variable(type.__setattr__)


EGG_ERROR_NONE = _EggNetDriverCore.EGG_ERROR_NONE
EGG_ERROR_NULL_PTR = _EggNetDriverCore.EGG_ERROR_NULL_PTR
EGG_ERROR_DEVICE_COMMUNICATION_FAILED = _EggNetDriverCore.EGG_ERROR_DEVICE_COMMUNICATION_FAILED
EGG_ERROR_INIT_FAILDED = _EggNetDriverCore.EGG_ERROR_INIT_FAILDED
EGG_ERROR_UDEF = _EggNetDriverCore.EGG_ERROR_UDEF
EGG_MEM_LAYER1_BRAM_ADDR = _EggNetDriverCore.EGG_MEM_LAYER1_BRAM_ADDR
EGG_MEM_LAYER2_BRAM_ADDR = _EggNetDriverCore.EGG_MEM_LAYER2_BRAM_ADDR
EGG_MEM_LAYER3_BRAM_ADDR = _EggNetDriverCore.EGG_MEM_LAYER3_BRAM_ADDR
EGG_MEM_LAYER4_BRAM_ADDR = _EggNetDriverCore.EGG_MEM_LAYER4_BRAM_ADDR
EGG_MEM_LAYER1_BRAM_END_ADDR = _EggNetDriverCore.EGG_MEM_LAYER1_BRAM_END_ADDR
EGG_MEM_LAYER2_BRAM_END_ADDR = _EggNetDriverCore.EGG_MEM_LAYER2_BRAM_END_ADDR
EGG_MEM_LAYER3_BRAM_END_ADDR = _EggNetDriverCore.EGG_MEM_LAYER3_BRAM_END_ADDR
EGG_MEM_LAYER4_BRAM_END_ADDR = _EggNetDriverCore.EGG_MEM_LAYER4_BRAM_END_ADDR
EGG_MEM_LAYER1_BRAM_SIZE = _EggNetDriverCore.EGG_MEM_LAYER1_BRAM_SIZE
EGG_MEM_LAYER2_BRAM_SIZE = _EggNetDriverCore.EGG_MEM_LAYER2_BRAM_SIZE
EGG_MEM_LAYER3_BRAM_SIZE = _EggNetDriverCore.EGG_MEM_LAYER3_BRAM_SIZE
EGG_MEM_LAYER4_BRAM_SIZE = _EggNetDriverCore.EGG_MEM_LAYER4_BRAM_SIZE

def egg_init_dma():
    return _EggNetDriverCore.egg_init_dma()

def egg_close_dma():
    return _EggNetDriverCore.egg_close_dma()

def egg_forward(image_buffer, batch, height, width, channels, results):
    return _EggNetDriverCore.egg_forward(image_buffer, batch, height, width, channels, results)

def egg_send_single_image_sync(image_buffer):
    return _EggNetDriverCore.egg_send_single_image_sync(image_buffer)

def egg_send_single_image_async(image_buffer, batch_size, tid):
    return _EggNetDriverCore.egg_send_single_image_async(image_buffer, batch_size, tid)

def egg_tx_thread(batch, image_buffer):
    return _EggNetDriverCore.egg_tx_thread(batch, image_buffer)

def egg_tx_callback(args):
    return _EggNetDriverCore.egg_tx_callback(args)

def egg_print_err(code):
    return _EggNetDriverCore.egg_print_err(code)

def egg_debug_memdump(dst):
    return _EggNetDriverCore.egg_debug_memdump(dst)

def egg_debug_memread(src_start_address, byte_len, dst):
    return _EggNetDriverCore.egg_debug_memread(src_start_address, byte_len, dst)

def egg_debug_memwrite(src_start_address, byte_len, dst):
    return _EggNetDriverCore.egg_debug_memwrite(src_start_address, byte_len, dst)

def egg_debug_conv():
    return _EggNetDriverCore.egg_debug_conv()

def egg_debug_mul():
    return _EggNetDriverCore.egg_debug_mul()

def egg_conv():
    return _EggNetDriverCore.egg_conv()

