"""
test_mixin_attributes.py
"""


class CarMixin:
    # Assume these attributes exist by declaring them in the mixin
    make: str
    model: str

    def display_description(self) -> None:
        print(f"This car is a {self.make} {self.model}.")


class ElectricVehicle:
    def __init__(self, make, model):
        self.make = make
        self.model = model


class Volkswagen(ElectricVehicle, CarMixin):
    def __init__(self, model):
        super().__init__("VW", model)


def test_mixin_attribute():
    my_car = Volkswagen("Model S")
    my_car.display_description()  # This will use the mixin method
