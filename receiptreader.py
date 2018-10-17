import io, os, requests, json, base64, re, time

with open("api-key") as f:
    key = f.read()

input_file = "pics/beer.jpg"
with open(input_file, 'rb') as image:
    contents = image.read()
encoded_string = base64.b64encode(contents).decode('UTF-8')
body = {
  "requests":[
    {
      "image":{
        "content": encoded_string
      },
      "features":[
        {
          "type":"TEXT_DETECTION"
        }
      ]
    }
  ]
}
json_body = json.dumps(body)
r = requests.post("https://vision.googleapis.com/v1/images:annotate?key="
                  +key, json_body)
results = r.json() # Json File that the Google Vision API Outputs

# FIND OUT Y COORDINATES OF THE PRICES

textAnnotations = results["responses"][0]["textAnnotations"]
priceToLine = {} # Dictionary that maps prices on the receipt to their y coordinates (line number)

for word in textAnnotations[1:]: # iterating through the words that the Google Vision API recognized
    currWord = word["description"]
    if re.match("^\$?\d{1,4}\.\d{2}", currWord):
        priceToLine[currWord] = max([currDict["y"] for currDict in word["boundingPoly"]["vertices"]])

# FIGURE OUT PRICES OF ITEMS

itemToPrice = {} # Dictionary that maps items on the receipt to their prices
itemToLocation = {} # Dictionary that maps items to their locations on the receipt
 
for word in textAnnotations[1:]:
    currItem = word["description"]
    if re.match("^\$?\d{1,4}\.\d{2}", currItem):
        continue
    itemToLocation[currItem] = max([currDict["y"] for currDict in word["boundingPoly"]["vertices"]])
    for price, lineNumber in priceToLine.items():
        if abs((itemToLocation[currItem] - lineNumber)) < 12:
            if currItem.lower() == "subtotal" or currItem.lower() == "sub total":
                subtotal = price
                print("subtotal:", subtotal)
            elif currItem.lower() == "tax":
                tax = price
                # print("tax:", tax)
            elif re.match("\d+", currItem):
                itemToPrice[currItem] = price
            elif re.match("\%", currItem) or re.match("\$", currItem):
                continue
            elif price in itemToPrice.values(): # want to append to already added key
                for addedItem, cost in itemToPrice.items():
                    if price == cost and (abs(itemToLocation[currItem] - itemToLocation[addedItem]) < 12):
                        itemToPrice[addedItem + ' ' + currItem] = itemToPrice[addedItem]
                        itemToLocation[addedItem + ' ' + currItem] = itemToLocation[addedItem]
                        del itemToPrice[addedItem]
                        del itemToLocation[addedItem]
                        break
            else:
                itemToPrice[currItem] = price
print("Here are the items that you ordered:")
#time.sleep(1)
for key, value in itemToPrice.items(): # SANITY CHECK
    print(key,value)
#time.sleep(1)
# print("Please list the names of everyone who just ate. Type 'Done' when finished.")
# names = []
# while True:
#     currName = input("Name: ")
#     if currName.lower() == "done":
#         break
#     else:
#         names.append(currName)

itemToPeople = {}

for item in itemToPrice.keys():
    itemToPeople[item] = []
    print("Who ordered the " + item + "? Hit enter when finished.")
    while True:
        name = input("Name: ")
        if name.lower() == "":
            break
        itemToPeople[item].append(name)

peopleToPay = {}

for item, people in itemToPeople.items():
    for p in people:
        toAdd = float(itemToPrice[item]) / len(people)
        if p in peopleToPay.keys():
            peopleToPay[p] += toAdd
        else:
            peopleToPay[p] = toAdd

for item in peopleToPay.items():
    print(item)
#print(r.text)

