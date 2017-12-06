from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
import httplib2, socket


SHEETS_DISCOVERY_URL='https://sheets.googleapis.com/$discovery/rest?version=v4'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'


class GoogleSpreadsheet:
    def __init__(self, credentials_json_data, spreadsheet_id, range_name, data=None, major_dimension="ROWS",
                 value_input_option="RAW"):
        self.credentials_json_data = credentials_json_data
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.data = data
        self.major_dimension = major_dimension
        self.value_input_option = value_input_option

    def get_sheets_service(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.credentials_json_data, scopes=SCOPES)
        http = credentials.authorize(httplib2.Http(timeout=120))

        return discovery.build(
            'sheets',
            'v4',
            http=http,
            discoveryServiceUrl=SHEETS_DISCOVERY_URL
        )

    def update(self):
        final_payload = {
            "range": self.range_name,
            "majorDimension": self.major_dimension,
            "values": self.data
        }

        service = self.get_sheets_service()

        try:
            result = service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=self.range_name,
                valueInputOption=self.value_input_option,
                body=final_payload
            ).execute()

            response = {
                "data": result
            }

        except (httplib2.HttpLib2Error, socket.error) as ex:
            response = {
                "error": {
                    "code": 408,
                    "message": "Timeout error. Acessing google spreadsheet api."
                }
            }

        except (HttpError) as ex:
            response = {
                "error": {
                    "code": 400,
                    "message": ex
                }
            }

        return response


def main(credentials_json_data=None, spreadsheet_id="", range_name="", data=None,
         major_dimension="ROWS", value_input_option="RAW"):
    google_spreadsheet = GoogleSpreadsheet(
        credentials_json_data=credentials_json_data,
        spreadsheet_id=spreadsheet_id,
        range_name=range_name,
        data=data,
        major_dimension=major_dimension,
        value_input_option=value_input_option
    )

    response = google_spreadsheet.update()

    print response
    return response


if __name__ == '__main__':
    import argparse
    import json
    import ast

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--spreadsheet_id',
        help="Id of the spreadsheet."
    )
    parser.add_argument(
        '--credentials_json_data',
        help="Crendential from google appengine service account. Pass it as json converted as string"
    )
    parser.add_argument(
        '--range_name',
        help="range of the spreadhsheet to get, update, append etc."
    )
    parser.add_argument(
        '--data',
        help="data of the spreadhsheet to update, append, bold etc."
    )
    parser.add_argument(
        '--major_dimension',
        help="Not required",
        default="ROWS"
    )
    parser.add_argument(
        '--value_input_option',
        help="Not required",
        default="RAW"
    )

    args = parser.parse_args()
    args.data = ast.literal_eval(args.data) if args.data else None
    args.credentials_json_data = json.loads(args.credentials_json_data)

    main(**vars(args))
