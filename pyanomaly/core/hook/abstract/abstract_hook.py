"""
@author:  Yuhao Cheng
@contact: yuhao.cheng[at]outlook.com
"""
import torch
from ..hook_registry import HOOK_REGISTRY
import abc
__all__ = ['HookBase', 'EvaluateHook']

@HOOK_REGISTRY.register()
class HookBase(object):
    """
    Base class for hooks that can be registered with :class:`TrainerBase`.
    Each hook can implement 4 methods. The way they are called is demonstrated
    in the following snippet:
    .. code-block:: python
        hook.before_train()
        for iter in range(start_iter, max_iter):
            hook.before_step()
            trainer.run_step()
            hook.after_step()
        hook.after_train()
    Notes:
        1. In the hook method, users can access `self.trainer` to access more
           properties about the context (e.g., current iteration).
        2. A hook that does something in :meth:`before_step` can often be
           implemented equivalently in :meth:`after_step`.
           If the hook takes non-trivial time, it is strongly recommended to
           implement the hook in :meth:`after_step` instead of :meth:`before_step`.
           The convention is that :meth:`before_step` should only take negligible time.
           Following this convention will allow hooks that do care about the difference
           between :meth:`before_step` and :meth:`after_step` (e.g., timer) to
           function properly.
    Attributes:
        trainer: A weak reference to the trainer object. Set by the trainer when the hook is
            registered.
    """
    def before_train(self):
        """
        Called before the first iteration.
        """
        pass

    def after_train(self):
        """
        Called after the last iteration.
        """
        pass

    def before_step(self, current_step):
        """
        Called before each iteration.
        """
        pass

    def after_step(self, current_step):
        """
        Called after each iteration.
        """
        pass

@HOOK_REGISTRY.register()
class EvaluateHook(HookBase):
    def after_step(self, current_step):
        acc = 0.0
        if current_step % self.engine.steps.param['eval'] == 0 and current_step != 0:
            with torch.no_grad():
                acc = self.evaluate(current_step)
                if acc > self.engine.accuarcy:
                    self.engine.accuarcy = acc
                    # save the model & checkpoint
                    self.engine.save(current_step, best=True)
                elif current_step % self.engine.steps.param['save'] == 0 and current_step != 0:
                    # save the checkpoint
                    self.engine.save(current_step)
                    self.engine.logger.info('LOL==>the accuracy is not imporved in epcoh{} but save'.format(current_step))
    
    def inference(self):
        acc = self.evaluate(0)
        self.engine.logger.info(f'The inference metric is:{acc:.3f}')
    
    @abc.abstractmethod
    def evaluate(self, current_step)->float:
        pass