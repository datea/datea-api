import csv, codecs, cStringIO


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.writer = csv.writer(f, dialect=dialect, **kwds)
        #self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
