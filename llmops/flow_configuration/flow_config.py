
# TODO add comments to the class

class FlowConfiguration:
    def __init__(self, flow_name: str, **kwargs) -> None:
        self.flow_name = flow_name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict:
        # Collect all attributes that do not start with an underscore
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


    