import uuid
from models.VisitedURL import VisitedURL
import json

def markVisited(table, visitedURL: VisitedURL):
    table.put_item(Item=vars(visitedURL))

def enqueue(queue, visitedURL: VisitedURL):
    queue.send_message(MessageBody=json.dumps(vars(visitedURL)))

def batchGetItems(ddbresource, urls: list[str], runId: str):
    keys = []
    for url in urls:
        keys.append({
            "visitedURL": url,
            "runId": runId
        })
    input = {
        'VisitedURLs': { 'Keys': keys}
    }
    response = ddbresource.batch_get_item(RequestItems=input)
    items = response['Responses']['VisitedURLs']
    return items

def batchPutItems(table, urls, runId, sourceUrl, rootUrl):
    with table.batch_writer() as writer:
        for item in urls:
            writer.put_item(Item={
                "visitedURL": item,
                "runId": runId,
                "sourceURL": sourceUrl,
                "rootURL": rootUrl
            })

def batchEnqueue(queue, urls, runId, sourceUrl, rootUrl):
    items = []
    for item in urls:
        item = {
            "visitedURL": item,
            "runId": runId,
            "sourceURL": sourceUrl,
            "rootURL": rootUrl
        }
        items.append(item)

    batchedItems = list()
    batchSize = 10
    for i in range(0, len(items), batchSize):
        batchedItems.append(item[i:i+batchSize])
    
    print(f"Constructed {len(batchedItems)} batches for {len(items)} items")

    # Put to SQS in batches of 10

    batchSendCount = 0
    for batch in batchedItems:
        entries = list()
        for item in batch:
            pass