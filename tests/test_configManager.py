import os
from source.confParser import ConfigManager
from source.__version__ import __version__ as version
from nose2.tools.decorators import with_setup


def my_setup():
    global path, customConfigFile
    path = os.getcwd()
    customConfigFile = 'custom.ini'


def test_case01():
    cm = ConfigManager()
    result = cm.readConfigFile('config.ini')
    assert isinstance(result, dict)
    if version < "8.0.7":
        assert len(result.keys()) > 0
        assert 'tls' in result.keys()
    else:
        assert len(result) == 0


def test_case02():
    cm = ConfigManager()
    file = cm.get_template_path()
    result = cm.readConfigFile(file)
    assert isinstance(result, dict)
    assert len(result.keys()) > 0
    assert 'tls' in result.keys()


def test_case03():
    cm = ConfigManager()
    if version < "8.0.7":
        result = cm.readConfigFile('config.ini')
        connection = result['connection']
        assert len(connection) > 0
        assert isinstance(connection, dict)
        assert len(connection) > 0
        if version < "8.0":
            assert 'port' in connection.keys()
        else:
            assert 'port' not in connection.keys()


@with_setup(my_setup)
def test_case04():
    customFile = os.path.join(path, "tests", "test_data", customConfigFile)
    cm = ConfigManager()
    cm.customFile = customFile
    result = cm.readConfigFile(cm.customFile)
    assert 'tls' in result.keys()


def test_case05():
    cm = ConfigManager()
    result = cm.parse_defaults()
    assert isinstance(result, dict)


def test_case06():
    cm = ConfigManager()
    result = cm.parse_defaults()
    assert len(result.keys()) > 0


def test_case07():
    cm = ConfigManager()
    result = cm.parse_defaults()
    result1 = cm.defaults
    assert len(result) == len(result1)


def test_case08():
    cm = ConfigManager()
    result = cm.defaults
    elements = list(result.keys())
    if version < "8.0":
        mandatoryItems = {'port', 'serverPort'}
        assert mandatoryItems.issubset(set(elements))
    else:
        assert 'port' not in set(elements)


def test_case09():
    if version < "8.0":
        cm = ConfigManager()
        result = cm.defaults
        value = int(result['port'])
        assert value == 4242


def test_case10():
    cm = ConfigManager()
    result = cm.defaults
    if version < "7.0":
        assert int(result['port']) == 4242 and int(result['serverPort']) == 9084
    elif version < "8.0":
        assert int(result['port']) == 4242 and int(result['serverPort']) == 9980
    else:
        assert result.get('port', None) is None
        assert int(result['serverPort']) == 9980


def test_case11():
    cm = ConfigManager()
    result = cm.defaults
    assert 'includeDiskData' in result.keys()
    assert result['includeDiskData'] is False


def test_case12():
    cm = ConfigManager()
    result = cm.defaults
    assert 'apiKeyValue' not in result.keys()


def test_case13():
    cm = ConfigManager()
    result = cm.defaults
    assert 'protocol' in result.keys()
    assert result['protocol'] == 'http'


def lowercase_bool_setup():
    global tmp_ini
    import tempfile
    content = (
        "[basic_auth]\n"
        "enabled = true\n"
        "[prometheues_exporter_plugin]\n"
        "rawCounters = false\n"
        "[query]\n"
        "includeDiskData = yes\n"
        "[server]\n"
        "caCertPath = false\n"
    )
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(content)
        tmp_ini = f.name


@with_setup(lowercase_bool_setup)
def test_case14():
    '''readConfigFile converts lowercase "true" to bool True'''
    cm = ConfigManager()
    try:
        result = cm.readConfigFile(tmp_ini)
        assert result['basic_auth']['enabled'] is True
    finally:
        os.unlink(tmp_ini)


@with_setup(lowercase_bool_setup)
def test_case15():
    '''readConfigFile converts lowercase "false" to bool False'''
    cm = ConfigManager()
    try:
        result = cm.readConfigFile(tmp_ini)
        assert result['prometheues_exporter_plugin']['rawCounters'] is False
        assert result['server']['caCertPath'] is False
    finally:
        os.unlink(tmp_ini)


@with_setup(lowercase_bool_setup)
def test_case16():
    '''readConfigFile converts "yes" to bool True'''
    cm = ConfigManager()
    try:
        result = cm.readConfigFile(tmp_ini)
        assert result['query']['includeDiskData'] is True
    finally:
        os.unlink(tmp_ini)
