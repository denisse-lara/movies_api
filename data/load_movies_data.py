#! python3
# load_movies_data - Loads movies data from .tsv file.
# Download the .tsv file from: https://datasets.imdbws.com/title.basics.tsv.gz

import csv


if __name__ == "__main__":
    try:
        with open("data.tsv", newline="\n") as tsv_file:
            dict_reader = csv.DictReader(
                tsv_file,
                fieldnames=[
                    "tconst",
                    "titleType",
                    "primaryTitle",
                    "originalTitle",
                    "isAdult",
                    "startYear",
                    "endYear",
                    "runtimeMinutes",
                    "genres",
                ],
                delimiter="\t",
            )

            outputFile = open('movies.tsv', 'w', newline='')
            outputDictWriter = csv.DictWriter(outputFile, ["title", "release_year"])
            outputDictWriter.writeheader()

            for row in dict_reader:
                if row["titleType"] == "movie":
                    outputDictWriter.writerow({"title": row["originalTitle"], "release_year": row["startYear"]})
            outputFile.close()
    except OSError:
        print("Download the IMDB file and rename it to data.tsv")
