from utils import check_extension, extract_camera_id


def test_check_extension():
    assert check_extension("test.jpg")
    assert check_extension("test.jpeg")
    assert check_extension("test.png")
    assert check_extension("test.png")
    assert not check_extension("test.p")


def test_extract_camera_id():
    assert extract_camera_id("camera000_test.jpg") == "000"
    assert extract_camera_id("camera001_test.jpg") == "001"


def test_extract_camera_id_error():
    try:
        extract_camera_id("test.jpg")
    except ValueError as e:
        assert str(e) == "The file name does not contain the camera ID"
    else:
        assert False
