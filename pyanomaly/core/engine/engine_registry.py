"""
@author:  Yuhao Cheng
@contact: yuhao.cheng[at]outlook.com
"""
from fvcore.common.registry import Registry

ENGINE_REGISTRY = Registry("ENGINE")
ENGINE_REGISTRY.__doc__ = """
    Registry for hook functional classes
"""