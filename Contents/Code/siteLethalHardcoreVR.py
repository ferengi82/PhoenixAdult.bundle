import PAsearchSites
import PAgenres
import PAactors
import PAutils


def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="grid-item scene-list-item"]'):
        curID = PAutils.Encode(searchResult.xpath('.//a/@href')[0])
        titleNoFormatting = searchResult.xpath('.//p[contains(@class, "grid-item-title")]//span')[0].text_content().strip()
        releaseDate = parse(searchResult.xpath('.//p[@class="scene-update-stats"]//span')[1].text_content().strip()).strftime('%Y-%m-%d')

        if searchDate:
            score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, siteID, movieGenres, movieActors):
    metadata_id = metadata.id.split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteID) + sceneURL
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1')[0].text_content().strip()

    # Summary
    description = detailsPageElements.xpath('//div[@id="synopsis-full"]//p')
    if description:
        metadata.summary = description[0].text_content().strip()

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteID)

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.tagline = metadata.studio
    metadata.collections.add(metadata.studio)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genre in detailsPageElements.xpath('//meta[@name="Keywords"]/@content')[0].split(','):
        movieGenres.addGenre(genre)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//div[@id="bodyShotModal"]'):
        actorName = actorLink.xpath('.//img/@title')[0]
        actorPhotoURL = ''

        try:
            actorPhotoURL = actorLink.xpath('.//img/@src')[0]
            if 'http' not in actorPhotoURL:
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteID) + actorPhotoURL
        except:
            pass

        movieActors.addActor(actorName, actorPhotoURL)

    # Photos
    art = []
    xpaths = [
        '//meta[@property="og:image"]/@content',
        '//div[contains(@class, "screenshots-block")]//source/@srcset'
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            art.append(poster)

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.google.com'})
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
