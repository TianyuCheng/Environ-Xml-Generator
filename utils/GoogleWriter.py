# import keyring manager
from keyring import get_password, set_password

# import getpass function for password mask
from getpass import getpass 

# import google api for spreadsheet reading
import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service

class SpreadsheetWriter(object):

    """ A class wrapper for writing to the Google SpreadSheet """

    def __init__(self, username, doc_name):
        """ @todo: init the account, checking the account username and password. If not exist, asking user for password
        
        @username: the username for authentication
        @doc_name: the document to be read
        """
        # setting up the account
        self.doc_name = doc_name
        self.username = username
        self.password= get_password("xml_generator", username)

        self.register_password = False

        # setting up the password if not found
        if self.password is None:
            self.password = getpass("Password:")
            self.register_password = True
        
        # login with the account
        self.__authenticate__()


    def __authenticate__(self):
        """@todo: login with authentication.

        :username: @google account username
        :password: @google account password
        :document: @filename on the google drive
        :returns: @None

        """
        # Google Docs Login
        try:
            gd_client = gdata.spreadsheet.service.SpreadsheetsService()
            gd_client.email = self.username
            gd_client.password = self.password
            gd_client.source = 'xml-generator'
            gd_client.ProgrammaticLogin()
        except BadAuthentication, e:
            raise   #authentication failure

        # authentication success
        self.gd_client = gd_client

        # save password if needed
        if self.register_password:
            set_password('xml_generator', self.username, self.password)

        # get the spread with exact query
        q = gdata.spreadsheet.service.DocumentQuery()
        q['title'] = self.doc_name
        q['title-exact'] = 'true'

        # fetch the data
        feed = gd_client.GetSpreadsheetsFeed(query=q)
        # if len(feed.entry) == 0:
        #     print "The spreadsheet %s has not been found in your Google Drive!" % self.doc_name
        #
        # self.spreadsheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
        # self.feed = self.gd_client.GetWorksheetsFeed(self.spreadsheet_id)

    # def get_worsksheet_feeds(self, callback = lambda s : s):
    #     # store as a list
    #     self.worksheets = [(callback(worksheet.title.text), worksheet.id.text.rsplit('/', 1)[1]) for worksheet in self.feed.entry]
    #
    #     # store as a dictionary
    #     self.worksheets_dict = dict(self.worksheets)
    #     return self.worksheets_dict
    #
    # def read_worksheet(self, worksheet_feed):
    #     """@todo: read the worksheet by id/index
    #
    #     :worksheet_id: @the index of worksheet in the spreadsheet, 
    #                     starting from 0
    #     """
    #     return self.gd_client.GetListFeed(self.spreadsheet_id, worksheet_feed).entry
    #
    # def menu(self):
    #     """@todo: menu for options
    #         :returns: @(title, feed) of worksheet
    #                   @dictionary of feeds if option 0 is selected
    #     """
    #     print "0) All"  # add default all options
    #     for index, worksheet in enumerate(self.worksheets):
    #         print "%d) %s" % (index + 1, worksheet[0])
    #
    #     print "-----------------------------------------------------"
    #     print "Input the worksheet id that you want to work on"
    #     option = input("Input: ")
    #
    #     if option > len(self.worksheets):
    #         print "Index Out of Bounds! Abort!"
    #         raise # failure to choose correct index
    #
    #     if option == 0:
    #         return self.worksheets_dict
    #
    #     return self.worksheets[option - 1]
