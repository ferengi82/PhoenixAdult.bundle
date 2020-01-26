import PAsearchSites
import PAgenres
import PAactors

def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
    if searchSiteID != 9999:
        siteNum = searchSiteID
    # get last Page
    searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + "/sd3.php?show=recent_video_updates&page=1")
    lastPage = int(searchResults.xpath('(//div[@class="pagenav"]/a)[last()]')[0].get('href').strip().rsplit('=',1)[1])
    Log("lastPage: " + str(lastPage))

    #debug
    #lastPage = 4

    searchPageNum = 1
    while searchPageNum <= lastPage:
        searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + "/sd3.php?show=recent_video_updates&page=" + str(searchPageNum))
        for searchResult in searchResults.xpath('//div[@class="videoarea clear"]'):
            titleNoFormatting = searchResult.xpath('.//h3/a')[0].text_content().strip()
            Log("title:" + titleNoFormatting)
            curID = searchResult.xpath('.//h3/a')[0].text_content().strip().replace('/','_').replace('?','!')
            Log("curID: " + curID)
            releaseDate = parse(searchResult.xpath('.//p[@class="date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
            Log("releaseDate: " + releaseDate)
            actorNames = searchResult.xpath('.//span[@style="color:#FF0000; font-weight:bold;"]')[0].text_content().strip()
            Log("actors: " + actorNames)
            genres = searchResult.xpath('.//h4/a')[0].text_content().split(':')[1].strip()
            Log("genres: " + genres)
            summary = searchResult.xpath('.//div[@class="video_details clear"]/p')[0].text_content().split(':')[1][:-15].strip()
            Log("summary: " + summary)
            imageUrl = PAsearchSites.getSearchSearchURL(siteNum) + "/" + searchResult.xpath('.//div[@class="video_pic"]/a/img')[0].get("src").replace('/','_').replace('?','!')
            Log("imageURL: " + imageUrl)
            if searchDate:
                score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
                Log("score: " + str(score))
            else:
                score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                Log("score: " + str(score))
            results.Append(MetadataSearchResult(id = titleNoFormatting + "|" + releaseDate + "|" + actorNames + "|" + genres + "|" + summary + "|" + imageUrl , name = releaseDate + " - " + actorNames + " / " + titleNoFormatting + " [AllAnalAllTheTime] ", score = score, lang = lang))
            Log("....")
        searchPageNum += 1
        Log("")
        Log("--------------------------")
    return results

def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE CALLED*******')

    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'AllAnalAllTheTime'

    # Title
    metadata.title = str(metadata.id).split("|")[0]

    # Summary
    metadata.summary = str(metadata.id).split("|")[4]

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteID).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    genres = str(metadata.id).split("|")[3]
    #if len(genres) > 0:
    #    for genreLink in genres:
    #        genreName = genreLink.text_content().strip().lower()
    #        movieGenres.addGenre(genreName)

    # Release Date
    date = str(metadata.id).split("|")[1]
    if len(date) > 0:
        date_object = datetime.strptime(date, '%B %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actors
    actors = str(metadata.id).split("|")[2].split(',')
    if len(actors) > 0:
        for actorLink in actors:
            actorName = actorLink
            actorPhotoURL = ""
            movieActors.addActor(actorName,actorPhotoURL)

    ### Posters and artwork ###

    # Video trailer background image
    try:
        twitterBG = str(metadata.id).split("|")[5]
        art.append(twitterBG)
    except:
        pass


    j = 1
    Log("Artwork found: " + str(len(art)))
    for posterUrl in art:
        if not PAsearchSites.posterAlreadyExists(posterUrl,metadata):            
            #Download image file for analysis
            try:
                img_file = urllib.urlopen(posterUrl)
                im = StringIO(img_file.read())
                resized_image = Image.open(im)
                width, height = resized_image.size
                #Add the image proxy items to the collection
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
                j = j + 1
            except:
                pass

    return metadata