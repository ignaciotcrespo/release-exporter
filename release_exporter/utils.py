import configparser
import datetime
import os
from pathlib import Path

import dateutil.parser
from giturlparse import parse
from tabulate import tabulate

from release_exporter import version
from release_exporter.exceptions import ParserError

CONFIG_FILE_NAME = '.rex'


def get_repo_url_info(location=os.getcwd(), repo_url=None):
    """
    Returns the parsed URL.

    Parameters
    ----------
    location: str
        Absolute location of the current directory.
    repo_url: str
        URL of the repository.

    Returns
    -------
    parse: giturlparse.parser.Parsed
        A named tuple.

    """
    try:
        if repo_url is None:
            config = configparser.ConfigParser()
            config.read(location + os.sep + '.git' + os.sep + 'config')
            if 'remote "origin"' in config.sections():
                return parse(config['remote "origin"']['url'])
            else:
                raise ParserError('Git config file does not exist please provide the repository url by using --url.')
        else:
            return parse(repo_url + '.git')
    except configparser.DuplicateSectionError:
        raise configparser.DuplicateSectionError(
            'There seems to be a duplicate section in your config. Try giving the repository URL by using --url.')


def date_convert(date):
    """
    Converts ISO8601 date and time and returns only the date.

    Parameters
    ----------
    date: str
        datetime string.

    Returns
    -------
    date: str
        Date as Y-m-d format..

    """
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%Sz')
        date = date.strftime('%Y-%m-%d')
    except ValueError:
        date = dateutil.parser.parse(date).date().strftime('%Y-%m-%d')
    return date


def multi_key_gitlab(value):
    """
    Returns the username, if an exception occurs None is returned.

    Parameters
    ----------
    value: dict
        A dictionary of GitLab.

    Returns
    -------
    value: str or None
        Username or none.
    """

    try:
        return value['owner']['username']
    except (KeyError, TypeError):
        return None


def description(provider=None, repo_name=None, tags_number=None):
    """
    Description generator.

    Parameters
    ----------
    provider: str
        Name of the Git host.
    repo_name: str
        Repository name.
    tags_number: str or int
        Number of tags.
    
    Return
    ------
    tabulate: str
        A tabulated structure of the input.
    """
    table = [
        ['Provider', provider],
        ['Repository Name', repo_name],
        ['Number of Tags', tags_number]
    ]

    return tabulate(table, tablefmt="grid")


class Init:
    """
    Creates ``.rex`` and ``CHANGELOG`` file depending on the format given, if no format if given ``CHANGELOG.md`` is
    created.

    >>> rex init
    Created .rex config file at <user home path>
    """

    def __init__(self, location=Path.home()):
        self.location = location

        self.config_file_path = Path(os.path.join(self.location, CONFIG_FILE_NAME))

    @property
    def config(self):

        if self.config_file_path.is_file():
            config_file = configparser.ConfigParser()
            config_file.read(self.config_file_path)
            return self.config_file_path, config_file
        else:
            self._init_config()

        return self.config_file_path

    def _init_config(self):

        config = configparser.ConfigParser()

        config['DEFAULT'] = {
            'Version': version.__version__,
            'CheckCycle': 10,
            'GitHubKey': '',
            'GitLabKey': ''
        }

        with open(self.config_file_path, 'w') as configfile:
            config.write(configfile)

    @config.setter
    def config(self, config_dict):

        assert type(config_dict) == dict

        self.config_file_path, config_file = self.config

        exists, config, dict_key = self._check_config_property(config_dict)

        if not exists:
            if config_dict[dict_key]['Key']:
                value = config['DEFAULT']['githubkey'] if config_dict[dict_key]['Provider'] is 'github' else \
                    config['DEFAULT']['gitlabkey']
                config_dict[dict_key]['Key'] = value

            config.read_dict(config_dict)
            with open(self.config_file_path, 'w') as configfile:
                config.write(configfile)

    def _check_config_property(self, config_dict):
        config = configparser.ConfigParser()
        config.read(self.config_file_path)

        dict_key = next(iter(config_dict.keys()))
        exists = dict_key in config.sections()

        return exists, config, dict_key


if __name__ == '__main__':
    a = Init()
    # print(a.config)
    # a.config = {
    #     'github:release-exporter': {
    #         'Key': True,
    #         'URL': 'https://',
    #         'RepoName': 'release-exporter',
    #         'Provider': 'github'
    #     }
    # }
    print(a.config)
