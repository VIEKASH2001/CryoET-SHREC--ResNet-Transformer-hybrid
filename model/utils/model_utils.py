import torch
import torch.nn as nn
from math import log
from collections import OrderedDict
import torch.nn.functional as F



def flatten(seq):
    """
    Flatten a sequence of sequences and items.

    Args:
        seq (list | tuple): The sequence to be flattened.

    Returns:
        list | tuple: The flattened sequence.
    """
    seq_type = type(seq)

    out = []
    for item in seq:
        if isinstance(item, (list, tuple)):
            out += flatten(item)
        else:
            out.append(item)

    return seq_type(out)





class Parameter(nn.Parameter):
    """
    An :obj:`nn.Parameter` class that supports multiple inputs initializes the
    parameters using a scaled normal distribution.
    """

    def __new__(cls, *args, requires_grad=True, **kwargs):
        if torch.is_tensor(args[0]):
            data = args[0]
        elif isinstance(args[0], (list, tuple)):
            data = torch.randn(args[0], **kwargs) / args[0][-1]**0.5
        else:
            data = torch.randn(args, **kwargs) / args[-1]**0.5

        return torch.Tensor._make_subclass(cls, data, requires_grad)




class Sequential(nn.Sequential):
    """
    An :obj:`nn.Sequential` class that supports multiple inputs.
    """

    def __init__(self, *args):
        super(nn.Sequential, self).__init__()

        idx = 0
        for arg in args:
            if isinstance(arg, OrderedDict):
                for key, mod in arg.items():
                    if mod is not None:
                        self.add_module(key, mod)
                continue
            elif not isinstance(arg, (list, tuple)):
                arg = [arg]

            for mod in [a for a in arg if a is not None]:
                self.add_module(str(idx), mod)
                idx += 1

    def forward(self, *args, **kwargs):
        for mod in self:
            if isinstance(args, (list, tuple)):
                args = mod(*args, **kwargs)
            else:
                args = mod(args, **kwargs)
        return args


class ModuleList(nn.ModuleList):
    """
    An :obj:`nn.ModuleList` class that supports multiple inputs.
    """

    def __init__(self, *args):
        super(nn.ModuleList, self).__init__()
        self += [a for a in flatten(args) if a is not None]



