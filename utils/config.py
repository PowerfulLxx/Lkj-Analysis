from argparse import ArgumentParser

class Config(object):
    def __init__(self):
        self.csv_path = None
        self.parser = self.setup_parser()
        self.args = vars(self.parser.parse_args())
        self.__dict__.update(self.args)
    def setup_parser(self):
        parser = ArgumentParser(description='config')
        parser.add_argument('-csv_path',default='None',type=str)
        return parser
