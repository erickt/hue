
"""a really cheesy example of a module"""

class Bakery(object):
    def bake_pumpkin_pie(self):
        self.prepare_ingredients()
        
    def prepare_ingredients(self):
        self.prepare_eggs()
    
    def prepare_eggs(self):
        self.mix_eggs()
    
    def mix_eggs(self):
        raise ValueError("damn, didn't buy enough eggs!")