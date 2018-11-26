import json


class JsonLinesExportPipeline(object):

    data_path = 'data/'
    file = None

    def open_spider(self, spider):
        self.file = open(self.data_path + spider.name + '.jsonl', 'w')
        return

    def close_spider(self, spider):
        self.file.close()
        return

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line)
        return item
