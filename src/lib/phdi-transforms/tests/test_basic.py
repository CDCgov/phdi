from phdi_transforms.basic import transform_name
from phdi_transforms.basic import transform_phone


def test_transform_name():
    assert "JOHN DOE" == transform_name(" JOHN DOE ")
    assert "JOHN DOE" == transform_name(" John Doe3 ")


def test_transform_phone():
    assert "0123456789" == transform_phone("0123456789")
    assert "0123456789" == transform_phone("(012)345-6789")
    assert transform_phone("345-6789") is None
