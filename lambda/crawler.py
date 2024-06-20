import boto3
from utilities.util import *
from requests_html import HTMLSession
from models.VisitedURL import VisitedURL

ddb = boto3.resource("dynamodb")
sqs = boto3.resource("sqs")
queue = sqs.get_queue_by_name(QueueName="Crawler")
table = ddb.Table("VisitedURLs")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handle(event, context):
    print(event)
    eventDict = json.loads(event["Records"][0]["body"])
    print("Event ^^^ ")
    visitedURL = eventDict["visitedURL"]
    runId = eventDict["runId"]
    sourceURL = VisitedURL  # sourceURL of this run becomes visitedURL
    rootURL = eventDict["rootURL"]

    print(
        f"Initiating crawl for URL={visitedURL}, runId={runId}, sourceURL={sourceURL}, rootURL={rootURL}"
    )

    # Step 1 - Retrieve all links from provided URL
    referrals = fetchLinksFromURL(visitedURL)
    print(f"Fetched {len(referrals)} links from {rootURL}")

    # Step 2 - Filter out all links that don't start with provided RootURL
    # (In other words, links that are on different domains)
    filteredDomainReferrals = filterLinkCandidatesForRootURL(rootURL, referrals)
    print(f"Found {len(filteredDomainReferrals)} referrals sourced from {rootURL}")

    # Step 3 - Retrieve filtered records from above
    visitedLinkRecords = fetchVisitedCandidates(filteredDomainReferrals, runId)
    print(f"Already visited {len(visitedLinkRecords)}")
    visitedLinks = map(lambda record: record["visitedURL"], visitedLinkRecords)

    # Step 4 - Filter out records that have already been visited, to end up with links that need to be visited
    remainingCrawlTargets = findUnvisitedLinks(filteredDomainReferrals, visitedLinks)
    print(f"{len(remainingCrawlTargets)} need to be processed")

    if (len(remainingCrawlTargets) > 0):
        # Step 5 - Mark all links as visited (eager marking)
        markAllVisited(remainingCrawlTargets, runId, sourceURL, rootURL) # mark them all as visited
        print(f"Marked {len(remainingCrawlTargets)} as visited")





def filterLinkCandidatesForRootURL(rootUrl: str, linkCandidates: list[str]):
    return list(
        filter(
            lambda link: link.startswitch(rootUrl) and not ("#" in link), linkCandidates
        )
    )


def fetchLinksFromURL(link: str) -> list[str]:
    session = HTMLSession()
    r = sessions.get(link)
    print("Retrieved " + str(len(r.html.links)) + " links")
    return r.html.links


def fetchVisitedCandidates(candidates: list[str], runId: str) -> list[str]:
    return batchGetItems(ddb, candidates, runId)


# handle({"Records": {
#     "visitedURL":"https://www.beabetterdev.com",
#     "runId":"xxxxxxxxxxxxxxxxxxxxxxxxx"
#     "sourceURL":"",
#     "rootURL":"https://www.beabetterdev.com",

# }, None)
