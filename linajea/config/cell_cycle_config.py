import attr

from linajea import load_config
from .cnn_config import (EfficientNetConfig,
                         ResNetConfig,
                         VGGConfig)
from .evaluate import EvaluateCellCycleConfig
from .general import GeneralConfig
from .optimizer import (OptimizerTF1Config,
                        OptimizerTF2Config,
                        OptimizerTorchConfig)

from .predict import PredictCellCycleConfig
from .train_test_validate_data import (TestDataCellCycleConfig,
                                       TrainDataCellCycleConfig,
                                       ValidateDataCellCycleConfig)
from .train import TrainCellCycleConfig
from .utils import ensure_cls


def model_converter():
    def converter(val):
        if val['network_type'].lower() == "vgg":
            return VGGConfig(**val) # type: ignore
        elif val['network_type'].lower() == "resnet":
            return ResNetConfig(**val) # type: ignore
        elif val['network_type'].lower() == "efficientnet":
            return EfficientNetConfig(**val) # type: ignore
        else:
            raise RuntimeError("invalid network_type: {}!".format(
                val['network_type']))
    return converter


@attr.s(kw_only=True)
class CellCycleConfig:
    path = attr.ib(type=str)
    general = attr.ib(converter=ensure_cls(GeneralConfig))
    model = attr.ib(converter=model_converter())
    optimizerTF1 = attr.ib(converter=ensure_cls(OptimizerTF1Config), default=None)
    optimizerTF2 = attr.ib(converter=ensure_cls(OptimizerTF2Config), default=None)
    optimizerTorch = attr.ib(converter=ensure_cls(OptimizerTorchConfig), default=None)
    train = attr.ib(converter=ensure_cls(TrainCellCycleConfig))
    train_data = attr.ib(converter=ensure_cls(TrainDataCellCycleConfig))
    test_data = attr.ib(converter=ensure_cls(TestDataCellCycleConfig))
    validate_data = attr.ib(converter=ensure_cls(ValidateDataCellCycleConfig))
    predict = attr.ib(converter=ensure_cls(PredictCellCycleConfig))
    evaluate = attr.ib(converter=ensure_cls(EvaluateCellCycleConfig))

    @classmethod
    def from_file(cls, path):
        config_dict = load_config(path)
        # if 'path' in config_dict:
        #     assert path == config_dict['path'], "{} {}".format(path, config_dict['path'])
        #     del config_dict['path']
        try:
            del config_dict['path']
        except:
            pass
        return cls(path=path, **config_dict) # type: ignore

    def __attrs_post_init__(self):
        assert (int(bool(self.optimizerTF1)) +
                int(bool(self.optimizerTF2)) +
                int(bool(self.optimizerTorch))) == 1, \
                "please specify exactly one optimizer config (tf1, tf2, torch)"

        if self.predict.use_swa is None:
            self.predict.use_swa = self.train.use_swa