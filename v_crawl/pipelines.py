import json


class JsonLinesExportPipeline(object):

    url_file = 'data/items.jsonl'
    file = None

    def open_spider(self, spider):
        self.file = open(self.url_file, 'w')
        return

    def close_spider(self, spider):
        self.file.close()
        return

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line)
        return item
