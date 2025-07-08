import dataclasses
import enum
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pytest
from pydantic import BaseModel

from zvic.type_normalization import normalize_type


@dataclasses.dataclass
class Point:
    x: int
    y: int


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class User(BaseModel):
    id: int
    name: str
    meta: Dict[str, Any]


class Profile(BaseModel):
    user: User
    active: bool


class Custom:
    pass


@pytest.mark.parametrize(
    "tp, expected",
    [
        (int, {"type": "integer"}),
        (float, {"type": "number"}),
        (str, {"type": "string"}),
        (bool, {"type": "boolean"}),
    ],
)
def test_builtin_primitives(tp, expected):
    assert normalize_type(tp) == expected


def test_numpy_scalar_types():
    assert normalize_type(np.int32) == {"type": "integer", "format": "int32"}
    assert normalize_type(np.int64) == {"type": "integer", "format": "int64"}
    assert normalize_type(np.float32) == {"type": "number", "format": "float32"}
    assert normalize_type(np.float64) == {"type": "number", "format": "double"}


def test_list_of_ints_typing_list():
    tp = List[int]
    result = normalize_type(tp)
    assert result["type"] == "sequence"
    assert result["items"] == {"type": "integer"}


def test_list_of_numpy_typing_list():
    tp = List[np.int16]
    result = normalize_type(tp)
    assert result["type"] == "sequence"
    assert result["items"] == {"type": "integer", "format": "int16"}


def test_list_of_point():
    tp = List[Point]
    result = normalize_type(tp)
    assert result["type"] == "sequence"
    # inner item is object with Point properties
    item = result["items"]
    assert isinstance(item, dict), f"Expected dict, got {type(item)}"
    assert item.get("type") == "object"
    assert item.get("class") == "Point"
    props = item.get("properties")
    assert isinstance(props, dict), (
        f"Expected 'properties' to be a dict, got {type(props)}"
    )
    assert set(props.keys()) == {"x", "y"}


@pytest.mark.parametrize(
    "tp, union_types",
    [
        (Optional[int], {"integer", "null"}),
        (Union[int, str], {"integer", "string"}),
    ],
)
def test_optional_and_union(tp, union_types):
    result = normalize_type(tp)
    # expecting a JSON-schema style list of types
    assert set(result.get("type", [])) == union_types


def test_dict_type():
    tp = Dict[str, int]
    result = normalize_type(tp)
    assert result["type"] == "mapping"
    # Accept additionalProperties for mapping
    assert result.get("additionalProperties") == {"type": "integer"}


def test_enum_type():
    result = normalize_type(Color)
    assert result.get("type") == "object"
    assert result.get("class") == "Color"
    enum_members = {member.name for member in Color}
    enum_values = {member.value for member in Color}
    # Accept any of the following valid representations:
    has_properties = (
        "properties" in result
        and isinstance(result["properties"], dict)
        and set(result["properties"].keys()) == enum_members
    )
    has_enum = (
        "enum" in result
        and isinstance(result["enum"], (list, set))
        and set(result["enum"]) == enum_values
    )
    has_values = (
        "values" in result
        and isinstance(result["values"], (list, set))
        and set(result["values"]) == enum_values
    )
    has_empty_properties = "properties" in result and result["properties"] == {}
    assert has_properties or has_enum or has_values or has_empty_properties


def test_dataclass_type():
    result = normalize_type(Point)
    assert result.get("type") == "object"
    assert result.get("class") == "Point"
    if isinstance(result.get("properties"), dict):
        assert set(result["properties"].keys()) == {"x", "y"}
        assert result["properties"]["x"]["type"] == "integer"
    else:
        assert False, "Expected 'properties' to be a dict"


def test_pydantic_base_model():
    result = normalize_type(User)
    assert result.get("type") == "object"
    assert result.get("class") == "User"
    # include both id/name/meta
    if isinstance(result.get("properties"), dict):
        assert set(result["properties"].keys()) == {"id", "name", "meta"}
        assert result["properties"]["id"]["type"] == "integer"
    else:
        assert False, "Expected 'properties' to be a dict"


def test_nested_pydantic():
    result = normalize_type(Profile)
    assert result.get("type") == "object"
    assert result.get("class") == "Profile"
    # nested user sub-schema
    if isinstance(result.get("properties"), dict):
        assert "user" in result["properties"]
        assert result["properties"]["user"].get("class") == "User"
        assert result["properties"]["active"].get("type") == "boolean"
    else:
        assert False, "Expected 'properties' to be a dict"


def test_fallback_custom_class():
    result = normalize_type(Custom)
    # no annotations → fallback to string
    assert result["type"] == "string"
    assert result["class"] == "Custom"


class CustomWithAnnotations:
    __annotations__ = {"foo": int, "bar": str}


def test_custom_class_with_annotations():
    result = normalize_type(CustomWithAnnotations)
    # Should be treated as an object with properties
    assert result.get("type") == "object"
    assert result.get("class") == "CustomWithAnnotations"
    if isinstance(result.get("properties"), dict):
        assert "foo" in result["properties"]
        assert result["properties"]["foo"].get("type") == "integer"
        assert "bar" in result["properties"]
        assert result["properties"]["bar"].get("type") == "string"
    else:
        assert False, "Expected 'properties' to be a dict"


class CustomWithAttributes:
    def __init__(self):
        self.foo = 123
        self.bar = "abc"


def test_custom_class_with_attributes():
    result = normalize_type(CustomWithAttributes)
    # No __annotations__, so fallback to string
    assert result["type"] == "string"
    assert result["class"] == "CustomWithAttributes"


def test_any_type_fallback():
    result = normalize_type(Any)
    # `Any` usually maps to an open schema
    assert result["type"] in ("any", "object", ["any"])
