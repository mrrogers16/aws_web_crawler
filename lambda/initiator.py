import logging 
import boto3

from models.VisitedURL import VisitedURL
from utilities.util import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RUN_ID_DELIM = '#'

ddb = boto3.resource('dynamodb')
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='Crawler')
table = ddb.Table('VisitedURLs')

def handle(event, context):
    rootUrl = event["rootURL"]
    runId = generateRunId()
    logger.info("Initiating crawl - runId=-" + runId + " , rootUrl=" + rootUrl)

    # Convert to Model
    urlToVisit = VisitedURL(rootUrl, runId, None, rootUrl)

    # Mark as visited
    markVisited(table, urlToVisit)
    
    # Enqueue
    print(f"Enqueueing {json.dumps(vars(urlToVisit))}")
    enqueue(queue, urlToVisit)

'''
Generates a runId with format date#uuid'''