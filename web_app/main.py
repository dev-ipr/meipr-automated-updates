import logging
from datetime import date, timedelta
import io
from PIL import Image
import streamlit as st
import pandas as pd
from security_utils import check_password
from load_data_utils import GetDataFromIPR

logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s %(asctime)s %(message)s"
)
logger = logging.getLogger(__name__)

# configure the default settings of the page.
econ_min_icon = Image.open('images/logo_kementerian_ekonomi.png')
ipr_icon = Image.open('images/ipr-logo.png')

st.set_page_config(
                layout="wide",
                page_icon = econ_min_icon,
                initial_sidebar_state="expanded",
                page_title="Download the latest applications"
                )

# buffer to use for excel writer
buffer = io.BytesIO()

def get_user_input():
    """
    Function to get user input.
    
    ### Returns
    - `application_type`: Can be either *Individual* or *Offtaker* applications
    - `start_date`: Start date. Defaults to 2 days before today's date.
    - `end_date`: End date. Defaults to today's date.
    """
    today = date.today()
    yesterday = today - timedelta(days=2)

    application_type = st.selectbox(
        "**Specify Application Type**",
         ("Individual", "Offtaker"),
         index=0,
    )
    start_date = st.date_input(
        "**Start Date**",
        yesterday,
        format="YYYY/MM/DD",
    )
    end_date = st.date_input(
        "**End Date**",
        today,
        format="YYYY/MM/DD",
    )

    time_difference = end_date - start_date

    if time_difference.days > 31:
        st.error('Error: Please keep the range of dates to below 31 days.')
    else:
        if start_date < end_date:
            st.success(
                f'Application type: `{application_type}`\n\nStart date: `{start_date}`\n\nEnd date:`{end_date}`'
            )
            return application_type, start_date, end_date, time_difference
        else:
            st.error('Error: End date must fall after start date.')

# check if password has been entered correctly
if check_password():
    logger.info("Login successful")

    st.image(ipr_icon)
    st.markdown("#### Please input the following items")

    try:
        application_type_, start_date_, end_date_, day_diff = get_user_input()

        # set application_type='individual'/'offtaker'
        connection = GetDataFromIPR(application_type=application_type_.lower())

        df = connection.load_df(
            startdate=start_date_,
            enddate=end_date_,
        )

        st.write("-----")

        col1, col2, col3 = st.columns(3)

        with col1:
            # source: https://stackoverflow.com/questions/75323732/how-to-download-streamlit-output-data-frame-as-excel-file
            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df.to_excel(writer, sheet_name='Sheet1', index=False)

                writer.close()

                download2 = st.download_button(
                    label="ℹ️ :green[Download data as Excel]",
                    data=buffer,
                    file_name=f'{application_type_}-{start_date_}-to-{end_date_}.xlsx',
                    mime='application/vnd.ms-excel'
                )

        with col2:
            col2.metric(
                label=":green[No. of Applicants]",
                value=len(df)
            )

        with col3:
            col3.metric(
                label=":green[No. of Days]",
                value=day_diff.days
            )

        # change column names
        df.columns = [x.title().replace("_", " ") for x in df.columns]

        st.dataframe(df)
    
    except TypeError as e:
        logger.error(f"Wrong date inputs in `get_user_input()`: {e}")
        # raise e

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        st.error("An error establishing connection with the IPR site occured.")
        # raise e
