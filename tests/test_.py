# Core quick tests


from zvic import canonicalize
from zvic.annotation_constraints import apply_annotation_constraints


def test_case1_basic_value_constraint():
    src = """
def set_temperature(celsius: float(0 <= _ <= 100)):
    '''Thermostat control'''
"""
    expected = (
        "from typing import Annotated\n"
        "\n"
        "def set_temperature(celsius: Annotated[float, '0 <= _ <= 100']):\n"
        '    """Thermostat control"""'
    )
    result = apply_annotation_constraints(src).strip()
    assert result == expected.strip()


def test_case2_container_structure_content():
    src = """
def process_pixels(image: list[list[int(0 <= _ <= 255)](len(_) == 128)](len(_) == 128)):
    pass
"""
    expected = (
        "from typing import Annotated\n"
        "\n"
        "def process_pixels(image: Annotated[list[list[int(0 <= _ <= 255)](len(_) == 128)], '0 <= _ <= 255)](len(_) == 128)](len(_) == 128']):\n"
        "    pass"
    )
    result = apply_annotation_constraints(src).strip()
    assert result == expected.strip()


def simple_func(a: int, b: str = "x") -> bool:
    return str(a) == b


def test_canonicalize_function():
    result = canonicalize(simple_func)
    assert result["type"] == "callable"
    assert result["name"] == "simple_func"


def test_case3_type_safe_api_request():
    src = """
def create_user(payload: dict('name' in _ and isinstance(_['name'], str) and 'id' in _ and isinstance(_['id'], int) and _['id'] > 0)):
    pass
"""
    expected = """
from typing import Annotated

def create_user(payload: Annotated[dict, "'name' in _ and isinstance(_['name'], str) and ('id' in _) and isinstance(_['id'], int) and (_['id'] > 0)"]):
    pass
"""
    result = apply_annotation_constraints(src).strip()
    assert result == expected.strip()


def test_case4_physics_simulation_constraint():
    src = """
def simulate_particle(velocity: tuple[float, float](math.sqrt(_[0]**2 + _[1]**2) < 3e8)):
    pass
"""
    expected = """
from typing import Annotated

def simulate_particle(velocity: Annotated[tuple[float, float], 'math.sqrt(_[0] ** 2 + _[1] ** 2) < 300000000.0']):
    pass
"""
    result = apply_annotation_constraints(src).strip()
    assert result == expected.strip()
