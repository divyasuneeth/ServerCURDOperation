from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Restaurant
import cgi


engine=create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession= sessionmaker(bind=engine)
session=DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery =session.query(Restaurant).filter_by(
                id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    message=""
                    message += "<html><body>"
                    message += "<h1>"
                    message +="Are you sure you want to "
                    message +="delete : %s" %myRestaurantQuery.name
                    message +="</h1>"
                    message +="<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/delete' >"% restaurantIDPath
                    message +="<input type='submit' value='Delete'>"
                    message +="</form>"
                    message +="</body></html>"


                    self.wfile.write(message)


            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += myRestaurantQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurant/%s/edit' >" % restaurantIDPath
                    output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name
                    output += "<input type = 'submit' value = 'Rename'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output)


                return

            if self.path.endswith("/restaurant"):
                items=session.query(Restaurant).all()
                output=""
                self.send_response(200);
                self.send_header('Content-type', 'text/html');
                self.end_headers();

                output += "<html><body>"
                output += "<h2><a href='/restaurant/new'>Make a New Restaurant</a></h2>"
                for item in items:
                    output += item.name
                    output+="<br><a href='/restaurant/%s/edit'>Edit</a>" % item.id
                    output+="<br><a href='/restaurant/%s/delete'>Delete</a>" % item.id
                    output += "</br></br></br>"

                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurant/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurant/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return


        except:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                ctype,pdict= cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype =='multipart/form-data':
                    restaurantIDPath = self.path.split("/")[2]

                    myRestaurantQuery=session.query(Restaurant).filter_by(
                    id= restaurantIDPath).one()
                    session.delete(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurant')
                    self.end_headers()

                    
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]

                    myRestaurantQuery = session.query(Restaurant).filter_by(
                        id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurant')
                        self.end_headers()

            if self.path.endswith("/restaurant/new"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurant')
                self.end_headers()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                newRestaurant = Restaurant(name=messagecontent[0])
                session.add(newRestaurant)
                session.commit()

        except:
            pass



if __name__ == '__main__':
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()
