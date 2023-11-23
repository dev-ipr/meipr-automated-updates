import logging
from datetime import date, timedelta
import requests
import streamlit as st
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s %(asctime)s %(message)s"
)
logger = logging.getLogger(__name__)

class GetDataFromIPR:
    """Class to request data from the IPR website."""
    def __init__(self, application_type='individual'):
        self.application_type = application_type

    # https://docs.streamlit.io/library/advanced-features/caching
    # @st.cache_data(hash_funcs={
    #     "__main__.GetDataFromIPR" : lambda x: hash(x.application_type)
    #     })
    def load_df(
            self,
            startdate: date,
            enddate: date,
        ) -> pd.DataFrame:
        """
        Method to load data from IPR website.

        ### Arguments
        - `startdate`: Start date in '%Y-%m-%d' format
        - `enddate`: End date in '%Y-%m-%d' format

        ### Return
        A pandas dataframe 
        """
        payload = f'fromDate={startdate}&toDate={enddate}'

        if self.application_type != 'individual':
            ipr_url = st.secrets["endpoint_url"]["URL_OFFTAKER"]
        else:
            ipr_url = st.secrets["endpoint_url"]["URL_INDIVIDUAL"]
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-api-key': st.secrets["api_key"]["IPR_API_KEY"],
        'User-Agent': "Mozilla/5.0 (Windows NT 5.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.1.8865.38 Safari/537.36"
        }

        try:
            response_ipr = requests.request(
                "POST",
                url=ipr_url,
                headers=headers,
                data=payload,
                verify=False, # https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
                timeout=60 # seconds
            )

            logger.info(f"Status code: {response_ipr.status_code}, from {startdate} to {enddate} for {self.application_type}")
            
            assert response_ipr.status_code == 200, f"Cant connect to {ipr_url}"

            # convert to json format
            json_ipr = response_ipr.json()

            # convert to pandas dataframe
            df = pd.DataFrame.from_dict(json_ipr)

            logger.info(f"Size of dataframe: {df.shape}, from {startdate} to {enddate} for {self.application_type}")

            return df
        
        except requests.Timeout as e:
            logger.error(f"Read timeout error: {e}")
            st.error("The IPR database took too long to respond.")
            # raise e
        
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            st.error("An error establishing connection with the IPR site occured.")
            # raise e
            
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            st.error("An error establishing connection with the IPR site occured.")
            # raise e
    
if __name__ == "__main__":
    # Get the current date
    today = date.today()

    # Calculate yesterday's date
    yesterday = today - timedelta(days=1)

    # Format the date as a string in "YYYY-MM-DD" format
    formatted_today = today.strftime("%Y-%m-%d")

    # Format the date as a string in "YYYY-MM-DD" format
    formatted_yesterday = yesterday.strftime("%Y-%m-%d")

    print(f"Yesterday's date: {formatted_yesterday}")
    print(f"Today's date: {formatted_today}")

    # set application_type='individual' for Individual applications
    connection = GetDataFromIPR(application_type='offtaker')
    print(f"Application type: {connection.application_type}")

    df = connection.load_df(
        startdate=formatted_yesterday,
        enddate=formatted_today,
    )

    print(f"Shape of dataframe: {df.shape}")
    print("")
    print(df.info())
    print("")
    df.head(3)
