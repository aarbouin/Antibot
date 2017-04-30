import sys
from os.path import splitext, basename, dirname, abspath

from antibot.domain.configuration import Configuration


def build_configuration(args):
    sys.path.insert(0, dirname(abspath(args.conf_file)))
    conf = __import__(splitext(basename(args.conf_file))[0])
    return Configuration(
        jid=conf.jid,
        password=conf.password,
        base_url=conf.base_url,
        static_dir=conf.static_dir,
        plugins_package=conf.plugins_package,
        rooms_to_join=conf.rooms_to_join,
        api_token=conf.api_token
    )
