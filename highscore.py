from csv import DictReader, DictWriter
from datetime import datetime


class HighScoreTable:
    def __init__(self, path):
        self._path = path
        self.read()

    def is_high_score(self, score):
        return self._table[-1]["score"] < score

    def read(self):
        # load raw table
        f = open(self._path, "r")
        raw = DictReader(f)

        # parse scores
        self._table = list()
        for r in raw:
            r["score"] = int(r["score"])
            self._table.append(r)
        f.close()

        # sort table
        self._table.sort(key=lambda r: r["score"], reverse=True)

    def write(self):
        f = open(self._path, "w")
        w = DictWriter(f, ("name", "time", "score"))
        w.writeheader()
        w.writerows(self._table)
        f.close()

    def add_score(self, score, name):
        self._table.append({"name": name,
                            "time": datetime.now().strftime("%x"),
                            "score": score})
        self._table.sort(key=lambda x: int(x["score"]), reverse=True)
        self._table.pop(-1)
        self.write()

    def names(self):
        for r in self._table:
            yield r["name"]

    def times(self):
        for r in self._table:
            yield r["time"]

    def scores(self):
        for r in self._table:
            yield r["score"]