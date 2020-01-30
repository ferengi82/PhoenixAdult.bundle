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
        searchPostNum = 1
        for searchResult in searchResults.xpath('//div[@class="videoarea clear"]'):
            PageNum = searchPageNum
            Log("PageNum: " + str(PageNum))
            PostNum = searchPostNum
            Log("PostNum: " + str(searchPostNum))
            titleNoFormatting = searchResult.xpath('.//h3/a')[0].text_content().strip()
            Log("title:" + titleNoFormatting)

            curID = (PAsearchSites.getSearchSearchURL(siteNum) + "/sd3.php?show=recent_video_updates&page=" + str(PageNum)).replace('/','+').replace('?','!') + "-" + str(PostNum)

            Log("curID: " + curID)
            releaseDate = parse(searchResult.xpath('.//p[@class="date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
            Log("releaseDate: " + releaseDate)

            actorNames = searchResult.xpath('.//span[@style="color:#FF0000; font-weight:bold;"]')[0].text_content().strip()
            Log("actors: " + actorNames)
            
            if searchDate:
                score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
                Log("score: " + str(score))
            else:
                score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                Log("score: " + str(score))
            results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum) , name = releaseDate + " - " + actorNames + " / " + titleNoFormatting + " [AllAnalAllTheTime] ", score = score, lang = lang))
            Log("....")
            searchPostNum +=1
        searchPageNum += 1
        Log("")
        Log("--------------------------")
    return results

def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE CALLED*******')

    url = str(metadata.id).split("|")[0].replace('+','/').replace('!','?')

    PostNum = url.rsplit("-")[1]
    Log("updatePostNum:" + PostNum)
    url = url.rsplit("-")[0]
    Log("updateURL:" + url)
    detailsPageElements = HTML.ElementFromURL(url)

    #detailsPageElements = detailsPageElements.xpath('//div[@class="videoarea clear"]')[int(PostNum)]

    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'AllAnalAllTheTime'

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="videoarea clear"]/h3/a')[int(PostNum)-1].text_content().strip()
    
    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="video_details clear"]/p')[int(PostNum)-1].text_content().split(':')[1][:-15].strip()

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteID).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    genres = detailsPageElements.xpath('//div[@class="videoarea clear"]/div/h4/a')[int(PostNum)-1].text_content().split(':')[1].strip()
    Log("genres: " + genres)
    if len(genres) > 0:
        if genres == '100% Anal':
            genres = "anal"
        movieGenres.addGenre(genres)
    movieGenres.addGenre("anal")

    # Release Date
    date = detailsPageElements.xpath('//div[@class="videoarea clear"]/p[@class="date"]')[int(PostNum)-1].text_content().strip().replace('th','')
    if len(date) > 0:
        date_object = datetime.strptime(date, '%B %d %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    
    # Actors
    movieActors.addActor(detailsPageElements.xpath('//div[@class="video_details clear"]/p/span')[int(PostNum)-1].text_content().strip(),"")
            
    return metadata