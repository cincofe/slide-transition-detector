from abc import ABCMeta, abstractmethod
# import sys


class Source(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def contents(self):
        pass

    def __len__(self):
        # return sys.maxint
        return 10_000_000_000  # Arbitrary large number for compatibility with Python 3.x

class ListSource(Source):
    def __init__(self, list):
        self.list = list

    def contents(self):
        return self.list

    def __len__(self):
        return len(self.contents())


class AnalyzerSource(Source):
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def contents(self):
        for content in self.analyzer.analyze():
            yield content
