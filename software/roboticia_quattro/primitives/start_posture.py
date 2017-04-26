from pypot.primitive.utils import SimplePosture

class StartPosture(SimplePosture):
    def __repr__(self):
        return ('<Primitive name={self.name}>').format(self=self)
    @property
    def target_position(self):
        return {
            'm11': -5.,
            'm21': 5.,
            'm31': -5.,
            'm41': 5.,
            'm12': -20.,
            'm22': -20.,
            'm32': 20.,
            'm42': 20.,
            'm13': -20.,
            'm23': -20,
            'm33': 20.,
            'm43': 20.,
        }