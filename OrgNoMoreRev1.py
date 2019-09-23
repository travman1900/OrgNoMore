import requests
import json
from pprint import pprint
import glob
from os.path import basename, join
import re
from os import rename, makedirs
from threading import Thread
from time import sleep
import configparser
import ast
import time
import datetime
config = configparser.ConfigParser()
config.read('config.ini')

TVDB_TOKEN = ""
TVDB_URL = "https://api.thetvdb.com"

# * File path to look for episode files
#! create check to make folders if they don texist
#INCOMING_SHOWS = "C:\\Users\\Travis\\Desktop\\Test\\"
INCOMING_SHOWS = config['DEFAULT']['source_shows_directory']
#INCOMING_MOVIES = "C:\\Users\\Travis\\Desktop\\TestA\\"
INCOMING_MOVIES = config['DEFAULT']['source_movies_directory']
#DESTINATION_SHOWS = "C:\\Users\\Travis\\Desktop\\Test\\Completed\\"
DESTINATION_SHOWS = config['DEFAULT']['shows_destination_directory']
#DESTINATION_MOVIES = "C:\\Users\\Travis\\Desktop\\TestA\\Completed\\"
DESTINATION_MOVIES = config['DEFAULT']['movies_destination_directory']

FILE_TYPE = ast.literal_eval(config['DEFAULT']['file_type'])

print(DESTINATION_MOVIES)
print(INCOMING_MOVIES)
print(INCOMING_SHOWS)
print(DESTINATION_SHOWS)
print(FILE_TYPE)

#file_type = ast.literal_eval(config['DEFAULT']['file_type'])

# * ----------------- Movie Info -----------------
#! cleanup output for movie info (maybe jsonify?)


def searchMovie(movieName):
    url = "http://www.omdbapi.com/"
    params = {
        "apikey": "",
        "type": "movie",
        "t": movieName
    }
    response = requests.get(url, params=params)
    if response.status_code is not 200:
        print("No connection to OMDB")
    else:
        with open("movieresults.json", "w+") as f:
            json.dump(response.json(), f, indent=4)
        result = response.json()
        #print(len(result))
        newName = f"{result['Title']} ({result['Year']})"
        return newName

# * ----------------- Series Info -----------------
#! cleanup/streamline getSeriesID and getEpisodeInfo into 1 function to reduce clutter


def getSeriesID(series):
    """Grabs series ID and Name from TVDB
    
    Arguments:
        series {int} -- SeriesID
    
    Returns:
        json -- SeriesID and Name
    """

    endpoint = "/search/series"
    headers = {"Authorization": f"Bearer {TVDB_TOKEN}"}
    params = {"name": series}

    response = requests.get(
        TVDB_URL + endpoint, params=params, headers=headers
    )
    response = response.json()

    results = {
        "name": response["data"][0]["seriesName"],
        "id": response["data"][0]["id"],
    }

    return results

#! as stated above


def getEpisodeInfo(seriesId, season, episode):
    """Gets Episode info in a JSON format
    
    Arguments:
        seriesId {int} -- series ID from TVDB
        season {int} -- Season of Air Episode
        episode {int} -- Episode Number of respective season
    
    Returns:
        json -- dictionary of all the information above
    """
    endpoint = f"/series/{seriesId}/episodes/query"
    headers = {"Authorization": f"Bearer {TVDB_TOKEN}"}
    params = {
        "id": seriesId,
        "airedSeason": int(season),
        "airedEpisode": int(episode),
    }

    response = requests.get(
        TVDB_URL + endpoint, params=params, headers=headers
    )
    response = response.json()
    with open("results.json", "w+") as f:
        json.dump(response, f, indent=4)
    return response


# * ----------------- File Crawler -----------------
#! make the crawler skip the "Sorted" folders
def directoryCrawler(filePath):  # + "*" + "mkv",
    #files = [file for file in glob.glob(filePath + "*" + ft, recursive=True)] #! add ability to find more filetypes than just mkv
    #files = [file for path in Path(src_dir).glob("*"+FILE_TYPE)]
    fileList = []
    for ft in FILE_TYPE:
        files = [file for file in glob.glob(
            filePath + "*" + ft, recursive=True)]
        for item in files:
            fileName = basename(item)
            fileList.append(fileName)
    return fileList


