import PAsearchSites
import PAgenres
import PAactors
import ssl
from dateutil.relativedelta import relativedelta
from lxml.html.soupparser import fromstring

def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
    if searchSiteID != 9999:
        siteNum = searchSiteID

    url = PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle.replace('%20', '-')
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

    try:
        searchResult = HTML.ElementFromURL(url)
    except:
        # its helpful for linux users, who has "sslv3 alert handshake failure (_ssl.c:590)>" @kamuk90
        req = urllib.Request(url, headers=headers)
        resp = urllib.urlopen(req, context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        htmlstring = resp.read()
        searchResult = fromstring(htmlstring)



    titleNoFormatting = searchResult.xpath('//div[@class="videoTitleIntro"]')[0].text_content().strip()
    curID = url.replace('/','_').replace('?','!')

    releaseDate = parse(searchResult.xpath('//div[@class="introDatePublished"]')[0].text_content().strip()).strftime('%Y-%m-%d')
    if searchDate:
        score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
    else:
        score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

    results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = releaseDate + " - " + titleNoFormatting + " [HotGuysFuck] ", score = score, lang = lang))

    return results


def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE CALLED*******')

    pageURL = str(metadata.id).split("|")[0].replace('_','/').replace('!','?')

    Log('scene url: ' + pageURL)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
    try:
        detailsPageElements = HTML.ElementFromURL(pageURL)
    except:
        req = urllib.Request(pageURL, headers=headers)
        resp = urllib.urlopen(req, context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        htmlstring = resp.read()
        detailsPageElements = fromstring(htmlstring)

    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'HotGuysFuck'

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="videoTitleIntro"]')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="descriptionIntro"]/p')[0].text_content().strip()

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteID).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="introDatePublished"]')[0].text_content().strip()
    if len(date) > 0:
        date_object = datetime.strptime(date, '%b %d,%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actors
    actors = detailsPageElements.xpath('//span[@class="bioData"]/a')
    if len(actors) > 0:
        if len(actors) == 3:
            movieGenres.addGenre("Threesome")
        if len(actors) == 4:
            movieGenres.addGenre("Foursome")
        if len(actors) > 4:
            movieGenres.addGenre("Orgy")
        for actorLink in actors:
            actorName = str(actorLink.text_content().strip())
            actorPhotoURL = ""
            movieActors.addActor(actorName,actorPhotoURL)

    ### Posters and artwork ###

    # Phtos not working (need cookies, don't know how to implement)

    

    return metadata