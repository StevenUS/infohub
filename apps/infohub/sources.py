from .models import InfoSource, Audit
from ..login_reg.models import User
import time
import urllib2
import json


####################################################################
#                                                                  #
# This file should only contain methods used to communicate with   #
# external sources, such as Bing and CNN to retrieve articles      #
#                                                                  #
####################################################################


# Gets info from all active sources the logged in user has added.
def getInfo(user_id):
    # First get the user sources from the database. Only retrieve active sources.
    user_sources = InfoSource.objects.getActive(user_id)

    # Debugging settings
    TheGuardian_ENABLED = True
    CNN_ENABLED = True
    HuffPost_ENABLED = True

    # Loop and retrieve data from each source
    stories = {}
    for source in user_sources:
        if source.source_type == "api" and source.location == "TheGuardian" and TheGuardian_ENABLED:
            recentStories = getInfoGuardian(user_id, source.max_snippets, source.highlight_text)
            if len(recentStories) > 0:
                stories["TheGuardian"] = recentStories
        elif source.source_type == "api" and source.location == "CNN" and CNN_ENABLED:
            recentStories = getInfoCNN(user_id, source.max_snippets, source.highlight_text)
            if len(recentStories) > 0:
                stories["CNN"]  = recentStories
        elif source.source_type == "api" and source.location == "HuffPost" and HuffPost_ENABLED:
            recentStories = getInfoHuffPost(user_id, source.max_snippets, source.highlight_text)
            if len(recentStories) > 0:
                stories["HuffPost"] = recentStories

    # We have hit all the sources. Return the data.
    return stories

# Retrieves info from CNN.
def getInfoCNN(user_id, max_snippets, highlight_text):
    # Get the content from CNN API.
    # See https://newsapi.org/cnn-api for details.
    base_url = "https://newsapi.org/v1/articles?source=cnn&sortBy=top"
    api_key = "f2666e6b10934fb29ebb6849581ab509"
    url = base_url + "&apiKey=" + api_key
    req = urllib2.Request(url)

    content = None
    try:
        resp = urllib2.urlopen(req)
        content = json.load(resp)
    except Exception as e:
        print "DEBUG: urlopen failed for CNN"
        Audit.objects.audit(user_id, "Failed to retrieve info from CNN")
        return []

    # Parse the content and normalize into InfoHub format.
    stories = []
    previous_title = ""
    for story in content["articles"][:max_snippets]: # Account for dupe stories per 9/29/2016
        # NOTE: CNN returns the first story twice (likely bug on their side),
        # so we exlicitely check for that and ignore dupes.

        thumbnail = ""
        if "urlToImage" in story and len(story["urlToImage"]) > 0:
            thumbnail = story["urlToImage"]

        if story["title"] != previous_title:
            stories.append({
                "source" : "CNN News", # Displaying the source is required by CNN if site is public.
                "title" : story["title"],
                "url" : story["url"],
                "description" : story["description"],
                "highlight_text" : highlight_text,
                "image" : thumbnail
            })
            previous_title = story["title"]

    Audit.objects.audit(user_id, "Retrieved info from CNN")
    return stories

# Retrieves info from Guardian.
def getInfoGuardian(user_id, max_snippets, highlight_text):
    base_url = "http://content.guardianapis.com/search?show-fields=thumbnail%2CbodyText"
    api_key = "bf556d7d-da5e-4ec9-bd6a-3eb98645abef"
    url = base_url + "&api-key=" + api_key
    req = urllib2.Request(url)

    content = None
    try:
        resp = urllib2.urlopen(req)
        content = json.load(resp)
    except Exception as e:
        print "DEBUG: urlopen failed for Guardian"
        Audit.objects.audit(user_id, "Failed to retrieve info from Guardian")
        return []

    stories = []
    for story in content["response"]["results"][:max_snippets]:

        thumbnail = ""
        if "thumbnail" in story["fields"] and len(story["fields"]["thumbnail"]) > 0:
            thumbnail = story["fields"]["thumbnail"]

        description = story["fields"]["bodyText"][0:300]
        if description.rfind('.') > 0:
            description = description[:description.rfind('.')+1]

        stories.append({
            "source" : "Guardian",
            "title" : story["webTitle"],
            "url" : story["webUrl"],
            "description" : description,
            "highlight_text" : highlight_text,
            "image" : thumbnail
        })

    Audit.objects.audit(user_id, "Retrieved info from Guardian")
    return stories

def getInfoHuffPost(user_id, max_snippets, highlight_text):
    base_url = "https://newsapi.org/v2/top-headlines?sources=the-huffington-post"
    api_key = "a8fe3c304b85440b96349a807dfa181c"
    url = base_url + "&apiKey=" + api_key
    req = urllib2.Request(url)

    content = None
    try:
        resp = urllib2.urlopen(req)
        content = json.load(resp)
    except Exception as e:
        print "DEBUG: urlopen failed for HuffPost"
        Audit.objects.audit(user_id, "Failed to retrieve info from HuffPost")
        return []

    stories = []
    for story in content["articles"][:max_snippets]:
        
        thumbnail = ""
        if "urlToImage" in story and len(story["urlToImage"]) > 0:
            thumbnail = story["urlToImage"]

        stories.append({
            "source" : "HuffPost",
            "title" : story["title"],
            "url" : story["url"],
            "description" : story["description"],
            "highlight_text" : highlight_text,
            "image" : thumbnail
        })

    Audit.objects.audit(user_id, "Retrieved info from HuffPost")
    return stories