# * ----------------- File Parsing -----------------
#! streamline parsing/rename function since its onl yused for episdoes
#! also look into better regex matching for alternative file naming schemes. Idk how lul
def parseFile(filename):
    # split file name at '.' to get file extension
    filename = filename.split(".")
    # extention is at index 1 of the list we just made
    extension = filename[1]
    # split the first index of 'file' into a list
    filename = filename[0].split("-")
    # get episode/season, strip whitespace and S/E in name
    episodeNum = int(filename[1][4:].strip().strip("E"))
    seasonNum = int(filename[1][:4].strip().strip("S"))

    seriesName = filename[0].strip()
    # make new dictionary to hold the info we want
    info = {
        "series": seriesName,
        "episodeNum": episodeNum,
        "seasonNum": seasonNum,
        "extension": extension
    }
    return info

#! maybe make this a bit cleaner upstream. Might need a rewrite


def newFilename(filelist, mediatype):
    if mediatype == "episodes":
        for item in filelist:
            episodeInfo = parseFile(item)

            # looking up series info and store dcitionary with Series Name and TVDB ID
            seriesResults = getSeriesID(episodeInfo["series"])
            # Get series ID from seriesResults
            seriesId = seriesResults["id"]
            #! CLEANUP THIS SHIT / we dont needs all these extra variables. Was placed for readability. Could drop atleast 15 lines here
            #! also cleanup upstream data parsin
            # Original File Info
            originalSeason = episodeInfo["seasonNum"]
            originalEpisode = episodeInfo["episodeNum"]
            extension = episodeInfo["extension"]
            # Grab updated Info from TVDB
            episodeResults = getEpisodeInfo(
                seriesId, originalSeason, originalEpisode)
            # Updated show info
            series = seriesResults["name"]
            episodeName = episodeResults["data"][0]["episodeName"]
            seasonNum = episodeResults["data"][0]["airedSeason"]
            episodeNum = episodeResults["data"][0]["airedEpisodeNumber"]
            if len(str(episodeNum)) < 2:
                episodeNum = f"0{episodeNum}"
            else:
                pass
            if len(str(seasonNum)) < 2:
                seasonNum = f"0{seasonNum}"
            else:
                pass
            # * Generate the new file name
            newFileName = f"{series} - S{seasonNum}E{episodeNum} - {episodeName}.{extension}"
            #* mk series - Mk seasonNum
            #* add create folder for media

            print(newFileName)
            #* create series folder if doesnt exist
            makedirs(join(DESTINATION_SHOWS, series), exist_ok=True)
            #* make season folder if doesnt exist
            makedirs(join(DESTINATION_SHOWS, series,
                          f"Season {seasonNum}"), exist_ok=True)
            #* rename episode into corosponding season/series folder
            rename(join(INCOMING_SHOWS, item), join(
                DESTINATION_SHOWS, series, f"Season {seasonNum}", newFileName))

    elif mediatype == "movies":
        for item in filelist:
            #split file name at '.' to get file extension
            filename = item.split(".")
            #extention is at index 1 of the list we just made
            extension = filename[1]
            try:
                # * index 0 of filename is the name minus the extension
                newFileName = searchMovie(filename[0])
                #print("Hi")

                makedirs(join(DESTINATION_MOVIES, newFileName), exist_ok=True)
                rename(join(INCOMING_MOVIES, item), join(
                    DESTINATION_MOVIES, newFileName, f"{newFileName}.{extension}"))
            except KeyError as e:
                print(e)

#! remember to add a check to create directories for "Sorted" folder if they dont exist
#def supportingFiles():
    #for item in filelist:

#! incorporte watchdog for folder watching here.


def main():
    print("STARTING!")
    #! make check to see if folder is empty and if it is then do nothing
    while True:  # ! add watchdog
        try:
            episodelist = directoryCrawler(INCOMING_SHOWS)
            movielist = directoryCrawler(INCOMING_MOVIES)
            if movielist:
                print(movielist)
                newFilename(movielist, "movies")
            if episodelist:
                print(episodelist)
                newFilename(episodelist, "episodes")

            sleep(10)
        except KeyboardInterrupt:
            print("Exited!")


if __name__ == "__main__":
    t = Thread(target=main)
    try:
        t.start()
    except KeyboardInterrupt:
        print("Exited!")
