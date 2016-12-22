import os
import cStringIO
from logging import getLogger
from demjson import jsonlint
from demjson import decode

from graphite_api.node import BranchNode

DEMJSON_ARGS = {
    'strict': True,
    'allow_comments': True,
    'allow_trailing_comma': True,
    'allow_single_quoted_strings': True,
}


class Tags(object):
    def __init__(self, config):
        self.logger = getLogger(__name__)
        self.tags = {}
        tags_config = config.get('tags')
        if not tags_config:
            self.logger.error("No tags config found!")
            return

        self.prefix = tags_config.get('prefix', 'tags')
        self.tags_cfg_file = tags_config.get('file')
        if not self.tags_cfg_file:
            self.logger.error("No tags file in config found!")
            return

        self._load_config()

    def _load_config(self):
        if not os.path.isfile(self.tags_cfg_file):
            msg = "Tags file does not exists: %s"
            self.logger.error(msg, self.tags_cfg_file)
            return

        jsonlint_args = ['--verbose', '--strict']
        for k, v in DEMJSON_ARGS.items():
            if k.startswith('allow_') and v is True:
                jsonlint_args.append('--allow=' + k[len('allow_'):])
        jsonlint_args.append(self.tags_cfg_file)

        to_log = cStringIO.StringIO()
        ret = jsonlint(stdout=to_log, stderr=to_log).main(jsonlint_args)
        if ret:
            to_log.seek(0)
            self.logger.error("Invalid JSON file %s", self.tags_cfg_file)
            self.logger.error(to_log.read())
        else:
            with open(self.tags_cfg_file, 'r') as fd:
                self.tags = decode(fd.read(), **DEMJSON_ARGS)

    def find_nodes(self, query):
        """Query format:
            <prefix>.<tag_type> or
            <prefix>.<tag_type>.<tag>
        """

        query = query.pattern.split('.')
        if len(query) < 2 or query[0] != self.prefix:
            return []

        try:
            if len(query) == 2:
                return [BranchNode(tag) for tag in self.tags[query[1]]]

            if len(query) == 3:
                return [BranchNode(item) for item in self.tags[query[1]][query[2]]]
        except KeyError:
            return []
