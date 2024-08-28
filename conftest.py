def pytest_report_header(config):
    return "This is EO-staging automation team work"


def pytest_addoption(parser):
    parser.addoption("--DIT_name", action="store", default="not given")
    parser.addoption("--vnf_type", action="store", default="not given")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.DIT_name
    if 'DIT_name' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("DIT_name", [option_value])

    option_value_2 = metafunc.config.option.vnf_type
    if 'vnf_type' in metafunc.fixturenames and option_value_2 is not None:
        metafunc.parametrize("vnf_type", [option_value_2])