from tornado import web, ioloop, httpserver
import json
import pandas
import os
#test
#test
class MainHandler(web.RequestHandler):
    def get(self):
        self.write("Welcome to Matt's API!!")

class CountHandler(web.RequestHandler):
    def get(self):
        self.clear_header('Content-Type')
        self.set_header('Content-Type', 'application/json')

        #read csv
        df = pandas.read_csv("csv/dogs.csv")

        #get provided url params
        urlParams = self.request.arguments
        
        #create empty lists for valid and invalid params along with valid param values
        correctParams = []
        invalidParams = []
        valuesOfParams = []

        #sort and append the valid or invalid params depending on the loaded csv data frame
        [correctParams.append(x) if x in df else invalidParams.append(x) for x in urlParams]

        #if there is at least 1 invalid param, set response to bad request (400) and return the invalid params    
        if len(invalidParams) > 0:
            [inv.encode('UTF8') for inv in invalidParams]
            invalidParams.sort()
            response = {
                "unknown fields": invalidParams
            }
            self.write(json.dumps(response))
            self.set_status(400)

        #process the valid params with a response status 200 OK
        else:
            df = df.apply(lambda x: x.astype(str).str.lower() if(x.dtype == 'object') else x)
            #retrieve valid param's values
            [valuesOfParams.append(self.get_argument(u).lower()) for u in correctParams]
            #create a query based on the valid param values on the specific columns in the data frame
            queryBuilder = (df[correctParams].isin(valuesOfParams)).all(axis=1)
            #recreate the data frame with the applied query
            df = df[queryBuilder]
            #get the result count
            countResult = len(df)
            #provide response
            response = {
                "count": countResult
            }
            self.write(json.dumps(response))
            self.set_status(200)
        #reset the params list
        correctParams = []
        invalidParams = []

        
#configure endpoints
def entrypoint():
    return web.Application([
        ("/", MainHandler),
        ("/count", CountHandler
        )], debug=True)

if __name__ == "__main__":
    app = entrypoint()
    http_server = httpserver.HTTPServer(app)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    ioloop.IOLoop.current().start()